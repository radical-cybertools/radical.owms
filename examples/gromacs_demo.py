
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
        os.mkdir("/tmp/troy_demo/")
    except :
        pass # might exist

    os.chdir("/tmp/troy_demo/")

    # create a data stager for all workloads
    stager = troy.DataStager()

    # Responsible for application workload
    workload_mgr = troy.WorkloadManager(dispatcher = 'bigjob_pilot',
                                        stager     = stager)  # this is actually the default

    # Responsible for managing the pilot overlay
    overlay_mgr = troy.OverlayManager(scheduler    = 'round_robin',
                                      provisioner  = troy.AUTOMATIC)

    # Planning makes initial mapping of workload to overlay
    planner = troy.Planner (planner='concurrent')

    # Create a task for every radicalist
    task_descriptions = list()
    steps = 256
    bagsize = 10
    for n in range(bagsize):

        task_descr                   = troy.TaskDescription()
        task_descr.tag               = "%d" % n
        task_descr.executable        = '/N/u/marksant/bin/mdrun'
        task_descr.arguments         = ['-nsteps', steps]

        task_descr.inputs            = ['topol.tpr']
        task_descr.outputs           = ['state.cpt', 'confout.gro', 'ener.edr', 'traj.trr', 'md.log']
        task_descr.working_directory = "/N/u/marksant/troy_demo/tasks/%d/" % n

        print task_descr

        task_descriptions.append(task_descr)

    workload_id = workload_mgr.create_workload(task_descriptions)

    # execute the workload with the given execution strategy
    troy.execute_workload(workload_id, planner, overlay_mgr, workload_mgr, strategy='basic')

    # Woohooo!  Magic has happened!
