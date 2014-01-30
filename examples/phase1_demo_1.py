
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
    radicalists = ['Shantenu Jha',     'Andre Merzky',       'Ole Weidner']

    # Responsible for application workload
    workload_mgr = troy.WorkloadManager (dispatcher='sinon')

    # Responsible for managing the pilot overlay
    overlay_mgr = troy.OverlayManager (provisioner=troy.AUTOMATIC)

    # Planning makes initial mapping of workload to overlay
    planner = troy.Planner('maxcores')
    #planner = troy.Planner('bundles')

    # TROY data structure that holds the tasks and their relations
    workload_id = workload_mgr.create_workload ()
    workload    = workload_mgr.get_workload    (workload_id)

    # Create a task for every radicalist
    for r in radicalists:
        task_descr            = troy.TaskDescription()
        task_descr.tag        = "%s" % r

        task_descr.executable = '/bin/echo'
        task_descr.arguments  = ['Hello World, ', r, '!']

        task_id = workload.add_task(task_descr)

        # Tasks are uncoupled so no relationships are specified

    # combine or split tasks in te workload
    planner.expand_workload(workload_id)

    # Initial description of the overlay based on the workload
    overlay_descr = planner.derive_overlay (workload_id)

    # get overlay for that description
    overlay_id = overlay_mgr.create_overlay (overlay_descr)

    # Translate 1 workload into N ComputeUnits and N DataUnits
    workload_mgr.translate_workload(workload_id, overlay_id)

    # Translate 1 Overlay description into N Pilot Descriptions
    overlay_mgr.translate_overlay(overlay_id)

    # Schedule the workload onto the overlay
    # Early binding assumes the overlay is not yet scheduled.
    workload_mgr.bind_workload (workload_id, overlay_id,
                                bind_mode=troy.EARLY)

    # Decide which resources to use for constructing the overlay
    overlay_mgr.schedule_overlay(overlay_id)

    # Instantiate Pilots on specified resources
    overlay_mgr.provision_overlay(overlay_id)

    # Execute the ComputeUnits on the Pilots
    workload_mgr.dispatch_workload (workload_id, overlay_id)

    # Of course nothing will fail due to TROY's magic robustness and
    # and we therefore just wait until its done!
    while workload.state not in [troy.DONE, troy.FAILED]:
        troy._logger.info ("whats up, buddy? (workload state: %s)" % workload.state)
        time.sleep(1)

    if 'merzky' in getpass.getuser():
        troy._logger.info ("ok, German Skripter, lets see what you got (workload state: %s)" % workload.state)
    else:
        troy._logger.info ("ok, buddy, lets see what you got (workload state: %s)" % workload.state)

    if workload.state == troy.DONE :
        troy._logger.info ("game over")
    else :
        troy._logger.info ("game over -- play again?")

    workload_mgr.cancel_workload (workload_id)   # same as workload.cancel ()
    overlay_mgr .cancel_overlay  (overlay_id)


    for t_id in workload.tasks.keys():
        print "t_id", t_id
        task = workload.tasks[t_id]
        for u_id in task.units.keys():
            print "u_id", u_id
            unit = task.units[u_id]
            print unit.description

        #print workload.units[t].description
        

        #print t.tasks
        #print t.description
        #for u in t.units:
        #print j
        #print j.tasks()

    workload_mgr.cancel_workload (workload.id)   # same as workload.cancel ()
    overlay_mgr .cancel_overlay  (overlay_id)
