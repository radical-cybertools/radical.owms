

import radical.utils      as ru

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'planner_strategy', 
    'name'        : 'early_binding', 
    'version'     : '0.1',
    'description' : 'this is the basic troy strategy for executing workloads.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (troy.PluginBase):
    """
    The early binding strategy will execute a workload in very basic fasion: use
    planner, overlay_mgr and workload_mgr as configured, etc.  The interesting
    part is that it will schedule the units over the pilots *before* the pilots
    are scheduled over resources.  That scheduling will have less information,
    but can happen early in the game.
    
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
        run the given workload, using the given managers, in early-binding mode.
        """

        workload = None
        overlay  = None

        try :

            # first, we set the 'AUTO' plugins to the troy defaults.  The managers
            # would do that anyways, but we want to explicitly make this part of the
            # stratey.

            troy._logger.info ('apply early binding strategy to workload %s!' % workload_id)
            workload = workload_mgr.get_workload (workload_id)

            # combine or split tasks in te workload
            workload_mgr.expand_workload (workload.id)

            # Initial description of the overlay based on the workload
            overlay_descr = planner.derive_overlay (workload.id)

            # create an overlay based on that description
            overlay = troy.Overlay (overlay_mgr.session, overlay_descr)

            # Translate 1 Overlay description into N Pilot Descriptions
            overlay_mgr.translate_overlay (overlay.id)

            # Decide which resources to use for constructing the overlay
            overlay_mgr.schedule_overlay (overlay.id)

            # Translate /split workload into ComputeUnits etc
            workload_mgr.translate_workload (workload.id, overlay.id)

            ########################################################################
            # 
            # EARLY BINDING:
            # 
            # before provisioning the overlay, we already schedule and dispatch the 
            # *first* workload partition over/to the overlay.  Only then the overlay
            # gets provisioned, and will serve all folloing partitions in
            # late-binding
            #
            ########################################################################
            
            # ----------------------------------------------------------------------
            # schedule the first partition before the overlay is provisioned
            for partition_id in workload.partitions[:1] :

                troy._logger.info  ("dispatch workload partition 0 (%s)" % partition_id)
                partition = troy.WorkloadManager.get_workload (partition_id)

                # throughout this loop, we reflect the workload state as the state
                # of the current partition.  This only works because troy does
                # not enforce a workload state model...
                workload.state = partition.state

                # Schedule the partition onto the overlay
                workload_mgr.bind_workload (partition.id, overlay.id,
                                            bind_mode=troy.EARLY)
                workload.state = partition.state

                # both the overlay and the workload are now scheduled/bound -- we
                # can expect the unit working directories to be createable, at the
                # least, and can thus trigger stage-in for the workload.
                workload_mgr.stage_in_workload (partition_id)


            # ----------------------------------------------------------------------
            # partition 0 is  dispatched, now provision the overlay

            # Instantiate Pilots on specified resources
            overlay_mgr.provision_overlay (overlay.id)


            # ----------------------------------------------------------------------
            # dispatch the first partition to provisioned overlay then wait for
            # partition 0 to finish, before we can dispatch the other partitions
            for partition_id in workload.partitions[:1] :

                # Execute the ComputeUnits on the Pilots
                workload_mgr.dispatch_workload (partition.id, overlay.id)
                workload.state = partition.state

                partition.wait ()
                workload.state = partition.state

                if partition.state == troy.DONE :
                    troy._logger.info  ("partition %s done" % partition.id)
                else :
                    troy._logger.error ("partition %s failed - abort" % partition.id)
                    raise RuntimeError ("partition %s failed - abort" % partition.id)

                # # we did not do any stage-in, but actually *could* do stage-out,
                # as the working dirs and resources are now obviously known.
                # once the workload is done, we stage data out...
                workload_mgr.stage_out_workload (partition_id)


            # ----------------------------------------------------------------------
            # now partition 0 is done, so we can schedule and dispatch the other
            # partitions.  Since the overlay now exists, it is de-facto late-binding
            # from now on.  stage-in and stage-out are here fully supported.
            #
            # this strategy honors workload partitions, and will execute one
            # partition after the other.
            for partition_id in workload.partitions[1:] :

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
                    troy._logger.info  ("partition done")
                else :
                    troy._logger.error ("partition failed - abort")
                    raise RuntimeError ("partition failed - abort")

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

            troy._logger.warn ("shutting down workload: %s" % workload.id)
            workload_mgr.cancel_workload (workload.id)

            troy._logger.warn ("shutting down overlay: %s" % overlay.id)
            overlay_mgr.cancel_overlay (overlay.id)



# ------------------------------------------------------------------------------

