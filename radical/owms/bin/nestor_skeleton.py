#!/usr/bin/env python

__author__    = "Matteo Turilli"
__copyright__ = "Copyright 2013, The AIMES Project"
__license__   = "MIT"


"""AIMES workload manager (wmanager)

It takes a skeleton file as an input and it executes its output on a pilot.
. The current implementation is limited to the execution of coupled ensembles.
. Using bigjob >= 0.50
. Using saga-python >= 9.8

TODOs
. Integration with bundle information system.

"""


import sys
import time
import argparse
import traceback

import radical.owms
import radical.owms.application


# -----------------------------------------------------------------------------
if  __name__ == '__main__':

    #--------------------------------------------------------------------------
    # command line arguments
    #--------------------------------------------------------------------------
    if  2 != len(sys.argv) :
        print """
        usage: %s <skeleton_file>
        """ % sys.argv[0]
        sys.exit (0)

    skeleton_file = sys.argv[1]

    # initialize radical.owms
    workload_mgr = radical.owms.WorkloadManager ()
    overlay_mgr  = radical.owms.OverlayManager ()
    planner      = radical.owms.Planner ('default')

    try:

      # credentials = wmanager.Credentials()
      #
      # credentials.add_coordination_password(args.coordination_password)
      # credentials.add_ssh_user_name(args.ssh_user_name)
      # credentials.add_ssh_private_key(args.ssh_private_key)


        # create workloads from skeleton, for all stages
        skeleton_application = radical.owms.application.Skeleton ('test_skeleton', 
                                                          skeleton_file, 
                                                          'Shell')

        workloads = skeleton_application.generate_workloads ()

        # execute each stage's workload in radical.owms
        for workload in workloads :

            # create, schedule and start overlay for workload execution
            overlay_id = planner.derive_overlay (workload.id)
            overlay_mgr.translate_overlay       (overlay_id)
            workload_mgr.translate_workload     (workload.id, overlay_id)
            workload_mgr.bind_workload          (workload.id, overlay_id,
                                                 bind_mode=radical.owms.EARLY)
            overlay_mgr.schedule_overlay        (overlay_id)
            overlay_mgr.provision_overlay       (overlay_id)

            # on overlay, schedule and run workload
            workload_mgr.dispatch_workload      (workload.id, overlay_id)

            # wait for workload to reach a final state
            while workload.state not in [radical.owms.DONE, radical.owms.FAILED]:
                radical.owms._logger.info ("whats up, buddy? (workload state: %s)" % workload.state)
                time.sleep(1)

            radical.owms._logger.info ("ok, buddy, lets see what you got (workload state: %s)" % workload.state)

            # clean up
            workload_mgr.cancel_workload (workload.id)
            overlay_mgr .cancel_overlay  (overlay_id)

            if  workload.state != radical.owms.DONE :
                radical.owms._logger.info  ("workload failed!")
                raise RuntimeError ("workload failed!")

            radical.owms._logger.info ("workload done")

        radical.owms._logger.info ("all workloads done")


    except Exception as ex :

        print "AN ERROR OCCURED: %s" % str(ex)
        # print a stack trace in case of an exception -
        # this can be helpful for debugging the problem
        traceback.print_exc ()
        sys.exit (-1)

    # all is well
    sys.exit (0)

