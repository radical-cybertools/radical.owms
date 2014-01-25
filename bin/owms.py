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

    if not args.pilot_system in ['bigjob', 'sinon']:
        raise Exception("Pilot system \'%s\' is not supported." %
            args.pilot_system)

    # Generate the workload(s) to be executed by means of an overlay.
    for counter in range(args.workload_count):

        w = Workload(counter,
                args.tag,
                args.workload_pattern,
                args.data_staging,
                args.local_working_directory,
                args.remote_working_directory,
                args.workload_directory,
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

            cu_description = troy.TaskDescription()

            if args.remote_working_directory:
                cu_description.working_directory = args.remote_working_directory
                print "OWMS DEBUG: task_description.working_directory: %s" % args.remote_working_directory
            else:
                cu_description.working_directory = args.local_working_directory
                print "OWMS DEBUG: task_description.working_directory: %s" % args.local_working_directory

            cu_description.tag        = t.tag
            cu_description.executable = '/bin/sh'
            cu_description.arguments  = [t.executable_name]

            # Type None for .input_file and output_file are not yet managed.
            if args.data_staging:
                cu_description.inputs  = [t.input_file, t.executable_name]
                cu_description.outputs = [t.output_file]

            task_descriptions.append(cu_description)

          # print cu_description.as_dict ()

    # Create a session for TROY.
    session = troy.Session(
        {
            'planner_concurrent': {
                'concurrency': args.concurrency
            },
            'workload_dispatcher_bigjob_pilot': {
                'coordination_url ': args.bigjob_coordination_endpoint
            },
            'overlay_provisioner_bigjob_pilot': {
                'coordination_url': args.bigjob_coordination_endpoint,
                'queue'           : 'batch'
            },
            'workload_dispatcher_sinon': {
                'coordination_url': args.sinon_coordination_endpoint
            },
            'overlay_provisioner_sinon': {
                'coordination_url': args.sinon_coordination_endpoint,
                'queue'           : 'batch'
            }
        })

    # Add resources to the session.
    if args.pilot_system == 'bigjob':

        session.user_cfg['overlay_scheduler_round_robin'] = {
          # 'resources': 'pbs+ssh://india.futuregrid.org/,pbs+ssh://sierra.futuregrid.org/'
            'resources': 'pbs+ssh://india.futuregrid.org/'
        }

    elif args.pilot_system == 'sinon':

        session.user_cfg['overlay_scheduler_round_robin'] = {
          # 'resources': 'futuregrid.INDIA,futuregrid.SIERRA'
            'resources': 'futuregrid.INDIA'
        }


    # Manage credentials.
    # TODO: set it to args.protocol (default ssh).
    c1 = troy.Context ('ssh')
    c1.user_id = args.ssh_user_name
    session.add_context (c1)

    # Instantiate TROY planner and managers.
    planner = troy.Planner(planner = args.troy_planner, session = session)

    # if args.data_staging:
    #     workload_manager = troy.WorkloadManager(dispatcher  = args.troy_workload_dispatcher,
    #                                             session     = session)
    # else:
    #     workload_manager = troy.WorkloadManager(dispatcher  = args.troy_workload_dispatcher,
    #                                             session     = session)
    workload_manager = troy.WorkloadManager(dispatcher  = args.troy_workload_dispatcher,
                                            scheduler   = args.troy_workload_scheduler,
                                            session     = session)

    overlay_manager  = troy.OverlayManager (scheduler   = args.troy_overlay_scheduler,
                                            provisioner = args.troy_overlay_provisioner,
                                            session     = session)

    # Questions:
    # - How do we use bundles?

    workload_id = workload_manager.create_workload(task_descriptions)
    troy.execute_workload(workload_id, planner, overlay_manager,
        workload_manager, strategy=args.troy_strategy)


#==============================================================================
class Workload(object):

    def __init__(self, counter, tag, pattern, data_staging,
        local_working_directory, remote_working_directory,
        workload_directory, task_duration, task_count,
        task_input_file_size, task_output_file_size):

        self.name               = pattern.lower()+'_'+str(counter)
        self.counter            = counter
        self.tag                = tag
        self.pattern            = pattern
        self.data_staging       = data_staging
        self.local_directory    = local_working_directory
        self.remote_directory   = remote_working_directory
        self.workload_directory = workload_directory
        self.task_duration      = task_duration
        self.task_count         = task_count
        self.task_if_size       = task_input_file_size
        self.task_of_size       = task_output_file_size

        self.tasks              = []


    def create_tasks(self):

        for task_number in range(self.task_count):

            task = Task(self, task_number, self.local_directory,
                self.remote_directory, self.workload_directory,
                self.task_duration, self.task_if_size,
                self.task_of_size, self.data_staging)

            if self.data_staging:
                task.write_input_file()

            task.write_executable()

            self.tasks.append(task)


#==============================================================================
class Task(object):

    def __init__(self, workload, counter, local_directory, remote_directory,
        workload_directory, duration, data_staging, if_size, of_size):

        self.name               = 'task_'+str(counter)
        self.local_directory    = local_directory
        self.remote_directory   = remote_directory
        self.workload_directory = workload_directory
        self.duration           = duration
        self.data_staging       = data_staging
        self.input_file_size    = if_size
        self.output_file_size   = of_size

        self.workload           = workload

        self.tag                = None
        self.working_directory  = None
        self.input_file         = None
        self.output_file        = None
        self.executable_name    = None


    def write_input_file(self):

        self.input_file = self.workload.name+'-'+self.name+'.input'

        subprocess.call(["dd", "if=/dev/zero",
            "of="+self.local_directory+'/'+self.input_file,
            "bs="+str(self.input_file_size),
            "count=1"])


    def write_executable(self):

        self.tag             = self.workload.name+'-'+self.name
        self.executable_name = self.workload.tag+self.tag+'.sh'
        self.output_file     = self.workload.tag+self.tag+'.output'

        # TODO: Using remote_directory is a stupid hack due to the lack of
        # data staging capabilities. It works only when running this on the
        # head node of the cluster where the pilot will be submitted.
        self.executable = open("%s/%s" %
            (self.remote_directory, self.executable_name), "w")

        self.executable.write("#!/bin/bash\n\n")

        self.executable.write("date                        > %s\n" % self.output_file)
        self.executable.write("echo hostname = `hostname` >> %s\n" % self.output_file)
        self.executable.write("echo kernel   = $0         >> %s\n" % self.output_file)
        self.executable.write("echo user     = `whoami`   >> %s\n" % self.output_file)
        self.executable.write("echo workdir  = `pwd`      >> %s\n" % self.output_file)

        self.executable.write("\nsleep %s\n" % self.duration)
        self.executable.write("echo 'slept for %s seconds' >> %s\n\n" % (self.duration, self.output_file))

        # TODO: THe choice of having a data staging is not yet implemented in
        # TROY.
        # if self.data_staging:
        #     self.executable.write("cat %s > /dev/null\n" % self.input_file)

        #     self.executable.write("dd if=/dev/zero of=%s bs=%s count=1\n" %
        #         (self.output_file, self.output_file_size))

        self.executable.close()

        # TODO: Change the directory once the data staging mess in TROY will
        # be fixed.
        os.chmod(self.remote_directory+"/"+self.executable_name, 0755)


#==============================================================================
if __name__ == '__main__':

    #--------------------------------------------------------------------------
    # COMMAND LINE PARSER
    #--------------------------------------------------------------------------
    parser = argparse.ArgumentParser(description='Automates the execution of'
        'a given workload description on a tailored pilot framework.')

    # -------------------------------------------------------------------------
    # OWMS
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

    parser.add_argument(
        '-lwd', '--local-working-directory',
        default = os.getcwd(),
        metavar = 'local_working_directory',
        help    = 'The working directory on the machine on which owms.py is \
        executed. Default: owms.py execution directory.'
    )

    parser.add_argument(
        '-rwd', '--remote-working-directory',
        metavar = 'remote_working_directory',
        help    = 'The working directory on the remote resource(s).'
    )

    parser.add_argument(
        '-ds', '--data-staging',
        default = None,
        metavar = 'data_staging',
        help    = 'Enables data staging if the workload requires it. \
                   Default: None.'
    )

    parser.add_argument(
        '-t', '--tag',
        default = "",
        metavar = 'tag',
        help    = 'Tag of the run. Useful when using owms.py in an \
        experimental setup that requires to identify uniquely each run. \
        Default: empty string.'
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
        '-es', '--troy-strategy',
        choices = ['basic', 'basic_early_binding', 'basic_late_binding'],
        default = 'basic_late_binding',
        metavar = 'troy_strategy',
        help    = 'The strategy used by TROY in order to execute the given \
        workload. Default: basic_late_binding.'
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
        metavar = 'troy_workload_scheduler',
        help    = 'The algorithm used to schedule the workload on the targeted \
        resources. Default: round_robin.'
    )

    parser.add_argument(
        '-ewd', '--troy-workload-dispatcher',
        choices = ['local', 'bigjob_pilot', 'sinon'], default='bigjob_pilot',
        metavar = 'troy_workload_dispatcher',
        help    = 'The dispatcher used by TROY. Default: local'
    )

    parser.add_argument(
        '-eos', '--troy-overlay-scheduler',
        choices = ['local', 'round_robin'],
        default='round_robin',
        metavar = 'troy_overlay_scheduler',
        help    = 'The algorithm used to schedule the overlay on the targeted \
        resources. Default: round_robin.'
    )

    parser.add_argument(
        '-eop', '--troy-overlay-provisioner',
        choices = ['local', 'bigjob_pilot', 'sinon'], default='bigjob_pilot',
        metavar = 'troy_overlay_provisioner',
        help    = 'The provisioner of the overlay on the targeted \
        resources. Default: local'
    )


    # -------------------------------------------------------------------------
    # Pilot
    parser.add_argument(
        '-P', '--pilot-system',
        choices = ['bigjob', 'sinon'], default='bigjob',
        metavar = 'pilot_system',
        help    = 'The type of pilot system used to execute the given \
        workload. Default: BigJob.'
    )

    parser.add_argument(
        '-sce', '--sinon-coordination-endpoint',
        metavar = 'sinon_coordination_endpoint',
        help    = 'The Sinon coordination URL. Location of the mongdb server.'
    )

    parser.add_argument(
        '-bj', '--bigjob-config',
        default = sys.prefix+'/etc/bigjob.conf',
        metavar = 'bigjob_config',
        help    = 'The BigJob configuration file. Default file located at \
        <virtualenv>/etc/bigjob.conf.'
    )

    parser.add_argument(
        '-bce', '--bigjob-coordination-endpoint',
        metavar = 'bigjob_coordination_endpoint',
        help    = 'The BigJob coordination endpoint. Location of the redis \
        server.'
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
        '-wld', '--workload-directory',
        default = os.getcwd(),
        metavar = 'workload_directory',
        help    = 'The working directory of the workload. Default: \
        owms.py execution directory.'
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

    if args.pilot_system == 'sinon':
        args.troy_workload_dispatcher = 'sinon'
        args.troy_overlay_provisioner = 'sinon'

    if args.pilot_system == 'bigjob':
        args.troy_workload_dispatcher = 'bigjob_pilot'
        args.troy_overlay_provisioner = 'bigjob_pilot'

    if args.execution_mode == 'local':
        args.remote_working_directory = None

    if args.execution_mode == 'remote':
        if not args.remote_working_directory:
            raise Exception("Please specify the remote directory for the "
                "workload execution with the flag -wrd. Use full path only.")


    # print "DEBUG: args %s" % args
    # print "DEBUG: sys.prefix %s" % sys.prefix
    # print "DEBUG: sys.exec_prefix %s" % sys.exec_prefix

    # Execute nestor.
    main(args)
