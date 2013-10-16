

import threading
import radical.utils   as ru

import troy
from   troy.constants import *


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
    I guess we should add the option to schedule a single CU, or reschedule
    a complete workload -- but that collides with the state semantics of the
    workload.  Iterative scheduling needs to be implemented anyways though, if
    we want to get any meaningful feedback loop.  Easiest and cleanest is
    probably to allow to repeatedly run through earlier stages again -- DONE
    tasks will then simply be ignored...
    """

    # FIXME: state checks ignore PLANNED state...


    # --------------------------------------------------------------------------
    #
    def __init__ (self, workload_id, 
                        translator = 'default', 
                        scheduler  = 'default',
                        dispatcher = 'default') :
        """
        Create a new workload manager instance.  

        Use default plugins if not indicated otherwise
        """

        # make this instance lockable
        self.lock = threading.RLock ()

        # initialize state, load plugins
        self._workload_id = workload_id
        self._registry    = troy._Registry   ()
        self._plugin_mgr  = ru.PluginManager ('troy')

        # FIXME: error handling
        self._translator  = self._plugin_mgr.load  ('workload_translator', translator)
        self._scheduler   = self._plugin_mgr.load  ('workload_scheduler',  scheduler)
        self._dispatcher  = self._plugin_mgr.load  ('workload_dispatcher', dispatcher)

        # make sure the workload exists
        workload = self._registry.acquire (self._workload_id)
        workload = self._registry.release (self._workload_id)



    # --------------------------------------------------------------------------
    #
    def translate_workload (self, overlay=None) :
        """
        Translate the referenced workload, i.e. transform its tasks into
        ComputeUnit and DataUnit descriptions.

        The translator may or may not have access to an overlay for that action.

        See the documentation of the :class:`Workload` class on how exactly the
        translator changes and/or annotates the given workload.
        """

        workload = self._registry.acquire (self._workload_id)

        try :

            # make sure the workflow is 'fresh', so we can translate it
            if  workload.state != NEW :
                raise ValueError ("workload '%s' not in NEW state" % workload.id)

            # within the locked scope, hand over control over workload to the
            # translator plugin, so it can do what it has to do.
            self._translator.translate (workload, overlay)

            # mark workload as 'translated'
            workload.state = TRANSLATED

        # exceptions fall through, but we make sure to release the workload
        finally :
            self._registry.release (self._workload_id)


    # --------------------------------------------------------------------------
    #
    def schedule_workload (self, overlay_id=None) :
        """
        schedule the referenced workload, i.e. assign its components to specific
        overlay elements.

        See the documentation of the :class:`Workload` class on how exactly the
        scheduler changes and/or annotates the given workload.
        """

        workload = self._registry.acquire (self._workload_id)

        try :

            # check if we have an overlay...
            overlay = None
            try :
                if  overlay_id :
                    overlay = self._registry.acquire (overlay_id)
            except :
                pass

            # make sure the workload is translated, so that we can schedule it
            if  workload.state != TRANSLATED :
                raise ValueError ("workload '%s' not in NEW state" % workload.id)

            # within the locked scope, hand over control over workload (and
            # overlay) to the scheduler plugin, so it can do what it has to do.
            self._scheduler.schedule (workload, overlay)

            # mark workload as 'scheduled'
            workload.state = SCHEDULED

            # release overlay (if we had any...)
            if  overlay:
                self._registry.release (overlay_id)

        # exceptions fall through, but we make sure to release the workload
        finally :
            self._registry.release (self._workload_id)


    # --------------------------------------------------------------------------
    #
    def dispatch_workload (self, overlay_id) :
        """
        schedule the referenced workload, i.e. submit its CUs and DUs to the
        respective overlay elements.  The workload must have been scheduled
        before diapatching.

        See the documentation of the :class:`Workload` class on how exactly the
        scheduler changes and/or annotates the given workload.
        """

        workload = self._registry.acquire (self._workload_id)

        try :
            overlay  = self._registry.acquire (overlay_id)

            try :
            
                # make sure the workload is scheduled, so we can dispatch it.
                # we don't care about overlay state
                if  workload.state != TRANSLATED :
                    raise ValueError ("workload '%s' not in NEW state" % workload.id)

                # within the locked scope, hand over control over workload to the
                # dispatcher plugin, so it can do what it has to do.
                self._dispatcher.dispatch (workload, overlay)

                # mark workload as 'scheduled'
                workload.state = DISPATCHED

            # exceptions fall through, but we make sure to release the overlay
            finally :
                self._registry.release (overlay_id)

        # exceptions fall through, but we make sure to release the workload
        finally :
            self._registry.release (self._workload_id)


    # --------------------------------------------------------------------------
    #
    def inspect_workload (self) :
        """
        expose a workload to a requesting entity for inspection.
        
        The inspector is expected *not* to change the workload state, nor its
        composition or properties.
        """

        return self._registry.acquire (self._workload_id)


# ------------------------------------------------------------------------------
#
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

