
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


"""
    Demo application for 1 feb 2014
    - Bag of Task (BoT)

"""

import time
import troy
import getpass

# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    radicalists = ['Shantenu Jha',     'Andre Merzky',       'Ole Weidner',
                   'Andre Luckow',     'Matteo Turilli',     'Melissa Romanus',
                   'Ashley Zebrowski', 'Dinesh Ganapathi',   'Mark Santcroos',
                   'Antons Treikalis', 'Jeffery Rabinowitz', 'Patrick Gray',
                   'Vishal Shah',      'Radicalobot']

    # Responsible for application workload
    workload_mgr = troy.WorkloadManager (dispatcher='local')

    # Responsible for managing the pilot overlay
    overlay_mgr = troy.OverlayManager (provisioner=troy.AUTOMATIC)

    # Planning makes initial mapping of workload to overlay
    planner = troy.Planner (planner=troy.AUTOMATIC)

    # TROY data structure that holds the tasks and their relations
    workload_id = workload_mgr.create_workload ()
    workload    = workload_mgr.get_workload    (workload_id)

    # Create a task for every radicalist
    for r in radicalists:
        task_descr            = troy.TaskDescription()
        task_descr.tag        = "%s" % r
        task_descr.executable = '/bin/echo'
        task_descr.arguments  = ['Hello World, ', r, '!']

        task_id = workload.add_task (task_descr)

    # execute the workload with the given execution strategy
    troy.execute_workload (workload_id, planner, overlay_mgr, workload_mgr, strategy='basic')

    # Wohooo!  Magic has happened!

