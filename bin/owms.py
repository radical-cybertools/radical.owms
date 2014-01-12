#!/usr/bin/env python

__author__ = "Matteo Turilli"
__copyright__ = "Copyright 2013, The AIMES Project"
__license__ = "MIT"


"""AIMES overlay and workload manager system (owms)

It takes a workload description as an input and executes it on one or more a 
pilots.
. The current implementation is limited to the execution of bag of tasks.
. Uses TROY >= 0.1

Assumptions:

TODOs:

"""

import sys
import os
import pdb
import math
import argparse
import traceback

import troy


def main(args):

    # Check whether the requested application generator, pilot system and
    # skeleton modes are implemented.
    if not args.application_generator in ['skeleton', 'file']:
        raise Exception("Application generator \'%s\' not supported." % args.application_generator)

    if args.skeleton_mode != 'Shell':
        raise Exception("%s is not supported." % args.skeleton_mode)

    if not args.pilot_system in ['BigJob', 'SagaPilot']:
        raise Exception("Pilot system \'%s\' is not supported." % args.pilot_system)


    # Select the requested execution strategy.
    strategy = ExecutionStrategy(args)

    if args.execution_mode == 'local':
        strategy.local()

    if args.execution_mode == 'remote':
        strategy.remote()

    sys.exit(0)


#==============================================================================
class ExecutionStrategy(object):

    def __init__(self, args):

        self.execution_mode        = args.execution_mode

        self.coordination_password = args.coordination_password
        self.ssh_user_name         = args.ssh_user_name
        self.ssh_private_key       = args.ssh_private_key

        self.bj_config             = args.bigjob_config
        self.binding_order         = args.binding_order
        self.number_of_cores       = args.number_of_cores
        
        self.information_system    = args.information_system        
        self.bundle_config         = args.bundle_config

        self.workload_description  = args.workload_description 
        self.skeleton_mode         = args.skeleton_mode 
        self.skeleton_output_file  = args.skeleton_output_file
        self.concurrency           = args.concurrency
        self.task_execution_time   = args.task_execution_time

        self.credentials           = None
        self.bundle                = None
        self.skeleton              = None
        self.workload              = None
        self.overlay               = None


    #--------------------------------------------------------------------------
    # STRATEGIES
    #--------------------------------------------------------------------------
    # Add profile and arguments to describe the experiments.
    def local(self):
        
        try:

            self.set_credentials()
            self.generate_skeleton()
            self.generate_workload()
            self.generate_overlay()
            self.instantiate_overlay()
            self.execute_workload()

        except Exception, ex:

            print "The local execution strategy has failed: %s" % ((str(ex)))
            traceback.print_exc()
            sys.exit(-1)

        finally:

            if self.overlay:
                self.overlay.shutdown()

    #--------------------------------------------------------------------------
    def remote(self):
        
        try:

            self.set_credentials()
            self.generate_skeleton()
            self.generate_workload()
            self.generate_overlay()
            self.instantiate_overlay()
            self.execute_workload()

        except Exception, ex:

            print "The remote execution strategy has failed: %s" % ((str(ex)))
            traceback.print_exc()
            sys.exit(-1)

        finally:

            if self.overlay:
                self.overlay.shutdown()

    #--------------------------------------------------------------------------
    # CREDENTIALS
    #--------------------------------------------------------------------------
    def set_credentials(self):

        try:

            timer = Timer('EXPERIMENT: Acquiring credentials')

            self.credentials = wmanager.Credentials()

            self.credentials.add_coordination_password(self.coordination_password)
            self.credentials.add_ssh_user_name(self.ssh_user_name)
            self.credentials.add_ssh_private_key(self.ssh_private_key)

            timer.checkpoint('is done')

        except Exception, ex:

            print "Credentials setup failed: %s" % ((str(ex)))
            timer.checkpoint('is done')
            traceback.print_exc()
            sys.exit(-1)


    #--------------------------------------------------------------------------
    # SKELETON
    #--------------------------------------------------------------------------
    def generate_skeleton(self):

        try:

            self.skeleton = wmanager.adapters.Skeleton('test_skeleton', 
                self.workload_description, 
                self.skeleton_mode, 
                self.skeleton_output_file,
                self.task_execution_time
            )
            
            self.skeleton.generate()

        except Exception, ex:

            print "Skeleton generation failed: %s" % ((str(ex)))
            traceback.print_exc()
            sys.exit(-1)


    #--------------------------------------------------------------------------
    # WORKLOAD
    #--------------------------------------------------------------------------
    def generate_workload(self):

        try:

            self.workload = wmanager.Workload('skeleton', 
                self.skeleton, 
                self.concurrency
            )    
            self.workload.generate()

        except Exception, ex:

            print "Workload generation failed: %s" % ((str(ex)))
            traceback.print_exc()
            sys.exit(-1)

    #--------------------------------------------------------------------------
    def execute_workload(self):

        try:

            self.workload.execute(self.overlay)

        except Exception, ex:

            print "Workload execution failed: %s" % ((str(ex)))
            traceback.print_exc()
            sys.exit(-1)



    #--------------------------------------------------------------------------
    # PILOT OVERLAY
    #--------------------------------------------------------------------------
    def generate_overlay(self):

        try:

            self.overlay = wmanager.PilotFramework(self.execution_mode, 
                self.bj_config, 
                self.workload, 
                self.credentials, 
                self.information_system, 
                self.bundle_config,
                self.binding_order,
                self.number_of_cores
            )

            # Generate the pilot framework for the given workload
            #
            # - describe_pilots()
            # - escribe_compute_units()
            # - bigjob.PilotComputeService()
            self.overlay.generate()

        except Exception, ex:

            print "Overlay generation failed: %s" % ((str(ex)))
            traceback.print_exc()
            sys.exit(-1)


    #--------------------------------------------------------------------------
    def instantiate_overlay(self):
        # FRAMEWORK INSTANTIATION - BULK API
        # 
        # - bulk_bind_pilots_to_resource()
        # - bulk_schedule_cus_to_pilots()
        # - bulk_instantiate_pilots()
        # - bulk_stage_in_data()
        
        try:

            if self.binding_order == 'WR':
                self.overlay.bulk_schedule_cus_to_pilots('WR')
                self.overlay.bulk_bind_pilots_to_resource()
                self.overlay.bulk_instantiate_pilots()
                self.overlay.bulk_stage_in_data()

            if self.binding_order == 'RW':
                self.overlay.bulk_bind_pilots_to_resource()
                self.overlay.bulk_instantiate_pilots()
                self.overlay.bulk_schedule_cus_to_pilots('RW')
                self.overlay.bulk_stage_in_data()

        except Exception, ex:

            print "Overlay instantiation failed: %s" % ((str(ex)))
            traceback.print_exc()
            sys.exit(-1)

    #--------------------------------------------------------------------------
    def shutdown_overlay(self):

        try:
        
            self.overlay.shutdown()

        except Exception, ex:

            print "Overlay shutdown failed: %s" % ((str(ex)))
            traceback.print_exc()
            sys.exit(-1)


