

import radical.utils      as ru

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'strategy', 
    'name'        : 'basic_late_binding', 
    'version'     : '0.1',
    'description' : 'this is the basic troy strategy for executing workloads.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (troy.PluginBase):

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

        # first, we set the 'AUTO' plugins to the troy defaults.  The managers
        # would do that anyways, but we want to explicitly make this part of the
        # strategy.

        troy._logger.info ('troy default strategy : strategize workload %s!' % workload_id)
        workload = workload_mgr.get_workload (workload_id)

        # combine or split tasks in te workload
        planner.expand_workload (workload.id)

        # Initial description of the overlay based on the workload
        overlay_descr = planner.derive_overlay (workload.id)

        # create an overlay based on that description
        overlay = troy.Overlay (overlay_mgr.session, overlay_descr)

        # Translate 1 Overlay description into N Pilot Descriptions
        overlay_mgr.translate_overlay (overlay.id)


        # ######################################################################
        #
        # LATE BINDING:
        #
        # we first provision the overlay, and then dispatch one partition after
        # the other.   Right after overlay scheduling and dispatching, we should
        # know the target pilot resources and task working dirs, so data staging
        # is supported for all workload partitions.
        #
        # ######################################################################


        # ----------------------------------------------------------------------
        # provision the overlay

        # Decide which resources to use for constructing the overlay
        overlay_mgr.schedule_overlay (overlay.id)

        # Instantiate Pilots on specified resources
        overlay_mgr.provision_overlay (overlay.id)

        # ----------------------------------------------------------------------
        # expand, schedule and dispatch the workload partitions

        # Translate /split workload into ComputeUnits etc
        workload_mgr.translate_workload (workload.id, overlay.id)

        # this strategy honors workload partitions, and will execute one
        # partition after the other.
        for partition_id in workload.partitions :

            troy._logger.info  ("running workload partition %s" % partition_id)
            partition = troy.WorkloadManager.get_workload (partition_id)

            # throughout this loop, we reflect the workload state as the state
            # of the current partition.  This only works because troy does
            # not enforce a workload state model...
            workload.state = partition.state

            # Schedule the partition onto the overlay
            workload_mgr.bind_workload (partition.id, overlay.id,
                                        bind_mode=troy.LATE)
            workload.state = partition.state

            # both the overlay and the workload are now scheduled/bound -- we
            # can expect the unit working directories to be createable, at the
            # least, and can thus trigger stage-in for the workload.
            workload_mgr.stage_in_workload (partition_id)

            # Execute the ComputeUnits on the Pilots
            workload_mgr.dispatch_workload (partition.id, overlay.id)
            workload.state = partition.state

            # Of course nothing will fail due to TROY's magic robustness and
            # and we therefore just wait until its done!
            partition.wait ()
            workload.state = partition.state

            if partition.state == troy.DONE :
                troy._logger.info  ("partition %s done" % partition.id)
            else :
                troy._logger.error ("partition %s failed - abort" % partition.id)
                raise RuntimeError ("partition %s failed - abort" % partition.id)

            # once the workload is done, we stage data out...
            workload_mgr.stage_out_workload (partition_id)


        troy._logger.info ("all partition done (%s)" % workload.state)

        overlay_mgr.cancel_overlay (overlay.id)


# ------------------------------------------------------------------------------

