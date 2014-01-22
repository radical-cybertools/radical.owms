
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

    # create a data stager for all workloads
    stager = troy.DataStager ()

    radicalists = ['Shantenu Jha',     'Andre Merzky',       'Ole Weidner',
                   'Andre Luckow',     'Matteo Turilli',     'Melissa Romanus',
                   'Ashley Zebrowski', 'Dinesh Ganapathi',   'Mark Santcroos',
                   'Antons Treikalis', 'Jeffery Rabinowitz', 'Patrick Gray',
                   'Vishal Shah',      'Radicalobot']

    fnames = dict ()
    # prepare task input files for each task
    for r in radicalists :
        
        fnames[r] = r.replace(' ', '_').lower()
        tmp       = open ("%s.in" % fnames[r], "w")
        tmp.write   ("%s\n" % r)
        tmp.close   ()


    # Responsible for application workload
    workload_mgr = troy.WorkloadManager (dispatcher = 'local', 
                                         stager     = stager)  # this is actually the default

    # Responsible for managing the pilot overlay
    overlay_mgr = troy.OverlayManager (scheduler    = 'round_robin', 
                                       provisioner  = troy.AUTOMATIC)

    # Planning makes initial mapping of workload to overlay
    planner = troy.Planner (planner='concurrent')

    # Create a task for every radicalist
    task_descriptions = list()
    for r in radicalists:
        fin  = fnames[r] + '.in'
        fout = fnames[r] + '.out'

        task_descr                   = troy.TaskDescription()
        task_descr.tag               = "%s" % r
        task_descr.executable        = '/bin/cp'
        task_descr.arguments         = [fin, fout]

        task_descr.inputs            = [fin]
        task_descr.outputs           = [fout]
      # task_descr.working_directory = "/N/u/merzky/troy_demo/tasks/%s/" % fnames[r]
        task_descr.working_directory = "/tmp/troy_demo/tasks/%s/" % fnames[r]

        print task_descr

        task_descriptions.append (task_descr)


    workload_id = workload_mgr.create_workload (task_descriptions)

    # execute the workload with the given execution strategy
    troy.execute_workload (workload_id, planner, overlay_mgr, workload_mgr, strategy='basic')

    # Wohooo!  Magic has happened!

