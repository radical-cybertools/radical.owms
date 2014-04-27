

import radical.utils      as ru

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'planner_strategy', 
    'name'        : 'late_binding', 
    'version'     : '0.1',
    'description' : 'this is the basic troy strategy for executing workloads.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (troy.PluginBase):
    """
    The late binding strategy will execute a workload in very basic fasion: use
    planner, overlay_mgr and workload_mgr as configured, etc.  The interesting
    part is that it will schedule the units over the pilots *after* the pilots
    are scheduled over resources.  That scheduling will have more information
    then, but happens rather late in the game.
    
    **Configuration Options:** None
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
        run the given workload, using the given managers, in late-binding mode.
        """

        workload = None
        overlay  = None

        try :

            troy._logger.info ('troy default strategy : strategize workload %s!' % workload_id)
            workload = workload_mgr.get_workload (workload_id)

            # combine or split tasks in te workload
            workload_mgr.expand_workload (workload.id)

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

            troy._logger.warn ("shutting down workload: %s" % workload.id)
            workload_mgr.cancel_workload (workload.id)

            troy._logger.warn ("shutting down overlay: %s" % overlay.id)
            overlay_mgr.cancel_overlay (overlay.id)

            session = planner.session
            if  session.cfg.get ('troy_timing') == 'store' :
                tgt = session.cfg.get ('troy_timing_db')

                if  not tgt :
                    troy._logger.critical ("cannot store timings, no troy_timing_db")
                else :
                    session.timed_store (tgt)


        except Exception as e :

            troy._logger.critical ("strategy execution failed: %s" % e)
            import traceback
            traceback.print_exc()

            troy._logger.warn ("shutting down workload: %s" % workload.id)
            workload_mgr.cancel_workload (workload.id)

            troy._logger.warn ("shutting down overlay: %s" % overlay.id)
            overlay_mgr.cancel_overlay (overlay.id)


# ------------------------------------------------------------------------------

