
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


"""
    Demo application for 1 feb 2014
    - Bag of Task (BoT)

"""

import os
import time
import troy
import getpass

# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    # set up local pwd
    try :
        os.mkdir ("/tmp/troy_demo/")
    except :
        pass # might exist

    os.chdir ("/tmp/troy_demo/")

    radicalists = ['Shantenu Jha',     'Andre Merzky',       'Ole Weidner',
                   'Andre Luckow',     'Matteo Turilli',     'Melissa Romanus',
                   'Ashley Zebrowski', 'Dinesh Ganapathi',   'Mark Santcroos',
                   'Antons Treikalis', 'Jeffery Rabinowitz', 'Patrick Gray',
                   'Vishal Shah',      'Radicalobot']
    radicalists = ['Andre Merzky',     'Ole Weidner']

    fnames = dict ()
    # prepare task input files for each task
    for r in radicalists :
        
        fnames[r] = r.replace(' ', '_').lower()
        tmp       = open ("%s.in" % fnames[r], "w")
        tmp.write   ("%s\n" % r)
        tmp.close   ()

    session = troy.Session (user_cfg = {
        'planner' : {
            'derive' : {
                'concurrent' : {
                    'concurrency' : 50
                    }
                }
            }
        })

    # Responsible for application workload
    workload_mgr = troy.WorkloadManager (session)

    # Responsible for managing the pilot overlay
    overlay_mgr = troy.OverlayManager (session)

    # Planning makes initial mapping of workload to overlay
    planner = troy.Planner (session)

    # Create a task for every radicalist
    task_descriptions = list()
    for r in radicalists:
        fin  = fnames[r] + '.in'
        fout = fnames[r] + '.out'

        task_descr                   = troy.TaskDescription()
        task_descr.tag               = "%s" % r
        task_descr.walltime          = len(r)
        task_descr.executable        = '/bin/cp'
        task_descr.arguments         = ['input', 'output']

        task_descr.inputs            = ["%s > %s" % (fin,  'input')]
        task_descr.outputs           = ["%s < %s" % (fout, 'output')]
        task_descr.working_directory = "%%(home)s/troy_demo/tasks/%s/" % fnames[r]

        print task_descr

        task_descriptions.append (task_descr)


    workload = troy.Workload (session, task_descriptions)

    # execute the workload with the given execution strategy
    planner.execute_workload (workload.id)

    # Wohooo!  Magic has happened!

