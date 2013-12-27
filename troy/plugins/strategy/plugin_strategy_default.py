

import radical.utils as ru

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'strategy', 
    'name'        : 'default', 
    'version'     : '0.1',
    'description' : 'this is the basic troy strategy for executing workloads.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (troy.PluginBase):
    """
    This class implements the simple default Troy execution strategy.
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def execute (self, workload_id, planner, overlay_mgr, workload_mgr) :
        """
        This simple implementation does the expected thing: executes one
        subworkload after the other, on the given overlay.  Other
        implementations may want to alter the overlay, or may run subworkloads
        concurrently, etc.
        """

        troy._logger.info ('troy default strategy : strategize workload %s!' % workload_id)
        workload = workload_mgr.get_workload (workload_id)


        # combine or split tasks in te workload
        planner.expand_workload (workload.id)

        # Initial description of the overlay based on the workload
        overlay_id = planner.derive_overlay (workload.id)

        # Translate 1 Overlay description into N Pilot Descriptions
        overlay_mgr.translate_overlay (overlay_id)

        # Decide which resources to use for constructing the overlay
        overlay_mgr.schedule_overlay (overlay_id)

        # Instantiate Pilots on specified resources
        overlay_mgr.provision_overlay (overlay_id)

        # Translate /split workload into ComputeUnits etc
        sub_workload_ids = workload_mgr.translate_workload (workload.id, overlay_id)


        for sub_workload_id in sub_workload_ids :

            troy._logger.info  ("running sub-workload %s" % sub_workload_id)
            sub_workload   = troy.WorkloadManager.get_workload (sub_workload_id)

            # throughout this loop, we reflect the workload state as the state
            # of the current sub_workload.  This only works because troy does
            # not enforce a workload state model...
            workload.state = sub_workload.state

            # Schedule the sub_workload onto the overlay
            workload_mgr.bind_workload (sub_workload.id, overlay_id,
                                        bind_mode=troy.LATE)
            workload.state = sub_workload.state

            # Execute the ComputeUnits on the Pilots
            workload_mgr.dispatch_workload (sub_workload.id, overlay_id)
            workload.state = sub_workload.state

            # Of course nothing will fail due to TROY's magic robustness and
            # and we therefore just wait until its done!
            sub_workload.wait ()
            workload.state = sub_workload.state

            if sub_workload.state == troy.DONE :
                troy._logger.info  ("sub-workload done")
            else :
                troy._logger.error ("sub-workload failed - abort")
                raise RuntimeError ("sub-workload failed - abort")


        troy._logger.info ("all sub-workloads done")


        overlay_mgr .cancel_overlay  (overlay_id)


# ------------------------------------------------------------------------------

