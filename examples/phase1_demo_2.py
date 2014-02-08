
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


PLUGIN_PLANNER              = 'concurrent'
PLUGIN_OVERLAY_SCHEDULER    = 'round_robin'
PLUGIN_OVERLAY_TRANSLATOR   = troy.AUTOMATIC
PLUGIN_OVERLAY_PROVISIONER  = 'local'
PLUGIN_WORKLOAD_SCHEDULER   = troy.AUTOMATIC
PLUGIN_WORKLOAD_DISPATCHER  = 'local' # troy.AUTOMATIC # 'sinon'

WORKDIR                     = '/N/u/merzky/troy_demo/'
WORKDIR                     = '/home/merzky/troy_demo/'


# ------------------------------------------------------------------------------
def create_task_description (r, msg) :
    """
    litte helper which creates a task description for a radical member greeting
    """

    task_descr                   = troy.TaskDescription ()
    task_descr.tag               = "%s" % r
    task_descr.executable        = '/bin/echo'
    task_descr.arguments         = ['Hello', msg, r, '!']
    task_descr.working_directory = WORKDIR

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

    radical_students = ['Melissa Romanus',  'Ashley Zebrowski',   'Dinesh Ganapathi']
    radical_oldfarts = ['Shantenu Jha',     'Andre Merzky',       'Ole Weidner']

    # create a session with custom config options
    session = troy.Session ({'concurrent_planner' : {'concurrency' : '100'}})

    # create planner, overlay and workload manager, with plugins as configured
    planner      = troy.Planner         (session     = session                   ,
                                         planner     = PLUGIN_PLANNER            )
    workload_mgr = troy.WorkloadManager (session     = session                   ,
                                         scheduler   = PLUGIN_WORKLOAD_SCHEDULER , 
                                         dispatcher  = PLUGIN_WORKLOAD_DISPATCHER)
    overlay_mgr  = troy.OverlayManager  (session     = session                   ,
                                         scheduler   = PLUGIN_OVERLAY_SCHEDULER  ,
                                         translator  = PLUGIN_OVERLAY_TRANSLATOR ,
                                         provisioner = PLUGIN_OVERLAY_PROVISIONER)


    # --------------------------------------------------------------------------
    # Create the student workload first.  Makes sense, amiright?
    # Create two task for every radical student.  They love getting more tasks!
    workload_1 = troy.Workload (session=session)

    for r in radical_students :
        workload_1.add_task (create_task_description (r+'_1', 'student       '))
        workload_1.add_task (create_task_description (r+'_2', 'future oldfart'))


    # Initial description of the overlay based on the workload, and translate the
    # overlay into N pilot descriptions.
    overlay_descr = planner.derive_overlay (workload_1.id)
    overlay       = troy.Overlay           (session, overlay_descr)

    # make sure the overlay is properly represented by pilots
    overlay_mgr.translate_overlay   (overlay.id)


    # Translate 1 workload into N tasks and then M ComputeUnits, and bind them 
    # to specific pilots (which are not yet running, thus early binding)
    planner.expand_workload         (workload_1.id)
    workload_mgr.translate_workload (workload_1.id, overlay.id)
    workload_mgr.bind_workload      (workload_1.id, overlay.id, bind_mode=troy.EARLY)

    # Schedule pilots on the set of target resources, then instantiate Pilots as
    # scheduled
    overlay_mgr.schedule_overlay   (overlay.id)
    overlay_mgr.provision_overlay  (overlay.id)

    # ready to dispatch first workload on the overlay
    workload_mgr.dispatch_workload (workload_1.id, overlay.id)


    # --------------------------------------------------------------------------
    # Now take care of the oldfart workload -- not so many tasks for the old
    # people, and we lazily reuse the same overlay -- which is running, so,
    # late binding in this case.
    workload_2 = troy.Workload (session)

    for r in radical_oldfarts :
        workload_2.add_task (create_task_description (r, 'oldfart       '))


    # Translate expand, translate and bind workload again, and immediately
    # dispatch it, too.  We could have used
    # different plugins here...
    planner.expand_workload         (workload_2.id)
    workload_mgr.translate_workload (workload_2.id, overlay.id)
    workload_mgr.bind_workload      (workload_2.id, overlay.id, bind_mode=troy.LATE)
    workload_mgr.dispatch_workload  (workload_2.id, overlay.id)


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
    # We are done -- save traces
  # session     .store_workload_trace (               target='stdout')
  # overlay_mgr .store_overlay _trace (overlay.id   , target='stdout')
  # workload_mgr.store_workload_trace (workload_1.id, target='stdout')
  # workload_mgr.store_workload_trace (workload_2.id, target='stdout')

  # workload_mgr.timed_dump ()
  # workload_mgr.timed_store ('mongodb://localhost/timing/')
    session.timed_dump ()
    session.timed_store ('mongodb://localhost/timing/')


    # --------------------------------------------------------------------------
    # We are done -- clean up
    workload_mgr.cancel_workload (workload_1.id)
    workload_mgr.cancel_workload (workload_2.id)
    overlay_mgr .cancel_overlay  (overlay.id)


    # --------------------------------------------------------------------------

