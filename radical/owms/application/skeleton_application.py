
__author__    = "Matteo Turilli"
__copyright__ = "Copyright 2013, The AIMES Project"
__license__   = "MIT"


"""
Adapter pattern to translate the workload interface implemented by a 
skeleton to the one implemented by the AIMES workload manager.
"""

# FIXME: we can't call this file 'radical.owms/application/skeleton.py', because we
# import the top-level 'skeleton.py' below -- or try to.  This should be fixed
# in aimes, to move into a namespace hierarchy like 'aimes/skeleton.py' ...


import os
import skeleton
import subprocess

import radical.owms

# ------------------------------------------------------------------------------
#
class Skeleton (skeleton.Application) :
    """
    This class uses the aimes skeleton module to create a staged set of tasks
    according to some skeleton description.  It adds methods to execute the
    skeleton via BigJob, and translates it into a radical.owms workload.
    """

    def __init__ (self, name, input_file, mode) :

        super (Skeleton, self).__init__ (name, input_file, mode, ofile=None)


    # --------------------------------------------------------------------------
    #
    def generate_workloads (self) :
        """
        based on the skeleton description (input_file) and type (mode), create
        a skeleton, and from that create a radical.owms.Workload for each stage -- that
        list of workloads is then returned
        """

        # Generate a skeleton.
        generated = super(Skeleton, self).generate ()
        print 'generated: %s' % generated

        # Prepare the input files for each stage of the skeleton.
        # WARNING: script names are hard-coded into the Skeleton module.
        if  not self.stagelist :
            raise RuntimeError ("Empty stagelist, Skeleton.generate() failed")

        for skeleton_stage in self.stagelist :
            # FIXME: maybe we should execute the content of the script line by
            # line, for better tracing / error reporting?
            shell_script = '/bin/sh %s_prepare.sh' % (skeleton_stage.name)
            print 'executing %s' % shell_script
            subprocess.check_call (shell_script, shell=True)


        """
        Set the executable and its arguments for each task of a skeleton.
        Note: This is a hack. It lifts part of the skeleton code.
        Note: This is a hack. It lifts part of the wmanager code.
        """

        workloads = list()

        for skeleton_stage in self.stagelist:

            stage_workload = radical.owms.Workload ()

            print skeleton_stage
            for skeleton_task in skeleton_stage.tasklist:

                # add execuable and args
                self._complete_skeleton_task (skeleton_task)

                # convert to radical.owms task description, and add to workload
                td = radical.owms.TaskDescription ()

                td.tag               = skeleton_task.taskid
                td.executable        = skeleton_task.executable
                td.arguments         = skeleton_task.arguments

                stage_workload.add_task (td)


            # stage done -- add resulting stage workload (register first)
            radical.owms.WorkloadManager.register_workload (stage_workload)
            workloads.append (stage_workload)

        # all stages done
        return workloads


    # --------------------------------------------------------------------------
    #
    def _complete_skeleton_task (self, skeleton_task) :

        # FIXME: The pwd use is an hack. Without it, BJ will not
        # find the task.stage.sh script.
        skeleton_task.executable  = 'pwd; %s.sh'    % (skeleton_task.stage)

        # duration
        skeleton_task.arguments   = []
        skeleton_task.arguments.append (skeleton_task.length.strip('s'))

        # input files
        for i in skeleton_task.inputlist:

            inputdir = ""
            words    = i.name.split ('_')
            
            for word in words[:-1]:
                inputdir += "%s_" % word
            
            inputdir = inputdir.strip ('_')    
            
            skeleton_task.arguments.append ('%s/%s' % (inputdir, i.name))

        # output files and size
        for o in skeleton_task.outputlist:

            skeleton_task.arguments.append ("%s/%s" % (skeleton_task.outputdir, o.name))

            # This might be a bug - do we have a size for every output
            # file? If so, the bash script (executable) will not work.
            skeleton_task.arguments.append (o.size)

        
# ------------------------------------------------------------------------------

