
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils      as ru
import troy.utils         as tu
from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
class WorkloadManager (tu.Timed) :
    """
    The `WorkloadManager` class, as its name suggests, manages :class:`Workload`
    instances, i.e. translates, schedules and enacts those instances.

    FIXME: how are race conditions handled -- like, a workload is scheduled on
    an overlay, but before dispatching, a pilot in that overlay disappears?
    I guess we should add the option to schedule a single unit, or reschedule
    a complete workload -- but that collides with the state semantics of the
    workload.  Iterative scheduling needs to be implemented anyways though, if
    we want to get any meaningful feedback loop.  Easiest and cleanest is
    probably to allow to repeatedly run through earlier stages again -- DONE
    tasks will then simply be ignored...

    Notes

    . I agree that iterative scheduling has to be implemented. The state model
      of the workload could be extended by adding a RESCHEDULING state. In a
      synchronos model:
      - the manager should 'monitor' the state of its pilots
      - react to a well-defined set of states by transitioning the workload
        into a RESCHEDULING state
      - chose another resource if available or create a new (pilots of an)
        overlay
      - call the scheduler to get a scheduling map of the remaining task (I
        agree, the tasks in state done should be disregarded)
      - enact the scheduling map on the new (pilots of an) overlay.

    """

    # FIXME: state checks ignore PLANNED state...

    # this map is used to translate between troy unit IDs and native backend
    # IDs.
    _unit_id_map = dict ()

    # --------------------------------------------------------------------------
    #
    def __init__ (self, session,
                        translator  = AUTOMATIC,
                        scheduler   = AUTOMATIC,
                        dispatcher  = AUTOMATIC) :
        """
        Create a new workload manager instance.

        Use default plugins if not indicated otherwise
        """

        self.session = session
        self.id      = ru.generate_id ('wlm.')

        tu.Timed.__init__             (self, 'troy.WorkloadManager', self.id)
        self.session.timed_component  (self, 'troy.WorkloadManager', self.id)

        self._stager     = None
        self._plugin_mgr = None
        self.plugins     = dict ()

        # setup plugins from aruments
        #
        # We leave actual plugin initialization for later, in case a strategy
        # wants to alter / complete the plugin selection
        #
        # FIXME: we don't need no stupid arguments, ey!  Just use
        #        AUTOMATIC by default...
        self.plugins['translator'] = translator
        self.plugins['scheduler' ] = scheduler
        self.plugins['dispatcher'] = dispatcher


        # lets see if there are any plugin preferences in the config
        # note that config settings supercede arguments!
        cfg = session.get_config ('workload_manager')

        if  'plugin_workload_translator' in cfg : 
            self.plugins['translator']   =  cfg['plugin_workload_translator']
        if  'plugin_workload_scheduler'  in cfg : 
            self.plugins['scheduler' ]   =  cfg['plugin_workload_scheduler' ]
        if  'plugin_workload_dispatcher' in cfg : 
            self.plugins['dispatcher']   =  cfg['plugin_workload_dispatcher']

      # import pprint
      # pprint.pprint (session.cfg)
      # pprint.pprint (cfg)
      # pprint.pprint(self.plugins)
      # sys.exit(0)





    # --------------------------------------------------------------------------
    #
    def _init_plugins (self) :

        if  self._plugin_mgr :
            # we don't allow changes once plugins are loaded and used, for state
            # consistency
            # NOTES: Does this mean that we cannot unload/load plugin within
            #        the same workload manager? If so, why do we need a plugin
            #        manager at all?
            return

        # for each plugin set to 'AUTOMATIC', do the clever thing
        # TODO: We should probably move all this to a configuration file. I
        #       changed scheduler to round_robin because first kind of drug
        #       every run with multiple pilots. This is bad(tm).

        if  self.plugins['translator']  == AUTOMATIC :
            self.plugins['translator']  = 'direct'
        if  self.plugins['scheduler' ]  == AUTOMATIC :
            self.plugins['scheduler' ]  = 'round_robin'
        if  self.plugins['dispatcher']  == AUTOMATIC :
            self.plugins['dispatcher']  = 'local'

        # troy._logger.debug ("initializing workload manager (%s)" % self.plugins)

        # load plugins
        self._plugin_mgr = ru.PluginManager ('troy')

        # FIXME: error handling
        self._translator = self._plugin_mgr.load  ('workload_translator', self.plugins['translator'])
        self._scheduler  = self._plugin_mgr.load  ('workload_scheduler',  self.plugins['scheduler' ])
        self._dispatcher = self._plugin_mgr.load  ('workload_dispatcher', self.plugins['dispatcher'])

        if  not self._translator : raise RuntimeError ("Could not load translator plugin")
        if  not self._scheduler  : raise RuntimeError ("Could not load scheduler  plugin")
        if  not self._dispatcher : raise RuntimeError ("Could not load dispatcher plugin")

        self._translator.init_plugin (self.session, 'workload_manager')
        self._scheduler .init_plugin (self.session, 'workload_manager')
        self._dispatcher.init_plugin (self.session, 'workload_manager')

        # parser plugins are somewhat different, as we load all parsers we can
        # find.  On any incoming workload, we'll try one after the other
        self._parsers = list()
        for parser_plugin_name in self._plugin_mgr.list ('workload_parser') :
            parser = self._plugin_mgr.load ('workload_parser', parser_plugin_name)
            if parser :
                parser.init_plugin (self.session, 'workload_manager')
                self._parsers.append (parser)

        troy._logger.info ("initialized  workload manager (%s)" % self.plugins)

    # --------------------------------------------------------------------------
    #
    @classmethod
    def register_workload (cls, workload) :
        """
        Notes

        . What exactly does classmethod do. I saw the documentation in
          signatures.py but I did not manage to understand it.

        . What cls stands for? It is puzzling as when registering a
          workload in the examples we pass a single parameter. I suspect it
          has to do with classmethod and type registration. What exactly buy
          us a part oscurity and a very gray area in the phylosophy of
          language design?

        """

        if  isinstance (workload, list) :
            workloads =  workload
        else :
            workloads = [workload]

        for workload in workloads :

            if  not isinstance (workload, troy.Workload) :
                raise TypeError ('expected troy.Workload instance, not %s' % type(workload))

            ru.Registry.register (workload)


    # --------------------------------------------------------------------------
    #
    @classmethod
    def unregister_workload (cls, workload_id) :
        ru.Registry.unregister (workload_id)


    # --------------------------------------------------------------------------
    #
    @classmethod
    def get_workload (cls, workload_id, _manager=None) :
        """
        We don't care about locking at this point -- so we simply release the
        workload immediately...

        Questions

        . I remember we discussed this previously but I forgot about why we
          we decided to pass IDs instead of objects. Having a syntactic check
          on workload seems ugly and somewhat fragile. I would think a type
          checking would be more robust.

        . Why do we need to lock the acquising in readonly mode of a
          workload_id? I dag out the code for Registry.acquire and I see that
          'The registry will thus ensure that a consumer will always see
          instances which are not changed by a third party over the scope of
          a lease'. The access to the workload description submitted by the
          application layer is confined by desing to the planner. Why should
          we care about concurrent (especially readonly) access and possible
          modification to the workload?

        """
        if  not workload_id :
            return None

        if  not workload_id.startswith ('wl.') :
            raise ValueError ("'%s' does not represent a workload" % workload_id)

        workload = ru.Registry.acquire (workload_id, ru.READONLY)
        ru.Registry.release (workload_id)

        if  _manager :
            _manager.timed_component (workload, 'troy.Workload', workload_id)

        return workload


    # --------------------------------------------------------------------------
    #
    @classmethod
    def native_id_to_unit_id (cls, native_id) :

        for troy_id in cls._unit_id_map :
            if  native_id == cls._unit_id_map[troy_id] :
                return troy_id

        return None


    # --------------------------------------------------------------------------
    #
    @classmethod
    def unit_id_to_native_id (cls, unit_id, native_id=None) :

        # FIXME: this is not threadsafe.
        # FIXME: load from disk on first call

        if  native_id :

            # register id
            if  unit_id in cls._unit_id_map :
                raise ValueError ("Cannot register that unit id -- already known")
            cls._unit_id_map[unit_id] = native_id
            # FIXME: dump to disk

        else :

            # lookup id
            if  not unit_id in cls._unit_id_map :
                raise ValueError ("no such unit known '%s'" % unit_id)
            return cls._unit_id_map[unit_id]


    # --------------------------------------------------------------------------
    #
    def parse_workload (self, workload_description) :
        """
        Parse a json workload description, convert into a set of
        task_descriptions and relation_descriptions
        """

        # make sure manager is initialized
        self._init_plugins ()

        # see if the workload_description points to a file.  If so, read the
        # content and use that as the actual description string
        try :
            with open (workload_description, "r") as descr_file:
                workload_description = descr_file.read ()
        except Exception as e :
            # leave any error handling to the parsers -- what do we know..
            troy._logger.warn ("cannot read WL description at '%s'" \
                            % workload_description)


        # try one parser after the other, until one can handle the workload
        # description
        task_descriptions     = None  # list of task descriptions
        relation_descriptions = None  # list of reation descriptions

        for parser in self._parsers :
            troy._logger.debug ("trying parser %s" % parser.name)

            if True :
          # try :
                task_descriptions, relation_descriptions = parser.parse (workload_description)
          # except Exception as e :
          #     troy._logger.warn ("parser %s failed: %s" % (parser.name, e))
          # else :
          #     # success!
          #     break

        if  not task_descriptions  and \
            not relation_descriptions :
            raise ValueError ("Could not parse workload description\n----\n%s\n----\n" \
                            % workload_description)

        workload = troy.Workload (self.session, 
                                  task_descriptions,
                                  relation_descriptions)

        return workload.id


    # --------------------------------------------------------------------------
    #
    def create_workload (self, task_descriptions=None,
                         relation_descriptions=None) :
        """
        Notes

        . This methods breaks the design choice of having the planner as the
          entry point to TROY - i.e. the interface with the application layer.
          Following that design choice would require to move this method to
          the planner. You can see the consequences of breaking the design in
          the current demo: They create the workload by first instatiating
          a workload manager. This should not be the case. They should
          instantiate a planner.

        - AM: Hmm, we do that via the WL manager to keep ownership of the
          workload with that WL manager -- otherwise the planner would initially
          own the workload, and would hand off ownership to the WL manager
          later.  Is this acceptable then?
        """

        workload = troy.Workload (task_descriptions, relation_descriptions)

        return workload.id


    # --------------------------------------------------------------------------
    #
    def translate_workload (self, workload_id, overlay_id=None) :
        # FIXME: is empty overlay valid?
        """
        Translate the referenced workload, i.e. transform its tasks into
        ComputeUnit and DataUnit descriptions.

        The translator may or may not have access to an overlay for that action.

        See the documentation of the :class:`Workload` class on how exactly the
        translator changes and/or annotates the given workload.
        """


        workload = troy.WorkloadManager.get_workload (workload_id, _manager=self)
        overlay  = troy.OverlayManager .get_overlay  (overlay_id,  _manager=self)

        # make sure the workflow is 'fresh', so we can translate it
        if  workload.state not in [DESCRIBED, PLANNED] :
            raise ValueError ("workload '%s' not in DESCRIBED nor PLANNED state" % workload.id)

        # make sure manager is initialized
        self._init_plugins ()

        # hand over control over workload to the translator plugin, so it can do
        # what it has to do.
        workload.timed_method ('translate', [], 
                               self._translator.translate, [workload, overlay])


        # mark workload as 'translated'
        workload._set_state (TRANSLATED)

        for partition_id in workload.partitions :
            partition = self.get_workload (partition_id)
            partition._set_state (TRANSLATED)


    # --------------------------------------------------------------------------
    #
    def bind_workload (self, workload_id, overlay_id, bind_mode=None) :
        """
        bind (schedule) the referenced workload, i.e. assign its components to
        specific overlay elements.

        See the documentation of the :class:`Workload` class on how exactly the
        binding step changes and/or annotates the given workload.

        The `bind_workload` method optionally accepts an additional
        `bind_mode` parameter, which can be set to `troy.EARLY` or `troy.LATE`.
        If this parameter is set, it will trigger a test which ensures that the
        given Overlay is in the respective state, i.e. is not yet scheduled or
        dispatched in the case of early binding and is scheduled or dispatched
        in the case of late binding.  Partially dispatched overlays will not be
        usable in either case -- for those, the binding parameter must be left
        unspecified (i.e. `None`).
        """

        workload = self.get_workload (workload_id)
        overlay  = troy.OverlayManager.get_overlay (overlay_id)

        if  not overlay :
            raise ValueError ("binding needs a valid overlay")

        # make sure the workload is translated, so that we can bind it
        if  workload.state != TRANSLATED :
            raise ValueError ("workload '%s' not in TRANSLATED state" % workload.id)

        # make sure we can honor the requested scheduling mode
        if  bind_mode == EARLY :
            if  overlay.state not in [TRANSLATED, SCHEDULED] :
                raise ValueError ("overlay '%s' not in TRANSLATED or SCHEDULED " \
                                  "state, cannot do early binding" % str(overlay.id))

        elif bind_mode == LATE :
            if  overlay.state not in [SCHEDULED, PROVISIONED] :
                raise ValueError ( "overlay '%s' not in SCHEDULED or PROVISIONED "  \
                                   "state, cannot do late binding" % str(overlay.id))

        # make sure manager is initialized
        self._init_plugins ()

        # hand over control over workload (and overlay) to the scheduler plugin,
        # so it can do what it has to do.
        workload.timed_method ('schedule', [overlay.id], 
                               self._scheduler.schedule, [workload, overlay])

    # --------------------------------------------------------------------------
    #
    def dispatch_workload (self, workload_id, overlay_id) :
        """
        schedule the referenced workload, i.e. submit its Units to the
        respective overlay elements.  The workload must have been scheduled
        before diapatching.

        See the documentation of the :class:`Workload` class on how exactly the
        scheduler changes and/or annotates the given workload.
        """

        workload = self.get_workload (workload_id)
        overlay  = troy.OverlayManager.get_overlay (overlay_id)

        # make sure the workload is scheduled, so we can dispatch it.
        # we don't care about overlay state
        if  workload.state != BOUND :
            raise ValueError ("workload '%s' not in BOUND state" % workload.id)

        # make sure manager is initialized
        self._init_plugins ()

        # now that the units are bound and about to be dispatched, we can fix the
        # resource placeholders in the unit descriptions
        for (task_id, task) in workload.tasks.iteritems() :
            for (unit_id, unit) in task.units.iteritems() :

                # get troys idea of resource configuration
                pilot_id     = unit.pilot_id
                pilot        = troy.Pilot (self.session, pilot_id)
                resource_cfg = self.session.get_resource_config (pilot.resource)

                # and merge it conservatively into the unit config
                unit.merge_description (resource_cfg)


      # # we don't really know if the dispatcher plugin will perform the
      # # stage-in operations in time - so we trigger it manually here.
      # # Eventually, this should get a new task state (same for stage-out)
      # self.stage_in_workload (workload)

        # hand over control over workload to the dispatcher plugin, so it can do
        # what it has to do.
        workload.timed_method ('dispatch', [overlay.id], 
                               self._dispatcher.dispatch, [workload, overlay])

        # mark workload as 'scheduled'
        workload._set_state (DISPATCHED)

        for partition_id in workload.partitions :
            partition = self.get_workload (partition_id)
            partition._set_state (DISPATCHED)


    # --------------------------------------------------------------------------
    #
    def cancel_workload (self, workload_id) :
        """
        cancel the referenced workload, i.e. all its tasks
        """

        workload = self.get_workload (workload_id)
        workload.timed_method ('cancel', [], workload.cancel)


    # --------------------------------------------------------------------------
    #
    def stage_in_workload (self, workload_id) :
        """
        trigger stage-in for all workload tasks
        """

        if  not self._stager :
            self._stager = troy.DataStager (self.session)

        workload = self.get_workload (workload_id)
        workload.timed_method ('stage_in_workload', [], 
                               self._stager.stage_in_workload, [workload])


    # --------------------------------------------------------------------------
    #
    def stage_out_workload (self, workload_id) :
        """
        trigger stage-out for all workload tasks
        """

        if  not self._stager :
            self._stager = troy.DataStager (self.session)

        workload = self.get_workload (workload_id)
        workload.timed_method ('stage_out_workload', [], 
                               self._stager.stage_out_workload, [workload])


# ------------------------------------------------------------------------------

