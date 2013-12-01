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

import troy
import troy.application


if  __name__ == '__main__':

    #--------------------------------------------------------------------------
    # COMMAND LINE PARSER
    #--------------------------------------------------------------------------
    parser = argparse.ArgumentParser(description='Automates the execution of' 
        'a given workload on a tailored pilot framework.')

    # Parser shared among commands with the pilot options.
    pilot_parser = argparse.ArgumentParser(add_help=False)

    pilot_parser.add_argument('pilot_type',
                        choices=['BigJob', 'saga-pilot'],
                        metavar='pilot_type',
                        help='The type of pilot system used to execute the' 
                             'given workload.')

    pilot_parser.add_argument("pilot_input_file",
                        metavar="pilot_input_file",
                        help='File with the configuration for the '
                             'pilot and CUs'
                        )

    pilot_parser.add_argument("-b", "--bundle-input-file",
                        metavar="bundle_input_file",
                        help='File with the resource endpoints for the Bundle' 
                             'Manager.'
                        )

    pilot_parser.add_argument("-c", "--coordination-password",
                        metavar="coordination_password",
                        help='Password for the coordination server.'
                             'The endpoint of the coordination server is set'
                             'in configuration file of the pilot with the key'
                             'coordination_url'
                        )

    pilot_parser.add_argument("-u", "--ssh-user-name",
                        metavar="ssh_user_name",
                        help='User name for ssh.'
                             'Needed to access the remote resources like, for '
                             'example, FutureGrid.'
                        )

    pilot_parser.add_argument("-k", "--ssh-private-key",
                        metavar="ssh_private_key",
                        help='Private ssh key.'
                             'Needed to access the remote resources like, for '
                             'example, FutureGrid.'
                        )  

    subparser = parser.add_subparsers(dest="application_name", help='commands')

    # Skeleton arguments.
    parser_skeleton = subparser.add_parser('skeleton', 
        help='Execute a skeleton workload', 
        parents=[pilot_parser])
    
    parser_skeleton.add_argument("skeleton_input_file",
                        metavar="skeleton_input_file",
                        help='File with the skeleton description.'
                        )

    parser_skeleton.add_argument("skeleton_mode",
                        metavar="skeleton_mode",
                        choices=["Shell", "Swift", "DAX"],
                        help='The mode in which you want to run your skeleton:'
                             'Shell, Swift, DAX.'
                        )

    parser_skeleton.add_argument("-o", "--skeleton-output-file",
                        metavar="skeleton_output_file",
                        help='Skeleton output file. By default, '
                             'the skeleton output is written to STDOUT.'
                        )

    # Marvin arguments.
    # parser_marvin = subparser.add_parser('marvin', 
    #     help='Execute a marvin workload', 
    #     parents=[pilot_parser])

    # parser_marvin.add_argument("marvin_input_file",
    #                     metavar="marvin_input_file",
    #                     help='File with the Marvin workflow description'
    #                     )

    # Print help message if no arguments are passed. Better than the default 
    # error message.
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()


    # initialize troy
    workload_mgr = troy.WorkloadManager ()
    overlay_mgr  = troy.OverlayManager ()
    planner      = troy.Planner ('default')

    #--------------------------------------------------------------------------
    # PILOT FRAMEWORK AND WORKLOAD MANAGEMENT
    #--------------------------------------------------------------------------
    if args.application_name == 'skeleton':
        if args.pilot_type == 'BigJob':
            if args.skeleton_mode == 'Shell':

                try:

                  # #----------------------------------------------------------
                  # # CREDENTIALS
                  # #----------------------------------------------------------
                  # credentials = wmanager.Credentials()
                  #
                  # credentials.add_coordination_password(args.coordination_password)
                  # credentials.add_ssh_user_name(args.ssh_user_name)
                  # credentials.add_ssh_private_key(args.ssh_private_key)
                  #
                  # #----------------------------------------------------------
                  # # SKELETON
                  # #----------------------------------------------------------
                  # skeleton = wmanager.adapters.Skeleton('test_skeleton', 
                  #                     args.skeleton_input_file, 
                  #                     args.skeleton_mode, 
                  #                     args.skeleton_output_file)
                  # 
                  # skeleton.generate()

                    #----------------------------------------------------------
                    # WORKLOAD
                    #----------------------------------------------------------
                    skeleton_application = troy.application.Skeleton \
                                             ('test_skeleton', 
                                              args.skeleton_input_file, 
                                              args.skeleton_mode, 
                                              args.skeleton_output_file)

                    workloads = skeleton_application.generate_workloads ()
                    workload_mgr.register_workload (workloads)

                  # #----------------------------------------------------------
                  # # BUNDLE
                  # #----------------------------------------------------------
                  # bundle = None
                  #
                  # if args.bundle_input_file:
                  #     bundle = wmanager.adapters.Bundle(args.bundle_input_file)
                  #
                  #     #bundle.load_cluster_credentials(args.bundle_input_file)
                  #     bundle.generate()
                  #
                  # #----------------------------------------------------------
                  # # WORKLOAD
                  # #----------------------------------------------------------
                  # workload = wmanager.Workload('skeleton', skeleton)
                  # 
                  # workload.generate()
                  #
                  # #----------------------------------------------------------
                  # # PILOT FRAMEWORK
                  # #----------------------------------------------------------
                  # # TODO: add configuration keys so to specify:
                  # # . early/late binding.
                  # pilot_framework = wmanager.PilotFramework(
                  #                     args.pilot_input_file,
                  #                     workload, 
                  #                     credentials,
                  #                     bundle)
                  #
                  # # Generate the pilot framework for the given workload
                  # pilot_framework.generate()
                  #
                  # # Instantiate the pilot framework (note: includes staging 
                  # # data into the given resource).
                  # pilot_framework.instantiate()
  
                    #----------------------------------------------------------
                    # EXECUTING
                    #----------------------------------------------------------
                    for workload in workloads :

                        overlay_id = planner.derive_overlay (workload.id)
                        overlay_mgr.translate_overlay       (overlay_id)
                        overlay_mgr.schedule_overlay        (overlay_id)
                        overlay_mgr.provision_overlay       (overlay_id)

                        workload_mgr.translate_workload     (workload.id, overlay_id)
                        workload_mgr.bind_workload          (workload.id, overlay_id,
                                                             bind_mode=troy.LATE)
                        workload_mgr.dispatch_workload      (workload.id, overlay_id)

                    while workload.state not in [troy.DONE, troy.FAILED]:
                        troy._logger.info ("whats up, buddy? (workload state: %s)" % workload.state)
                        time.sleep(1)

                    troy._logger.info ("ok, buddy, lets see what you got (workload state: %s)" % workload.state)

                    if workload.state == troy.DONE :
                        troy._logger.info ("game over")
                    else :
                        troy._logger.info ("game over -- play again?")

                    workload_mgr.cancel_workload (workload.id)   # same as workload.cancel ()
                    overlay_mgr .cancel_overlay  (overlay_id)


                  # workload.execute(pilot_framework)
  
                except Exception, ex:

                    print "AN ERROR OCCURED: %s" % ((str(ex)))
                    # print a stack trace in case of an exception -
                    # this can be helpful for debugging the problem
                    traceback.print_exc()
                    sys.exit(-1)

                finally:

                    # Cleaning up
##                  pilot_framework.shutdown()
##
##                  if bundle:
##                      bundle.shutdown()
                    pass

            else:
                print "Execution mode %s is not yet implemented." % args.mode
        else:
            print "Pilot system %s is not yet implemented." % args.pilot_type
    else:
        print "Application %s is not yet supported." % args.application_name

    sys.exit(0)

