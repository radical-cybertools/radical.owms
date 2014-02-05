
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

    The internal state of the workload manager is not open for inspection -- but
    the workloads it manages can be exposed for inspection, on request
    (:func:`inspect_workload()`).

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

    . The workload should be open to inspection only to the components of TROY,
      to to the application layer.

    """

    # FIXME: state checks ignore PLANNED state...

    # this map is used to translate between troy unit IDs and native backend
    # IDs.
    _unit_id_map = dict ()

    # --------------------------------------------------------------------------
    #
    def __init__ (self, inspector  = AUTOMATIC,
                        translator = AUTOMATIC,
                        scheduler  = AUTOMATIC,
                        dispatcher = AUTOMATIC,
                        session    = None) :
        """
        Create a new workload manager instance.

        Use default plugins if not indicated otherwise
        """

        if  session : self.session = session
        else        : self.session = troy.Session ()

        self._stager = None


        # We leave actual plugin initialization for later, in case a strategy
        # wants to alter / complete the plugin selection

        self.plugins = dict ()
        self.plugins['inspector' ] = inspector
        self.plugins['translator'] = translator
        self.plugins['scheduler' ] = scheduler
        self.plugins['dispatcher'] = dispatcher

        self._plugin_mgr = None

        self.id = ru.generate_id ('wlm.')

        tu.Timed.__init__       (self, self.id)
        self.session.timed_component ('workload_manager', self.id)


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

        if  self.plugins['inspector' ]  == AUTOMATIC :
            self.plugins['inspector' ]  = 'reflect'
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
        self._inspector  = self._plugin_mgr.load  ('workload_inspector',  self.plugins['inspector' ])
        self._translator = self._plugin_mgr.load  ('workload_translator', self.plugins['translator'])
        self._scheduler  = self._plugin_mgr.load  ('workload_scheduler',  self.plugins['scheduler' ])
        self._dispatcher = self._plugin_mgr.load  ('workload_dispatcher', self.plugins['dispatcher'])

        if  not self._inspector  : raise RuntimeError ("Could not load inspector  plugin")
        if  not self._translator : raise RuntimeError ("Could not load translator plugin")
        if  not self._scheduler  : raise RuntimeError ("Could not load scheduler  plugin")
        if  not self._dispatcher : raise RuntimeError ("Could not load dispatcher plugin")

        self._inspector .init_plugin (self.session)
        self._translator.init_plugin (self.session)
        self._scheduler .init_plugin (self.session)
        self._dispatcher.init_plugin (self.session)

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
    def get_workload (cls, workload_id) :
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

        wl = ru.Registry.acquire (workload_id, ru.READONLY)
        ru.Registry.release (workload_id)

        return wl


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
              # import pprint
              # pprint.pprint (cls._unit_id_map)
                raise ValueError ("no such unit known '%s'" % unit_id)
            return cls._unit_id_map[unit_id]


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


        workload = self.get_workload (workload_id)
        overlay  = troy.OverlayManager.get_overlay (overlay_id)

        self.timed_component ('workload', workload.id)

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

        self.timed_component ('workload', workload.id)

        if  not overlay :
            raise ValueError ("binding needs a valid overlay")

        # make sure the workload is translated, so that we can bind it
        if  workload.state != TRANSLATED :
            raise ValueError ("workload '%s' not in TRANSLATED state" % workload.id)

        # make sure we can honor the requested scheduling mode
        if  bind_mode == EARLY :
            if  overlay.state not in [TRANSLATED, SCHEDULED] :
                raise ValueError ("overlay '%s' not in TRANSLATED or SCHEDULED state, cannot " \
                                  "do early binding" % str(overlay.id))

        elif bind_mode == LATE :
            if  overlay.state != PROVISIONED :
                raise ValueError ( "overlay '%s' neither scheduled nor " % str(overlay.id) \
                                 + "dispatched, cannot do late binding")

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

        self.timed_component ('workload', workload.id)

        # make sure the workload is scheduled, so we can dispatch it.
        # we don't care about overlay state
        if  workload.state != BOUND :
            raise ValueError ("workload '%s' not in BOUND state" % workload.id)

        # make sure manager is initialized
        self._init_plugins ()

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
        self.timed_component  ('workload', workload.id)
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

