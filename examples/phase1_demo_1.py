
__author__    = "RADICAL Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


"""
    Demo application for 1 feb 2014
    - Bag of Task (BoT)

"""

import time
import radical.owms
import getpass

# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    session = radical.owms.Session ()

    radicalists = ['Shantenu Jha',     'Andre Merzky',       'Ole Weidner',
                   'Andre Luckow',     'Matteo Turilli',     'Melissa Romanus',
                   'Ashley Zebrowski', 'Dinesh Ganapathi',   'Mark Santcroos',
                   'Antons Treikalis', 'Jeffery Rabinowitz', 'Patrick Gray',
                   'Vishal Shah',      'Radicalobot']
    radicalists = ['Shantenu Jha',     'Andre Merzky',       'Ole Weidner']

    session = radical.owms.Session ()

    # Responsible for application workload
    workload_mgr = radical.owms.WorkloadManager (session)

    # Responsible for managing the pilot overlay
    overlay_mgr = radical.owms.OverlayManager (session)

    # Planning makes initial mapping of workload to overlay
    planner = radical.owms.Planner (session)

    # radical.owms data structure that holds the tasks and their relations
    workload = radical.owms.Workload (session)

    # Create a task for every radicalist
    for r in radicalists:
        task_descr            = radical.owms.TaskDescription()
        task_descr.tag        = "%s" % r

        task_descr.executable = '/bin/echo'
        task_descr.arguments  = ['Hello World, ', r, '!']

        task_id = workload.add_task(task_descr)

        # Tasks are uncoupled so no relationships are specified

    # combine or split tasks in te workload
    workload_mgr.expand_workload(workload.id)

    # Initial description of the overlay based on the workload
    overlay_descr = planner.derive_overlay (workload.id)

    # get overlay for that description
    overlay = radical.owms.Overlay (session, overlay_descr)

    # Translate 1 workload into N ComputeUnits and N DataUnits
    workload_mgr.translate_workload(workload.id, overlay.id)

    # Translate 1 Overlay description into N Pilot Descriptions
    overlay_mgr.translate_overlay(overlay.id)

    # Schedule the workload onto the overlay
    # Early binding assumes the overlay is not yet scheduled.
    workload_mgr.bind_workload (workload.id, overlay.id,
                                bind_mode=radical.owms.EARLY)

    # Decide which resources to use for constructing the overlay
    overlay_mgr.schedule_overlay(overlay.id)

    # Instantiate Pilots on specified resources
    overlay_mgr.provision_overlay(overlay.id)

    # Execute the ComputeUnits on the Pilots
    workload_mgr.dispatch_workload (workload.id, overlay.id)

    # Of course nothing will fail due to RADICAL-OWMS's magic robustness and
    # and we therefore just wait until its done!
    while workload.state not in [radical.owms.DONE, radical.owms.FAILED]:
        radical.owms._logger.info ("whats up, buddy? (workload state: %s)" % workload.state)
        time.sleep(1)

    radical.owms._logger.info ("ok, buddy, lets see what you got (workload state: %s)" % workload.state)

    if workload.state == radical.owms.DONE :
        radical.owms._logger.info ("game over")
    else :
        radical.owms._logger.info ("game over -- play again?")

    workload_mgr.cancel_workload (workload.id)   # same as workload.cancel ()
    overlay_mgr .cancel_overlay  (overlay.id)


    for t_id in workload.tasks.keys():
        print "t_id", t_id
        task = workload.tasks[t_id]
        for u_id in task.units.keys():
            print "u_id", u_id
            unit = task.units[u_id]
            print unit.as_dict()

    workload_mgr.cancel_workload (workload.id)   # same as workload.cancel ()
    overlay_mgr .cancel_overlay  (overlay.id)

