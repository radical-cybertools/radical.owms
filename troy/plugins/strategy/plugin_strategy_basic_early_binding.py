

import radical.utils      as ru

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'strategy', 
    'name'        : 'basic_early_binding', 
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
        # stratey.

        troy._logger.info ('troy default strategy : strategize workload %s!' % workload_id)
        workload = workload_mgr.get_workload (workload_id)

        # combine or split tasks in te workload
        planner.expand_workload (workload.id)

        # Initial description of the overlay based on the workload
        overlay_descr = planner.derive_overlay (workload.id)

        # create an overlay based on that description
        overlay_id = overlay_mgr.create_overlay (overlay_descr)

        # Translate 1 Overlay description into N Pilot Descriptions
        overlay_mgr.translate_overlay (overlay_id)

        # Translate /split workload into ComputeUnits etc
        workload_mgr.translate_workload (workload.id, overlay_id)

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
        # submit the first partition before the overlay is provisioned
        for partition_id in workload.partitions[:1] :

            troy._logger.info  ("dispatch workload partition 0 (%s)" % partition_id)

            # throughout this loop, we reflect the workload state as the state
            # of the current partition.  This only works because troy does
            # not enforce a workload state model...
            workload.state = partition.state

            # Schedule the partition onto the overlay
            workload_mgr.bind_workload (partition.id, overlay_id,
                                        bind_mode=troy.LATE)
            workload.state = partition.state

          # --------------------------------------------------------------------
          # FIXME: we cannot stage in at this point, as we do not know the
          # target directories: the pilots are not scheduled and thus not
          # assigned to a resource, and thus the tasks are not bound to
          # a resource -- so where to stage to?

          # both the overlay and the workload are now scheduled/bound -- we
          # can expect the unit working directories to be createable, at the
          # least, and can thus trigger stage-in for the workload.
          # workload_mgr._stager.stage_in_workload (partition)

            # Execute the ComputeUnits on the Pilots
            workload_mgr.dispatch_workload (partition.id, overlay_id)
            workload.state = partition.state

        # ----------------------------------------------------------------------
        # partition 0 is  dispatched, now provision the overlay

        # Decide which resources to use for constructing the overlay
        overlay_mgr.schedule_overlay (overlay_id)

        # Instantiate Pilots on specified resources
        overlay_mgr.provision_overlay (overlay_id)


        # ----------------------------------------------------------------------
        # overlay is dispatched, now wait for partition 0 to finish, before we
        # can dispatch the other partitions
        for partition_id in workload.partitions[:1] :

            partition.wait ()
            workload.state = partition.state

            if partition.state == troy.DONE :
                troy._logger.info  ("partition done")
            else :
                troy._logger.error ("partition failed - abort")
                raise RuntimeError ("partition failed - abort")

            # # we did not do any stage-in, but actually *could* do stage-out,
            # as the working dirs and resources are now obviously known.
            # once the workload is done, we stage data out...
            workload_mgr._stager.stage_out_workload (partition)


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
            workload_mgr.bind_workload (partition.id, overlay_id,
                                        bind_mode=troy.LATE)
            workload.state = partition.state

            # both the overlay and the workload are now scheduled/bound -- we
            # can expect the unit working directories to be createable, at the
            # least, and can thus trigger stage-in for the workload.
            workload_mgr._stager.stage_in_workload (partition)

            # Execute the ComputeUnits on the Pilots
            workload_mgr.dispatch_workload (partition.id, overlay_id)
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
            workload_mgr._stager.stage_out_workload (partition)


        troy._logger.info ("all partition done (%s)" % workload.state)

        overlay_mgr.cancel_overlay (overlay_id)


# ------------------------------------------------------------------------------

