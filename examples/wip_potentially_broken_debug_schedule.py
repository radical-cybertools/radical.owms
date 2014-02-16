
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
import random 
# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    radicalists = ['Shantenu Jha',     'Andre Merzky',       'Ole Weidner',
                   'Andre Luckow',     'Matteo Turilli',     'Melissa Romanus'
                   'Ashley Zebrowski', 'Dinesh Ganapathi',   'Mark Santcroos',
                   'Antons Treikalis', 'Jeffery Rabinowitz', 'Patrick Gray',
                  'Vishal Shah',      'Radicalobot']

    random.seed(1)
    for i in range(1):
        run_start_time=time.time()

        #{'default_overlay_translator' : {'pilot_size': '1'}
        #{'concurrent_planner' : {'concurrency' : '1'},
        session = troy.Session ({'default_overlay_translator' :
                                     {'max_pilot_size': '1'}}
                                )

        # Responsible for application workload
        workload_mgr = troy.WorkloadManager(scheduler='ttc_load_balancing',
                                            session=session)

        # Responsible for managing the pilot overlay
        #overlay_mgr = troy.OverlayManager()
        overlay_mgr = troy.OverlayManager (translator="max_pilot_size",
                                           session=session
                                           )
        # Planning makes initial mapping of workload to overlay
        planner = troy.Planner('maxcores',
                               session=session)


        # TROY data structure that holds the tasks and their relations
        #workload = troy.Workload()
        workload_id = workload_mgr.create_workload ()
        workload    = workload_mgr.get_workload    (workload_id)

        # Create a task for every radicalist
        for r in radicalists:
            task_descr            = troy.TaskDescription()
            task_descr.tag        = "%s" % r

            task_descr.executable = '/bin/sleep'
            task_descr.arguments  = [str(random.randint(1,10))]
            task_descr.walltime = random.randint(1,10) # in seconds

            task_id = workload.add_task(task_descr)

        # combine or split tasks in te workload
        planner.expand_workload(workload.id)

        # Initial description of the overlay based on the workload
        overlay_descr = planner.derive_overlay (workload_id)

        overlay_id = overlay_mgr.create_overlay (overlay_descr)

        # Translate 1 workload into N ComputeUnits and N DataUnits
        workload_mgr.translate_workload(workload.id, overlay_id)

        # Translate 1 Overlay description into N Pilot Descriptions
        overlay_mgr.translate_overlay(overlay_id)

        # Schedule the workload onto the overlay
        # Early binding assumes the overlay is not yet scheduled.
        
        schedule_request_start_time = time.time()
        workload_mgr.bind_workload (workload.id, overlay_id,
                                    bind_mode=troy.EARLY)
        schedule_request_end_time   = time.time()

        # Decide which resources to use for constructing the overlay
        overlay_mgr.schedule_overlay(overlay_id)

        # Instantiate Pilots on specified resources
        overlay_mgr.provision_overlay(overlay_id)

        # Execute the ComputeUnits on the Pilots
        workload_mgr.dispatch_workload(workload.id, overlay_id)

        # Of course nothing will fail due to TROY's magic robustness and
        # and we therefore just wait until its done!
        while workload.state not in [troy.DONE, troy.FAILED]:
            troy._logger.info ("whats up, buddy? (workload state: %s)" % workload.state)
            time.sleep(1)

        troy._logger.info ("ok, buddy, lets see what you got (workload state: %s)" % workload.state)

        if workload.state == troy.DONE :
            troy._logger.info ("game over")
        else :
            troy._logger.info ("you lose")
        run_end_time=time.time()

        workload_mgr.cancel_workload (workload.id)   # same as workload.cancel ()
        overlay_mgr .cancel_overlay  (overlay_id)

        print "########################################"
        print "run stats"
        print "########################################"
        print "This run's total time:", run_end_time - run_start_time
        print "This run's time spent scheduling:", schedule_request_end_time - schedule_request_start_time
