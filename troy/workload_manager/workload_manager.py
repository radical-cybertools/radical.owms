

import threading
import radical.utils   as ru

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
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, translator = 'default', 
                        scheduler  = 'default',
                        dispatcher = 'default') :
        """
        Create a new workload manager instance.  

        Use default plugins if not indicated otherwise
        """

        # make this instance lockable
        self._rlock = threading.RLock ()

        with self._rlock :

            # initialize state, load plugins
            self._workloads  = dict() # registry of active workloads
            self._plugin_mgr = ru.PluginManager ('troy')

            # FIXME: error handling
            self._translator = self._plugin_mgr.load  ('workload_translator', translator)
            self._scheduler  = self._plugin_mgr.load  ('workload_scheduler',  scheduler)
            self._dispatcher = self._plugin_mgr.load  ('workload_dispatcher', dispatcher)


    # --------------------------------------------------------------------------
    #
    def submit_workload (self, workload) :
        """
        register a new workload, but do not perform any activity on it
        """

        if  not isinstance (workload, troy.Workload) :
            raise TypeError ("expected 'Workload' instance, not %s" % type(workload))


        # lock manager before checking/manipulating the registry
        with  self._rlock :

            # lock workload before checking state
            with workload.lock () :

                if  workload.id in self._workloads :
                    raise ValueError ("workload '%s' is already submitted" % workload.id)

                if  workload.state != troy.workload.NEW :
                    raise ValueError ("workload '%s' not in NEW state" % workload.id)

                self._workloads[workload.id] = workload


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

        # lock manager before checking/manipulating the registry
        with  self._rlock :

            workload = self._workloads.get (workload_id, None)

            if  not workload :
                raise LookupError ("no such workload '%s'" % workload_id)


        # we have a workload, and will not manipulate the registry further -- so
        # can release the manager lock.  But we intent to change the workload
        # state, so lock the workload
        with workload.lock () :

            # make sure the workflow is 'fresh', so we can translate it
            if  workload.state != troy.workload.NEW :
                raise ValueError ("workload '%s' not in NEW state" % workload.id)

            # within the locked scope, hand over control over workload to the
            # translator plugin, so it can do what it has to do.
            self._translator.translate (workload, overlay)

            # mark workload as 'translated'
            workload.state = troy.workload.TRANSLATED


    # --------------------------------------------------------------------------
    #
    def schedule_workload (self, workload_id, overlay) :
        """
        schedule the referenced workload, i.e. assign its components to specific
        overlay elements.

        See the documentation of the :class:`Workload` class on how exactly the
        scheduler changes and/or annotates the given workload.
        """

        # lock manager before checking/manipulating the registry
        with  self._rlock :

            workload = self._workloads.get (workload_id, None)

            if  not workload :
                raise LookupError ("no such workload '%s'" % workload_id)


        # we have a workload, and will not manipulate the registry further -- so
        # can release the manager lock.  But we intent to change the workload
        # state, so lock the workload
        with workload.lock () :

            # make sure the workload is translated, so that we can schedule it
            if  workload.state != troy.workload.TRANSLATED :
                raise ValueError ("workload '%s' not in NEW state" % workload.id)

            # within the locked scope, hand over control over workload to the
            # scheduler plugin, so it can do what it has to do.
            self._scheduler.schedule (workload, overlay)

            # mark workload as 'scheduled'
            workload.state = troy.workload.SCHEDULED


    # --------------------------------------------------------------------------
    #
    def dispatch_workload (self, workload_id, overlay) :
        """
        schedule the referenced workload, i.e. submit its CUs and DUs to the
        respective overlay elements.  The workload must have been scheduled
        before diapatching.

        See the documentation of the :class:`Workload` class on how exactly the
        scheduler changes and/or annotates the given workload.
        """

        # lock manager before checking/manipulating the registry
        with  self._rlock :

            workload = self._workloads.get (workload_id, None)

            if  not workload :
                raise LookupError ("no such workload '%s'" % workload_id)


        # we have a workload, and will not manipulate the registry further -- so
        # can release the manager lock.  But we intent to change the workload
        # state, so lock the workload
        with workload.lock () :

            # make sure the workload is scheduled, so we can dispatch it
            if  workload.state != troy.workload.TRANSLATED :
                raise ValueError ("workload '%s' not in NEW state" % workload.id)

            # within the locked scope, hand over control over workload to the
            # dispatcher plugin, so it can do what it has to do.
            self._dispatcher.dispatch (workload, overlay)

            # mark workload as 'scheduled'
            workload.state = troy.workload.DISPATCHED


    # --------------------------------------------------------------------------
    #
    def inspect_workload (self, workload_id) :
        """
        expose a workload to a requesting entity for inspection.
        
        The inspector is expected *not* to change the workload state, nor its
        composition or properties.  If the inspector requires a static workload
        representation, it must lock the workload during inspection.
        """

        # lock manager before checking/manipulating the registry
        with  self._rlock :

            workload = self._workloads.get (workload_id, None)

            if  not workload :
                raise LookupError ("no such workload '%s'" % workload_id)

            return self._workloads[workload_id]



# ------------------------------------------------------------------------------
#
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

