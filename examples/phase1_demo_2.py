
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


"""
    Demo application for 1 feb 2014
    - Bag of Task (BoT)

"""

import sys
import time
import troy
import getpass

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

    # the troy session gives us access to the troy configuration
    session = troy.Session ()
    config  = session.cfg.get_config_as_dict ()

    if 'demo2' in config : demo_cfg = config['demo2']
    else                 : demo_cfg = dict ()

    # get plugin configuration
    planner_plugin = demo_cfg.get ('planner',             'default')
    osched_plugin  = demo_cfg.get ('overlay_scheduler',   'default')
    otrans_plugin  = demo_cfg.get ('overlay_translator',  'default')
    oprov_plugin   = demo_cfg.get ('overlay_provisioner', 'default')
    wsched_plugin  = demo_cfg.get ('workload_scheduler',  'default')
    wdisp_plugin   = demo_cfg.get ('workload_dispatcher', 'default')


    # create planner, overlay and workload manager, with plugins as above
    planner      = troy.Planner         (planner     = planner_plugin)
    overlay_mgr  = troy.OverlayManager  (scheduler   =  osched_plugin,
                                         translator  =  otrans_plugin, 
                                         provisioner =   oprov_plugin)
    workload_mgr = troy.WorkloadManager (scheduler   =  wsched_plugin, 
                                         dispatcher  =   wdisp_plugin)


    # --------------------------------------------------------------------------
    # Create the student workload first.  Makes sense, amiright?
    # Create two task for every radical student.  They love getting more tasks!
    workload_1 = troy.Workload ()

    for r in radical_students :
        workload_1.add_task (create_task_description (r+'_1', 'student       '))
        workload_1.add_task (create_task_description (r+'_2', 'future oldfart'))


    # Initial description of the overlay based on the workload, and translate the
    # overlay into N pilot descriptions.
    overlay_id = planner.derive_overlay (workload_1.id)
    overlay_mgr.translate_overlay       (overlay_id)


    # Translate 1 workload into N tasks and then M ComputeUnits, and bind them 
    # to specific pilots (which are not yet running, thus early binding)
    planner.expand_workload         (workload_1.id)
    workload_mgr.translate_workload (workload_1.id, overlay_id)
    workload_mgr.bind_workload      (workload_1.id, overlay_id, bind_mode=troy.EARLY)

    # Schedule pilots on the set of target resources, then instantiate Pilots as
    # scheduled
    overlay_mgr.schedule_overlay   (overlay_id)
    overlay_mgr.provision_overlay  (overlay_id)

    # ready to dispatch first workload on the overlay
    workload_mgr.dispatch_workload (workload_1.id, overlay_id)


    # --------------------------------------------------------------------------
    # Now take care of the oldfart workload -- not so many tasks for the old
    # people, and we lazily reuse the same overlay -- which is running, so,
    # late binding in this case.
    workload_2 = troy.Workload ()

    for r in radical_oldfarts :
        workload_2.add_task (create_task_description (r, 'oldfart       '))


    # Translate expand, translate and bind workload again, and immediately
    # dispatch it, too.  We could have used
    # different plugins here...
    planner.expand_workload         (workload_2.id)
    workload_mgr.translate_workload (workload_2.id, overlay_id)
    workload_mgr.bind_workload      (workload_2.id, overlay_id, bind_mode=troy.LATE)
    workload_mgr.dispatch_workload  (workload_2.id, overlay_id)


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
    workload_mgr.cancel_workload (workload_1.id)
    workload_mgr.cancel_workload (workload_2.id)
    overlay_mgr .cancel_overlay  (overlay_id)


    # --------------------------------------------------------------------------

