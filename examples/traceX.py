

import threading
import radical.utils      as ru

import troy


# ------------------------------------------------------------------------------
#
class Troy (object) :
    """
    The `Troy` class exposes the application facing troy API, and mediates the
    interaction between the application and Troy.
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :
        """
        Create a new troy instance.  
        """
        pass


    # --------------------------------------------------------------------------
    #
    def submit_workload (self, workload, session=None) :
        """
        submit a new workload to run.

        The optional session contains a set of security contexts to be used for
        backend interactions.
        """

        if  not isinstance (workload, troy.Workload) :
            raise TypeError ("expected 'Workload' instance, not %s" % type(workload))

        if  session and not isinstance (session, troy.Session) :
            raise TypeError ("expected 'Session' instance, not %s" % type(session))

        workload._session = session

        # this implements one specific trace (early binding)
        def trace_example (workload_id) :
            try :
                
                planner      = troy.Planner         ()
                workload_mgr = troy.WorkloadManager ()
                overlay_mgr  = troy.OverlayManager  ()

                overlay_id   = planner.plan     (workload_id)

                workload_mgr.translate_workload (workload_id, overlay_id)
                workload_mgr.schedule_workload  (workload_id, overlay_id,
                                                      binding=troy.EARLY)

                overlay_mgr.schedule_overlay    (overlay_id)
                overlay_mgr.dispatch_overlay    (overlay_id)

                workload_mgr.dispatch_workload  (workload_id, overlay_id)

            except Exception as e :
                workload.state = troy.FAILED
                workload.error = e


        # run that trace in a separate thread
        threading.Thread (trace_example, workload.id).start ()

        # we return the workload ID as identifier of this trace -- even though
        # the app already has that ID within the submitted workload.
        return workload.id


# ------------------------------------------------------------------------------

