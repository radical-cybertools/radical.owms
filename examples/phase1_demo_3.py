
__author__    = "RADICAL Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


"""
    Demo application for 1 feb 2014
    - Bag of Task (BoT)

"""

import os
import time
import radical.owms
import getpass

# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    # set up local pwd
    try :
        os.mkdir ("/tmp/radical_owms_demo/")
    except :
        pass # might exist

    os.chdir ("/tmp/radical_owms_demo/")

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

    session = radical.owms.Session (user_cfg = {
        'planner' : {
            'derive' : {
                'concurrent' : {
                    'concurrency' : 50
                    }
                }
            }
        })

    # Responsible for application workload
    workload_mgr = radical.owms.WorkloadManager (session)

    # Responsible for managing the pilot overlay
    overlay_mgr = radical.owms.OverlayManager (session)

    # Planning makes initial mapping of workload to overlay
    planner = radical.owms.Planner (session)

    # Create a task for every radicalist
    task_descriptions = list()
    for r in radicalists:
        fin  = fnames[r] + '.in'
        fout = fnames[r] + '.out'

        task_descr                   = radical.owms.TaskDescription()
        task_descr.tag               = "%s" % r
        task_descr.walltime          = len(r)
        task_descr.executable        = '/bin/cp'
        task_descr.arguments         = ['input', 'output']

        task_descr.inputs            = ["%s > %s" % (fin,  'input')]
        task_descr.outputs           = ["%s < %s" % (fout, 'output')]
        task_descr.working_directory = "%%(home)s/radical_owms_demo/tasks/%s/" % fnames[r]

        print task_descr

        task_descriptions.append (task_descr)


    workload = radical.owms.Workload (session, task_descriptions)

    # execute the workload with the given execution strategy
    planner.execute_workload (workload.id)

    # Wohooo!  Magic has happened!