#==============================================================================
if __name__ == '__main__':

    #--------------------------------------------------------------------------
    # COMMAND LINE PARSER
    #--------------------------------------------------------------------------
    parser = argparse.ArgumentParser(description='Automates the execution of' 
        'a given workload description on a tailored pilot framework.')

    # Nestor
    # To be replaced by --troy-dispatcher
    parser.add_argument(
        '-m', '--execution-mode',
        choices = ['remote', 'local'], default='remote',
        metavar = 'execution_mode',
        help    = 'The execution mode: On localhost (local) or on remote \
        resources (remote). Default: remote.'
    )

    parser.add_argument(
        '-bo', '--binding-order',
        choices = ['RW', 'WR'], default='WR',
        metavar = 'binding_order',
        help    = 'The order in which compute resources (R) and workload (W) \
        are bound to pilots. RW = Resources are bound before the Workload; WR \
        = Workload is bound before the Resources. Default: WR.'
    )

    parser.add_argument(
    '-nc', '--number-of-cores',
        default = 8,
        metavar = 'number_of_cores',
        help    = 'The number of cores that each pilot of the framework \
        should bind. This option is honored only when selecting RW as \
        binding strategy. Default: 8.'
    )

    parser.add_argument(
    '-cc', '--concurrency',
        default=100,
        metavar = 'concurrency',
        help    = 'The degree of concurrency of the workload. 100 = all \
        tasks run on a pilot with a single core. 0 = all tasks run on \
        a pilot with #cores = #tasks. Default: 100.'
    )

    parser.add_argument(
    '-td', '--task-duration',
        default = 0,
        metavar = 'task_duration',
        help    = 'The time taken by each task to execute. Tasks are \
        homogeneous so they all take the same time to execute.'
    )

    # Execution manager
    parser.add_argument(
        '-E', '--execution-manager',
        choices = ['TROY', 'manual'], default='TROY',
        metavar = 'execution_manager',
        help    = 'The execution manager system used to execute the given \
        workload. Default: TROY.'
    )

    parser.add_argument(
        '-ep', '--troy-planner',
        choices = ['concurrent', ], default='concurrent',
        metavar = 'troy_planner',
        help    = 'The planner used by TROY. Default: concurrent'
    )

    parser.add_argument(
        '-ews', '--troy-workload-scheduler',
        choices = ['roundrobin', 'loadbalance'], default='roundrobin',
        metavar = 'troy_overlay_scheduler',
        help    = 'The algorithm used to schedule the overlay on the targeted \
        resources. Default: roundrobin'
    )

    parser.add_argument(
        '-ewd', '--troy-workload-dispatcher',
        choices = ['local', 'remote'], default='TROY',
        metavar = 'troy_workload_dispatcher',
        help    = 'The dispatcher used by TROY. Default: local'
    )

    parser.add_argument(
        '-eos', '--troy-overlay-scheduler',
        choices = ['roundrobin'], default='roundrobin',
        metavar = 'troy_overlay_scheduler',
        help    = 'The algorithm used to schedule the overlay on the targeted \
        resources. Default: roundrobin'
    )

    parser.add_argument(
        '-eop', '--troy-overlay-provisioner',
        choices = [''], default='',
        metavar = 'troy_overlay_provisioner',
        help    = 'The provisioner of the overlay on the targeted \
        resources. Default: '
    )

    # Pilot
    parser.add_argument(
        '-P', '--pilot-system',
        choices = ['BigJob', 'SagaPilot'], default='BigJob',
        metavar = 'pilot_system',
        help    = 'The type of pilot system used to execute the given \
        workload. Default: BigJob.'
    )

    parser.add_argument(
        '-bj', '--bigjob-config',
        default = sys.prefix+'/etc/bigjob.conf',
        metavar = 'bigjob_config',
        help    = 'The BigJob configuration file. Default file located at \
        <virtualenv>/etc/bigjob.conf'
    )

    # Application
    parser.add_argument(
        '-A', '--application-generator',
        choices = ['skeleton', 'abstract-application', 'file'], 
        default='skeleton',
        metavar = 'application_generator',
        help    = 'The type of application used to generate the workload to \
        execute. Default: Skeleton.'
    )

    parser.add_argument(
        '-sm', '--skeleton-mode',
        choices = ['Shell', 'Swift', 'DAX'], default='Shell',
        metavar = 'skeleton_mode',
        help    = 'The mode in which you want to run your skeleton: Shell, \
        Swift, DAX. Default: Shell'
    )

    parser.add_argument(
        '-so', '--skeleton-output-file',
        metavar = 'skeleton_output_file',
        help    = 'Save the output of a skeleton to a file.'
    )

    # Information system
    parser.add_argument(
        '-I', '--information-system',
        choices = ['bundles', 'static'],
        default = 'bundles',
        metavar = 'information_system',
        help    = 'The system used to collect information about the resources \
        on which to run the given workload. \'Bundles\' to collect dynamic \
        information; \'static\' to use the pilot configuration file with the \
        three keys: service_url, queue, and walltime_max_queue. \
        Default: Bundles.'
    )

    parser.add_argument(
        '-b', '--bundle-config',
        default = sys.prefix+'/etc/bundle.conf',
        metavar = 'bundle_config',
        help    = 'The configuration file of the bundle manager. Default file \
        located at <virtualenv>/etc/bundle.conf'
    )

    # Credentials
    parser.add_argument(
        '-c', '--coordination-password',
        metavar = 'coordination_password',
        help    = 'Password for the coordination server. The endpoint of the \
        coordination server is set in configuration file of the pilot with \
        the key \'coordination_url\''
    )

    parser.add_argument(
        '-u', '--ssh-user-name',
        metavar = 'ssh_user_name',
        help    = 'User name for ssh. Needed to access the remote resources \
        like, for example, FutureGrid.'
    )

    parser.add_argument(
        '-k', '--ssh-private-key',
        metavar = 'ssh_private_key',
        help    = 'Private ssh key. Needed to access the remote resources \
        like, for example, FutureGrid.'
    )  

    # The description of the workload to be executed is the only mandatory
    # positional argument.
    parser.add_argument(
        'workload_description',
        metavar = 'workload_description',
        help    = 'The description of the application workload to execute. By \
        default a skeleton description.'
    )

    # Print help message if no arguments are passed. Better than the default 
    # error message.
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    # Manage dependences among parser arguments
    if args.execution_mode == 'local':
        args.bundle_config = None
        args.information_system = 'static'

    if args.information_system == 'static':
        args.bundle_config = None

    if args.application_generator != 'skeleton':
        args.skeleton_mode = None
        args.skeleton_output_file = None

    if args.binding_order != 'RW':
        args.number_of_cores = None

    if args.binding_order == 'WR' and args.concurrency == 0:
        args.number_of_cores = 1

    # print "DEBUG: args %s" % args
    # print "DEBUG: sys.prefix %s" % sys.prefix
    # print "DEBUG: sys.exec_prefix %s" % sys.exec_prefix

    # Execute nestor.
    main(args)
