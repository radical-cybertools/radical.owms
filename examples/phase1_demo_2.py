
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


"""
Demo application for 1 feb 2014 - Bag of Task (BoT)
"""

import sys
import time
import troy
import getpass


PLUGIN_PLANNER              = 'concurrency'
PLUGIN_OVERLAY_SCHEDULER    = troy.AUTOMATIC
PLUGIN_OVERLAY_TRANSLATOR   = troy.AUTOMATIC
PLUGIN_WORKLOAD_SCHEDULER   = troy.AUTOMATIC
PLUGIN_WORKLOAD_DISPATCHER  = troy.AUTOMATIC # 'sinon'


# ------------------------------------------------------------------------------
def create_task_description (r, msg) :
    """
    litte helper which creates a task description for a radical member greeting
    """

    task_descr            = troy.TaskDescription ()
    task_descr.tag        = "%s" % r
    task_descr.executable = '/bin/echo'
    task_descr.arguments  = ['Hello', msg, r, '!']

    return task_descr


# ------------------------------------------------------------------------------
#
#
#
if __name__ == '__main__' :

    radical_students = ['Melissa Romanus',  'Ashley Zebrowski',   'Dinesh Ganapathi',   
                        'Mark Santcroos',   'Antons Treikalis',   'Jeffery Rabinowitz', 
                        'Patrick Gray',     'Vishal Shah',        'Radicalobot']

    radical_oldfarts = ['Shantenu Jha',     'Andre Merzky',       'Ole Weidner',
                        'Andre Luckow',     'Matteo Turilli']

    # create a session with custom config options
    session = troy.Session ({'concurrency_planner' : {'concurrency' : '80'}})

    # create planner, overlay and workload manager, with plugins as configured
    planner      = troy.Planner         (planner     = PLUGIN_PLANNER            ,
                                         session     = session                   )
    workload_mgr = troy.WorkloadManager (scheduler   = PLUGIN_WORKLOAD_SCHEDULER , 
                                         dispatcher  = PLUGIN_WORKLOAD_DISPATCHER,
                                         session     = session                   )
    overlay_mgr  = troy.OverlayManager  (scheduler   = PLUGIN_OVERLAY_SCHEDULER  ,
                                         translator  = PLUGIN_OVERLAY_TRANSLATOR ,
                                         session     = session                   )


    # --------------------------------------------------------------------------
    # Create the student workload first.  Makes sense, amiright?
    # Create two task for every radical student.  They love getting more tasks!
    workload_id_1 = workload_mgr.create_workload ()
    workload_1    = workload_mgr.get_workload    (workload_id_1)

    for r in radical_students :
        workload_1.add_task (create_task_description (r+'_1', 'student       '))
        workload_1.add_task (create_task_description (r+'_2', 'future oldfart'))


    # Initial description of the overlay based on the workload, and translate the
    # overlay into N pilot descriptions.
    overlay_descr = planner.derive_overlay     (workload_id_1)
    overlay_id    = overlay_mgr.create_overlay (overlay_descr)

    # make sure the overlay is properly represented by pilots
    overlay_mgr.translate_overlay   (overlay_id)


    # Translate 1 workload into N tasks and then M ComputeUnits, and bind them 
    # to specific pilots (which are not yet running, thus early binding)
    planner.expand_workload         (workload_id_1)
    workload_mgr.translate_workload (workload_id_1, overlay_id)
    workload_mgr.bind_workload      (workload_id_1, overlay_id, bind_mode=troy.EARLY)

    # Schedule pilots on the set of target resources, then instantiate Pilots as
    # scheduled
    overlay_mgr.schedule_overlay   (overlay_id)
    overlay_mgr.provision_overlay  (overlay_id)

    # ready to dispatch first workload on the overlay
    workload_mgr.dispatch_workload (workload_id_1, overlay_id)


    # --------------------------------------------------------------------------
    # Now take care of the oldfart workload -- not so many tasks for the old
    # people, and we lazily reuse the same overlay -- which is running, so,
    # late binding in this case.
    workload_id_2 = workload_mgr.create_workload ()
    workload_2    = workload_mgr.get_workload    (workload_id_2)

    for r in radical_oldfarts :
        workload_2.add_task (create_task_description (r, 'oldfart       '))


    # Translate expand, translate and bind workload again, and immediately
    # dispatch it, too.  We could have used
    # different plugins here...
    planner.expand_workload         (workload_id_2)
    workload_mgr.translate_workload (workload_id_2, overlay_id)
    workload_mgr.bind_workload      (workload_id_2, overlay_id, bind_mode=troy.LATE)
    workload_mgr.dispatch_workload  (workload_id_2, overlay_id)


    # --------------------------------------------------------------------------
    # Of course nothing will fail due to TROY's magic robustness and
    # and we therefore just wait until its done!
    state_1 = workload_1.state
    state_2 = workload_2.state

    while state_1 not in [troy.DONE, troy.FAILED] or \
          state_2 not in [troy.DONE, troy.FAILED] :

        troy._logger.info  ("workload_1 state: %s)" % state_1)
        troy._logger.info  ("workload_2 state: %s)" % state_2)

        state_1 = workload_1.state
        state_2 = workload_2.state

        time.sleep (1)


    # 'analyse' the results
    if workload_1.state == troy.DONE and \
       workload_2.state == troy.DONE : 
        troy._logger.info  ("workload_1 done")
        troy._logger.info  ("workload_2 done")

    else :
        troy._logger.error ("workload(s) failed!")
        troy._logger.info  ("workload_1 state: %s)" % workload_1.state)
        troy._logger.info  ("workload_2 state: %s)" % workload_2.state)

    # --------------------------------------------------------------------------
    # We are done -- clean up
    workload_mgr.cancel_workload (workload_id_1)
    workload_mgr.cancel_workload (workload_id_2)
    overlay_mgr .cancel_overlay  (overlay_id)


    # --------------------------------------------------------------------------

