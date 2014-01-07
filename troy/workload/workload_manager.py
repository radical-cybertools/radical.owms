
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils      as ru
import troy.utils         as tu
from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
class WorkloadManager (object) :
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
                        stager     = None,
                        session    = None) :
        """
        Create a new workload manager instance.  

        Use default plugins if not indicated otherwise
        """

        if  session :
            self._session = session
        else:
            self._session = troy.Session ()

        if  stager :
            self._stager = stager
        else :
            self._stager = troy.DataStager (self._session)


        # We leave actual plugin initialization for later, in case a strategy
        # wants to alter / complete the plugin selection

        self.plugins = dict ()
        self.plugins['inspector' ] = inspector
        self.plugins['translator'] = translator
        self.plugins['scheduler' ] = scheduler
        self.plugins['dispatcher'] = dispatcher

        self._plugin_mgr = None


    # --------------------------------------------------------------------------
    #
    def _init_plugins (self) :

        if  self._plugin_mgr :
            # we don't allow changes once plugins are loaded and used, for state
            # consistency
            return

        # for each plugin set to 'AUTOMATIC', do the clever thing

        if  self.plugins['inspector' ]  == AUTOMATIC :
            self.plugins['inspector' ]  = 'reflect'
        if  self.plugins['translator']  == AUTOMATIC :
            self.plugins['translator']  = 'direct'
        if  self.plugins['scheduler' ]  == AUTOMATIC :
            self.plugins['scheduler' ]  = 'first'
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

        self._inspector .init_plugin (self._session)
        self._translator.init_plugin (self._session)
        self._scheduler .init_plugin (self._session)
        self._dispatcher.init_plugin (self._session)

        troy._logger.info ("initialized  workload manager (%s)" % self.plugins)

    # --------------------------------------------------------------------------
    #
    @classmethod
    def register_workload (cls, workload) :

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
                import pprint
                pprint.pprint (cls._unit_id_map)
                raise ValueError ("no such unit known '%s'" % unit_id)
            return cls._unit_id_map[unit_id]


    # --------------------------------------------------------------------------
    #
    def create_workload (self, task_descriptions=None) :

        workload = troy.Workload (workload_mgr=self)

        if  task_descriptions :
            if  not isinstance (task_descriptions, list) :
                task_descriptions = [task_descriptions]

            for task_descr in task_descriptions :
                workload.add_task (task_descr)

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


        workload = self.get_workload (workload_id)
        overlay  = troy.OverlayManager.get_overlay (overlay_id)

        # make sure the workflow is 'fresh', so we can translate it
        if  workload.state not in [DESCRIBED, PLANNED] :
            raise ValueError ("workload '%s' not in DESCRIBED nor PLANNED state" % workload.id)

        # make sure manager is initialized
        self._init_plugins ()

        # hand over control over workload to the translator plugin, so it can do
        # what it has to do.
        self._translator.translate (workload, overlay)

        # mark workload as 'translated'
        workload.state = TRANSLATED

        for partition_id in workload.partitions :
            partition = self.get_workload (partition_id)
            partition.state = TRANSLATED


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
            if  overlay.state != TRANSLATED :
                raise ValueError ("overlay '%s' not in TRANSLATED state, cannot " \
                                  "do early binding" % str(overlay.id))

        elif bind_mode == LATE : 
            if  overlay.state != BOUND   and \
                overlay.state != PROVISIONED :
                raise ValueError ( "overlay '%s' neither scheduled nor " % str(overlay.id) \
                                 + "dispateched, cannot do late binding")
                                 
        # make sure manager is initialized
        self._init_plugins ()

        # hand over control over workload (and overlay) to the scheduler plugin,
        # so it can do what it has to do.
        self._scheduler.schedule (workload, overlay)


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

      # # we don't really know if the dispatcher plugin will perform the
      # # stage-in operations in time - so we trigger it manually here.
      # # Eventually, this should get a new task state (same for stage-out)
      # self._stager.stage_in_workload (workload)

        # hand over control over workload to the dispatcher plugin, so it can do
        # what it has to do.
        self._dispatcher.dispatch (workload, overlay)

        # mark workload as 'scheduled'
        workload.state = DISPATCHED

        for partition_id in workload.partitions :
            partition = self.get_workload (partition_id)
            partition.state = DISPATCHED


    # --------------------------------------------------------------------------
    #
    def cancel_workload (self, workload_id) :
        """
        cancel the referenced workload, i.e. all its tasks
        """

        workload = self.get_workload (workload_id)
        workload.cancel ()


# ------------------------------------------------------------------------------

