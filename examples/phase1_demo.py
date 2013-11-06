
__author__ = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__ = "MIT"


"""
    Demo application for 1 feb 2014
    - Bag of Task (BoT)

"""

import time
import troy

# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    radicalists = ['Shantenu Jha', 'Andre Merzky', 'Ole Weidner',
                   'Andre Luckow', 'Matteo Turilli', 'Melissa Romanus',
                   'Ashley Zebrowski', 'Dinesh Ganapathi', 'Mark Santcroos',
                   'Antons Treikalis', 'Jeffery Rabinowitz', 'Patrick Gray',
                   'Vishal Shah']

    # Responsible for application workload
    workload_mgr = troy.WorkloadManager()
    # Responsible for managing the pilot overlay
    overlay_mgr = troy.OverlayManager()

    # Planning makes initial mapping of workload to overlay
    planner = troy.Planner()

    # TROY data structure that holds the tasks and their relations
    workload = troy.Workload()

    # Create a task for every radicalist
    for r in radicalists:
        task_desc = troy.TaskDescription()
        task_desc.exe = '/bin/echo'
        task_desc.args = ['Hello World, ', r, '!']
        task_id = workload.add_task(task_desc)
        # Tasks are uncoupled so no relationships are specified

    # Register the workload so we can pass it by ID
    troy.WorkloadManager.register_workload(workload)

    # Initial description of the overlay based on the workload
    overlay_id = planner.derive_overlay(workload.id)

    # Translate 1 workload into N ComputeUnits and N DataUnits
    workload_mgr.translate_workload(workload.id, overlay_id)

    # Translate 1 Overlay description into N Pilot Descriptions
    overlay_mgr.translate_overlay(overlay_id)

    # Schedule the workload onto the overlay
    # Early binding assumes the overlay is not yet scheduled.
    workload_mgr.schedule_workload(workload.id, overlay_id,
                                   binding=troy.EARLY)

    # Decide which resources to use for constructing the overlay
    overlay_mgr.schedule_overlay(overlay_id)

    # Instantiate Pilots on specified resources
    overlay_mgr.provision_overlay(overlay_id)

    # Execute the ComputeUnits on the Pilots
    workload_mgr.dispatch_workload(workload.id, overlay_id)

    # Of course nothing will fail due to TROY's magic robustness and
    # and we therefore just wait until its done!
    while workload.state != troy.COMPLETED:
        time.sleep(5)