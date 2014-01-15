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
. Move the workload/task classes to a dedicated tool/module.
. Generalize TROY instantiation, workload translation and execution to methods.

"""

import sys
import os
import subprocess
import pdb
import math
import argparse
import traceback

import troy

# Configuration parameters owms.py

# '-m',   '--execution-mode',           choices=['remote', 'local'],                  default='remote',           metavar='execution_mode',
# '-bo',  '--binding-order',            choices=['RW', 'WR'],                         default='WR',               metavar='binding_order',
# '-cc',  '--concurrency',                                                            default=100,                metavar='concurrency',
# '-E',   '--execution-manager',        choices=['TROY', 'manual'],                   default='TROY',             metavar='execution_manager',
# '-ep',  '--troy-planner',             choices=['concurrent', ],                     default='concurrent',       metavar='troy_planner',
# '-ews', '--troy-workload-scheduler',  choices=['roundrobin', 'loadbalance'],        default='roundrobin',       metavar='troy_overlay_scheduler',
# '-ewd', '--troy-workload-dispatcher', choices=['local', 'remote'],                  default='TROY',             metavar='troy_workload_dispatcher',
# '-eos', '--troy-overlay-scheduler',   choices=['roundrobin'],                       default='roundrobin',       metavar='troy_overlay_scheduler',
# '-eop', '--troy-overlay-provisioner', choices=[''],                                 default='',                 metavar='troy_overlay_provisioner',
# '-P',   '--pilot-system',             choices=['BigJob', 'saga-pilot'],             default='BigJob'            metavar='pilot_system'
# '-bj',  '--bigjob-config',                                                          default='etc/bigjob.conf',  metavar='bigjob_config'
# '-pc',  '--pilot-count',                                                            default=1,                  metavar='pilot_count',
# '-pcc', '--pilot-core-count',                                                       default=8,                  metavar='pilot_core_count',
# '-A',   '--application-generator',    choices=['skeleton', 'abstract-application'], default='skeleton',         metavar='application_generator'
# '-sm',  '--skeleton-mode',            choices=['Shell', 'Swift', 'DAX'],            default='Shell',            metavar='skeleton_mode'
# '-so',  '--skeleton-output-file',                                                                               metavar='skeleton_output_file',
# '-wc',  '--workload-count',                                                         default=1,                  metavar='workload_count',
# '-wp',  '--workload-pattern',         choices=['HOBOT', 'HEBOT'],                   default='HOBOT',            metavar='workload_pattern',
# '-wld', '--workload-local-directory',                                               default=sys.prefix+'.',     metavar='workload_local_directory',
# '-wrd', '--workload-remote-directory',                                                                          metavar='workload_remote_directory',
# '-td',  '--task-duration',                                                          default=0,                  metavar='task_duration',
# '-tc',  '--task-count',                                                             default=1,                  metavar='task_count',
# '-tis', '--task-input-file-size',                                                   default=1048576,            metavar='task_input_file_size',
# '-tos', '--task-output-file-size',                                                  default=1048576,            metavar='task_output_files_size',
# '-I',   '--information-system',       choices=['bundles'],                          default='bundles',          metavar='information_system'
# '-b',   '--bundle-config',                                                          default='etc/bundle.conf',  metavar='bundle_config'
# '-c',   '--coordination-password',                                                                              metavar='coordination_password'
# '-u',   '--ssh-user-name',                                                                                      metavar='ssh_user_name'
# '-k',   '--ssh-private-key',                                                                                    metavar='ssh_private_key'

# TODO: Delete and add an option task_description flag.
# 'workload_description', metavar='workload_description',

#==============================================================================
def main(args):

    # AIMES workload variables.
    working_directory = None
    aimes_workloads   = []
    
    # TROY variables.
    planner           = None
    workload_manager  = None
    overlay_manager   = None
    task_descriptions = []


    # Check whether the requested application generator, pilot system and
    # skeleton modes are implemented.
    if not args.application_generator in ['skeleton', 'file']:
        raise Exception("Application generator \'%s\' not supported." % 
            args.application_generator)

    if args.skeleton_mode != 'Shell':
        raise Exception("%s is not supported." % args.skeleton_mode)

    if not args.pilot_system in ['BigJob', 'SagaPilot']:
        raise Exception("Pilot system \'%s\' is not supported." % 
            args.pilot_system)

    # Execution mode affects both execution environment and strategy.
    if args.execution_mode == 'local':
        working_directory = args.workload_local_directory

    elif args.execution_mode == 'remote':
        working_directory = args.workload_remote_directory

    # Generate the workload(s) to be executed by means of an overlay.
    for counter in range(args.workload_count):

        w = Workload(counter, 
                args.workload_pattern, 
                working_directory, 
                args.task_duration, 
                args.task_count, 
                args.task_input_file_size, 
                args.task_output_file_size)

        w.create_tasks()

        aimes_workloads.append(w)

    # Translate the workload(s) into TROY internal workload description. 
    # NOTE: This is missing in TROY at the moment. We need a plugin for each
    #       workload.
    for w in aimes_workloads:
        for t in w.tasks:

            tag = t.workload.name+'-'+t.name

            task_description                   = troy.TaskDescription()
            task_description.tag               = "%s" % tag
            task_description.executable        = '/bin/sh'
            task_description.arguments         = [tag+'.sh']
            task_description.inputs            = [t.input_file]
            task_description.outputs           = [t.output_file]
            task_description.working_directory = working_directory

            task_descriptions.append(task_description)

    # Instantiate TROY planner, data stager, and managers.
    # TODO: Note that the provisioner has a funny name (AUTOMATIC?). We need to
    # use args.troy_overlay_rovisioner with a set of plausible names. We will 
    # take care of consistency checks (what scheduler goes with what 
    # provisioner) after parsing the CL arguments.
    session = troy.Session({'concurrent_planner' : {'concurrency' : args.concurrency}})

    data_stager      = troy.DataStager ()
    planner          = troy.Planner(planner = args.troy_planner, session = session)
    workload_manager = troy.WorkloadManager(dispatcher = args.troy_workload_dispatcher, stager = data_stager)
    overlay_manager  = troy.OverlayManager(scheduler = args.troy_overlay_scheduler, provisioner = args.troy_overlay_provisioner)

    # Questions: 
    # - How do I set the degree of concurrency for the planner?
    # - Can I use 1 workload manager for multiple workloads? (I think so)
    # - Do I have a tag in a troy task description to store the name of the 
    #   workload to which that task belongs?
    # - Can we change the name of the planner from 'concurrency' to 
    #   'concurrent'?
    # - How do we use bundles?

    # The following is 'quick and dirty' while waiting to answer to the 
    # questions above.
    workload_id = workload_manager.create_workload(task_descriptions)
    troy.execute_workload(workload_id, planner, overlay_manager, workload_manager, strategy='basic')


#==============================================================================
class Workload(object):

    def __init__(self, counter, pattern, directory, task_duration, task_count, 
        task_input_file_size, task_output_file_size):
        
        self.name          = pattern.lower()+'_'+str(counter)
        self.counter       = counter
        self.pattern       = pattern
        self.directory     = directory
        self.task_duration = task_duration
        self.task_count    = task_count
        self.task_if_size  = task_input_file_size
        self.task_of_size  = task_output_file_size

        self.tasks         = []


    def create_tasks(self):

        for task_number in range(self.task_count):

            task = Task(self, task_number, self.directory, 
                self.task_duration, self.task_if_size, self.task_of_size)

            task.write_input_file()
            task.write_executable()

            self.tasks.append(task)


#==============================================================================
class Task(object):

    def __init__(self, workload, counter, working_directory, duration, if_size, 
        of_size):

        self.name              = 'task_'+str(counter)
        self.working_directory = working_directory
        self.duration          = duration
        self.input_file_size   = if_size
        self.output_file_size  = of_size

        self.workload          = workload

        self.input_file        = None
        self.output_file       = None
        self.executable_name   = None
 

    def write_input_file(self):
        
        self.input_file = self.workload.name+'-'+self.name+'.input'

        subprocess.call(["dd", "if=/dev/zero", 
            "of="+self.working_directory+'/'+self.input_file, 
            "bs="+str(self.input_file_size), 
            "count=1"])


    def write_executable(self):

        self.executable_name = self.workload.name+'-'+self.name+'.sh'
        self.output_file     = self.workload.name+'-'+self.name+'.output'

        self.executable = open("%s/%s" % 
            (self.working_directory, self.executable_name), "w")

        self.executable.write("#!/bin/bash\n\n")

        self.executable.write("date\n")
        self.executable.write("echo $0\n")
        self.executable.write("whoami\n")
        self.executable.write("pwd\n\n")

        self.executable.write("sleep %s\n\n" % self.duration)
        
        self.executable.write("cat %s > /dev/null\n" % self.input_file)

        self.executable.write("dd if=/dev/zero of=%s bs=%s count=1\n" % 
            (self.output_file, self.output_file_size))
        
        self.executable.close()

        os.chmod(self.working_directory+"/"+self.executable_name, 0755)


#==============================================================================
# class ExecutionStrategy(object):

#     def __init__(self, args):

#         self.coordination_password = args.coordination_password
#         self.ssh_user_name         = args.ssh_user_name
#         self.ssh_private_key       = args.ssh_private_key

#         self.bj_config             = args.bigjob_config
#         self.binding_order         = args.binding_order
#         self.number_of_cores       = args.number_of_cores
        
#         self.information_system    = args.information_system        
#         self.bundle_config         = args.bundle_config

#         self.workload_description  = args.workload_description 
#         self.skeleton_mode         = args.skeleton_mode 
#         self.skeleton_output_file  = args.skeleton_output_file
#         self.concurrency           = args.concurrency
#         self.task_execution_time   = args.task_execution_time

#         self.credentials           = None
#         self.bundle                = None
#         self.skeleton              = None
#         self.workload              = None
#         self.overlay               = None


    #--------------------------------------------------------------------------
    # STRATEGIES
    #--------------------------------------------------------------------------
    # Add profile and arguments to describe the experiments.
    # def local(self):
        
    #     try:

    #         self.set_credentials()
    #         self.generate_skeleton()
    #         self.generate_workload()
    #         self.generate_overlay()
    #         self.instantiate_overlay()
    #         self.execute_workload()

    #     except Exception, ex:

    #         print "The local execution strategy has failed: %s" % ((str(ex)))
    #         traceback.print_exc()
    #         sys.exit(-1)

    #     finally:

    #         if self.overlay:
    #             self.overlay.shutdown()

    # #--------------------------------------------------------------------------
    # def remote(self):
        
    #     try:

    #         self.set_credentials()
    #         self.generate_skeleton()
    #         self.generate_workload()
    #         self.generate_overlay()
    #         self.instantiate_overlay()
    #         self.execute_workload()

    #     except Exception, ex:

    #         print "The remote execution strategy has failed: %s" % ((str(ex)))
    #         traceback.print_exc()
    #         sys.exit(-1)

    #     finally:

    #         if self.overlay:
    #             self.overlay.shutdown()

    # #--------------------------------------------------------------------------
    # # CREDENTIALS
    # #--------------------------------------------------------------------------
    # def set_credentials(self):

    #     try:

    #         timer = Timer('EXPERIMENT: Acquiring credentials')

    #         self.credentials = wmanager.Credentials()

    #         self.credentials.add_coordination_password(self.coordination_password)
    #         self.credentials.add_ssh_user_name(self.ssh_user_name)
    #         self.credentials.add_ssh_private_key(self.ssh_private_key)

    #         timer.checkpoint('is done')

    #     except Exception, ex:

    #         print "Credentials setup failed: %s" % ((str(ex)))
    #         timer.checkpoint('is done')
    #         traceback.print_exc()
    #         sys.exit(-1)


    # #--------------------------------------------------------------------------
    # # SKELETON
    # #--------------------------------------------------------------------------
    # def generate_skeleton(self):

    #     try:

    #         self.skeleton = wmanager.adapters.Skeleton('test_skeleton', 
    #             self.workload_description, 
    #             self.skeleton_mode, 
    #             self.skeleton_output_file,
    #             self.task_execution_time
    #         )
            
    #         self.skeleton.generate()

    #     except Exception, ex:

    #         print "Skeleton generation failed: %s" % ((str(ex)))
    #         traceback.print_exc()
    #         sys.exit(-1)


    # #--------------------------------------------------------------------------
    # # WORKLOAD
    # #--------------------------------------------------------------------------
    # def generate_workload(self):

    #     try:

    #         self.workload = wmanager.Workload('skeleton', 
    #             self.skeleton, 
    #             self.concurrency
    #         )    
    #         self.workload.generate()

    #     except Exception, ex:

    #         print "Workload generation failed: %s" % ((str(ex)))
    #         traceback.print_exc()
    #         sys.exit(-1)

    # #--------------------------------------------------------------------------
    # def execute_workload(self):

    #     try:

    #         self.workload.execute(self.overlay)

    #     except Exception, ex:

    #         print "Workload execution failed: %s" % ((str(ex)))
    #         traceback.print_exc()
    #         sys.exit(-1)



    # #--------------------------------------------------------------------------
    # # PILOT OVERLAY
    # #--------------------------------------------------------------------------
    # def generate_overlay(self):

    #     try:

    #         self.overlay = wmanager.PilotFramework(self.execution_mode, 
    #             self.bj_config, 
    #             self.workload, 
    #             self.credentials, 
    #             self.information_system, 
    #             self.bundle_config,
    #             self.binding_order,
    #             self.number_of_cores
    #         )

    #         # Generate the pilot framework for the given workload
    #         #
    #         # - describe_pilots()
    #         # - escribe_compute_units()
    #         # - bigjob.PilotComputeService()
    #         self.overlay.generate()

    #     except Exception, ex:

    #         print "Overlay generation failed: %s" % ((str(ex)))
    #         traceback.print_exc()
    #         sys.exit(-1)


    # #--------------------------------------------------------------------------
    # def instantiate_overlay(self):
    #     # FRAMEWORK INSTANTIATION - BULK API
    #     # 
    #     # - bulk_bind_pilots_to_resource()
    #     # - bulk_schedule_cus_to_pilots()
    #     # - bulk_instantiate_pilots()
    #     # - bulk_stage_in_data()
        
    #     try:

    #         if self.binding_order == 'WR':
    #             self.overlay.bulk_schedule_cus_to_pilots('WR')
    #             self.overlay.bulk_bind_pilots_to_resource()
    #             self.overlay.bulk_instantiate_pilots()
    #             self.overlay.bulk_stage_in_data()

    #         if self.binding_order == 'RW':
    #             self.overlay.bulk_bind_pilots_to_resource()
    #             self.overlay.bulk_instantiate_pilots()
    #             self.overlay.bulk_schedule_cus_to_pilots('RW')
    #             self.overlay.bulk_stage_in_data()

    #     except Exception, ex:

    #         print "Overlay instantiation failed: %s" % ((str(ex)))
    #         traceback.print_exc()
    #         sys.exit(-1)

    # #--------------------------------------------------------------------------
    # def shutdown_overlay(self):

    #     try:
        
    #         self.overlay.shutdown()

    #     except Exception, ex:

    #         print "Overlay shutdown failed: %s" % ((str(ex)))
    #         traceback.print_exc()
    #         sys.exit(-1)


#==============================================================================
if __name__ == '__main__':

    #--------------------------------------------------------------------------
    # COMMAND LINE PARSER
    #--------------------------------------------------------------------------
    parser = argparse.ArgumentParser(description='Automates the execution of' 
        'a given workload description on a tailored pilot framework.')

    # -------------------------------------------------------------------------
    # Nestor
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
        '-cc', '--concurrency',
        default=100,
        metavar = 'concurrency',
        help    = 'The degree of concurrency of the workload. 100 = all \
        tasks run on a pilot with a single core. 0 = all tasks run on \
        a pilot with #cores = #tasks. Default: 100.'
    )


    # -------------------------------------------------------------------------
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
        choices = ['concurrent', 'bundles', 'maxcores'], 
        default = 'concurrent',
        metavar = 'troy_planner',
        help    = 'The planner used by TROY. Default: concurrent'
    )

    parser.add_argument(
        '-ews', '--troy-workload-scheduler',
        choices = ['first', 'round_robin', 'ttc_load_balancing'], 
        default = 'round_robin',
        metavar = 'troy_overlay_scheduler',
        help    = 'The algorithm used to schedule the overlay on the targeted \
        resources. Default: roundrobin'
    )

    parser.add_argument(
        '-ewd', '--troy-workload-dispatcher',
        choices = ['local', 'bigjob', 'sinon'], default='bigjob',
        metavar = 'troy_workload_dispatcher',
        help    = 'The dispatcher used by TROY. Default: local'
    )

    parser.add_argument(
        '-eos', '--troy-overlay-scheduler',
        choices = ['round_robin', 'local'], default='round_robin',
        metavar = 'troy_overlay_scheduler',
        help    = 'The algorithm used to schedule the overlay on the targeted \
        resources. Default: roundrobin'
    )

    parser.add_argument(
        '-eop', '--troy-overlay-provisioner',
        choices = ['local', 'bigjob', 'sinon'], default='bigjob',
        metavar = 'troy_overlay_provisioner',
        help    = 'The provisioner of the overlay on the targeted \
        resources. Default: local'
    )


    # -------------------------------------------------------------------------
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
        <virtualenv>/etc/bigjob.conf.'
    )

    parser.add_argument(
        '-pc', '--pilot-count',
        default = 1,
        type = int,
        metavar = 'pilot_count',
        help    = 'The number of pilots to be used to execute the given \
        workload. Default file located at. Default: 1.'
    )

    parser.add_argument(
        '-pcc', '--pilot-core-count',
        default = 8,
        type = int,
        metavar = 'pilot_core_count',
        help    = 'The number of cores that each pilot of the framework \
        should bind. This option is honored only when selecting RW as \
        binding strategy. Default: 8.'
    )


    # -------------------------------------------------------------------------
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

    parser.add_argument(
        '-wc', '--workload-count',
        default = 1,
        type = int,
        metavar = 'workload_count',
        help    = 'The number of workloads to be executed. Default: 1.'
    )    

    parser.add_argument(
        '-wp', '--workload-pattern',
        choices = ['HOBOT', 'HEBOT'], default='HOBOT',
        metavar = 'workload_pattern',
        help    = 'The type of workload produced by the application \
        generator. Default: Heterogeneous Bag of Tasks (HOBOT).'
    )

    parser.add_argument(
        '-wld', '--workload-local-directory',
        default = os.getcwd(),
        metavar = 'workload_local_directory',
        help    = 'The local working directory of the workload. Default: \
        owms.py execution directory.'
    )

    parser.add_argument(
        '-wrd', '--workload-remote-directory',
        metavar = 'workload_remote_directory',
        help    = 'The remote working directory of the workload.'
    )

    parser.add_argument(
        '-td', '--task-duration',
        default = 0,
        type = int,
        metavar = 'task_duration',
        help    = 'The time taken by each task to execute. Tasks are \
        homogeneous so they all take the same time to execute.'
    )

    parser.add_argument(
        '-tis', '--task-input-file-size',
        default = 1048576, #1MB in bytes
        type = int,
        metavar = 'task_input_files_size',
        help    = 'The size in bytes of the input file for all the tasks.'
    )

    parser.add_argument(
        '-tos', '--task-output-file-size',
        default = 1048576, #1MB in bytes
        type = int,
        metavar = 'task_output_files_size',
        help    = 'The size in bytes of the output file for all the tasks.'
    )

    parser.add_argument(
        '-tc', '--task-count',
        default = 1,
        type = int,
        metavar = 'task_count',
        help    = 'The number of tasks for the given workload.'
    )

    # -------------------------------------------------------------------------
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
    # parser.add_argument(
    #     'workload_description',
    #     metavar = 'workload_description',
    #     help    = 'The description of the application workload to execute. \
    #     By default a skeleton description.'
    # )

    # Print help message if no arguments are passed. Better than the default 
    # error message.
    # if len(sys.argv) == 1:
    #     parser.print_help()
    #     sys.exit(1)

    args = parser.parse_args()

    # Manage dependences among parser arguments.
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

    if args.execution_mode == 'local':
        args.troy_workload_dispatcher = 'local'
        args.troy_overlay_provisioner = 'local'

    if args.execution_mode == 'remote':
        if not args.workload_remote_directory:
            raise Exception("Please specify the remote directory for the "
                "workload execution with the flag -wrd. Use full path only.")


    # print "DEBUG: args %s" % args
    # print "DEBUG: sys.prefix %s" % sys.prefix
    # print "DEBUG: sys.exec_prefix %s" % sys.exec_prefix

    # Execute nestor.
    main(args)
