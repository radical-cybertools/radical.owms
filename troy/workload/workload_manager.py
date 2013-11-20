

import threading
import radical.utils      as ru

from   troy.constants import *

import troy.overlay.overlay_manager as olm


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


    # --------------------------------------------------------------------------
    #
    def __init__ (self, inspector  = 'default', 
                        translator = 'default',
                        scheduler  = 'round_robin',
                        dispatcher = 'bigjob') :
        """
        Create a new workload manager instance.  

        Use default plugins if not indicated otherwise
        """

        # initialize state, load plugins
        self._plugin_mgr  = ru.PluginManager ('troy')

        # FIXME: error handling
        self._inspector   = self._plugin_mgr.load  ('workload_inspector',  inspector)
        self._translator  = self._plugin_mgr.load  ('workload_translator', translator)
        self._scheduler   = self._plugin_mgr.load  ('workload_scheduler',  scheduler)
        self._dispatcher  = self._plugin_mgr.load  ('workload_dispatcher', dispatcher)


    # --------------------------------------------------------------------------
    #
    @classmethod
    def register_workload (cls, workload) :
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
    def translate_workload (self, workload_id, overlay=None) :
        """
        Translate the referenced workload, i.e. transform its tasks into
        ComputeUnit and DataUnit descriptions.

        The translator may or may not have access to an overlay for that action.

        See the documentation of the :class:`Workload` class on how exactly the
        translator changes and/or annotates the given workload.
        """

        workload = self.get_workload (workload_id)

        # make sure the workflow is 'fresh', so we can translate it
        if  workload.state not in [DESCRIBED, PLANNED] :
            raise ValueError ("workload '%s' not in DESCRIBED nor PLANNED state" % workload.id)

        # hand over control over workload to the translator plugin, so it can do
        # what it has to do.
        self._translator.translate (workload, overlay)

        # mark workload as 'translated'
        workload.state = TRANSLATED


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
        overlay  = olm.OverlayManager.get_overlay (overlay_id)

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
            if  overlay.state != BOUND      and \
                overlay.state != DISPATCHED :
                raise ValueError ( "overlay '%s' neither scheduled nor " \
                                 + "dispateched, cannot do late binding" \
                                 % overlay.id)

        # hand over control over workload (and overlay) to the scheduler plugin,
        # so it can do what it has to do.
        self._scheduler.schedule (workload, overlay)

        # mark workload as 'scheduled'
        workload.state = BOUND


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
        overlay  = olm.OverlayManager.get_overlay (overlay_id)

        # make sure the workload is scheduled, so we can dispatch it.
        # we don't care about overlay state
        if  workload.state != BOUND :
            raise ValueError ("workload '%s' not in BOUND state" % workload.id)

        # hand over control over workload to the dispatcher plugin, so it can do
        # what it has to do.
        self._dispatcher.dispatch (workload, overlay)

        # mark workload as 'scheduled'
        workload.state = DISPATCHED


    # --------------------------------------------------------------------------
    #
    def cancel_workload (self, workload_id) :
        """
        cancel the referenced workload, i.e. all its tasks
        """

        workload = self.get_workload (workload_id)
        workload.cancel ()


# ------------------------------------------------------------------------------

