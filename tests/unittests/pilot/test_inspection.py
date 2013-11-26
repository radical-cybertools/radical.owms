
import time
import radical.utils.testing as rut

from   troy.constants import *
import troy

# ------------------------------------------------------------------------------
#
def test_pilot_inspection () :
    """ test pilot inspection """

    # we first need to create a pilot to inspect -- which means we need to
    # create an overlay.  Use the configured one... 
    test_conf    = rut.get_test_config ()

    # --------------------------------------------------------------------------
    #
    # prepare an overlay, and get it into a state where inspection is getting
    # interesting
    #

    overlay_dict = test_conf.overlay_dict
    overlay      = troy.Overlay ({troy.CORES : 1})

    if  not 'pilots' in overlay_dict :
        assert False, "no pilots in overlay dict" 

    if  not len(overlay_dict['pilots']) :
        assert False, "zero pilots in overlay dict" 

    for pilot_dict in overlay_dict['pilots'] :
        pilot_description = troy.PilotDescription (pilot_dict)
        overlay._add_pilot (pilot_description)

    troy.OverlayManager.register_overlay (overlay)

    overlay_mgr = troy.OverlayManager ()
    overlay_mgr.translate_overlay (overlay.id)
    overlay_mgr.schedule_overlay  (overlay.id)
    overlay_mgr.provision_overlay (overlay.id)


    # --------------------------------------------------------------------------
    #
    # prepare an workload, and get it into a state where inspection is getting
    # interesting
    #

    workload_dict = test_conf.workload_dict
    workload      = troy.Workload ()

    if  not 'tasks' in workload_dict :
        assert False, "no tasks in workload dict" 

    if  not len(workload_dict['tasks']) :
        assert False, "zero tasks in workload dict" 

    for task_dict in workload_dict['tasks'] :
        task_description = troy.TaskDescription (task_dict)
        workload.add_task (task_description)

    troy.WorkloadManager.register_workload (workload)


    workload_mgr = troy.WorkloadManager ()
    workload_mgr.translate_workload(workload.id, overlay.id)
    workload_mgr.bind_workload     (workload.id, overlay.id,
                                    bind_mode=troy.LATE)
    workload_mgr.dispatch_workload (workload.id, overlay.id)


    # --------------------------------------------------------------------------
    #
    # inspect the overlay
    #
    assert (overlay)
    assert (overlay.state == PROVISIONED),   "%s != Provisioned" % overlay.state
    assert ('cores' in overlay.description), "'cores' not in %s" % overlay.description
    assert (overlay.description.cores == 1), "%s != in %s"       % overlay.description.cores
    assert (len(overlay.pilots) == 3)      , "%s != %s"          % (len(overlay.pilots), 3)

    # --------------------------------------------------------------------------
    #
    # inspect a pilot
    #
    pilot_id = overlay.pilots.keys ()[1]
    pilot    = overlay.pilots[pilot_id]
    assert (pilot)
    assert (pilot.state == PROVISIONED)               , "%s != Provisioned'"         % pilot.state
    assert (pilot.description)                        , "no description (%s)"        % pilot.description
    assert (str(pilot.resource) == 'fork://localhost'), "%s != 'fork://localhost'"   % pilot.resource
    assert (str(pilot.size)  == '2')                  , "%s != '2'"                  % pilot.size  
    assert (len(pilot.units) ==  1 )                  , "%d !=  1"                   % len (pilot.units)
    assert (pilot.native_id)                          , "no native id"
    assert (pilot.native_description)                 , "no native description"
    assert (pilot.start_time)                         , "no start_time"
    assert (pilot.last_contact)                       , "no last contact"
    assert (pilot.end_queue_time)                     , "no end_queue_time"
    assert (pilot.processes_per_node)                 , "no processes_per_node"
    assert (pilot.slots)                              , "no slots"
  # assert (pilot.working_directory)                  , "no working_directory"
    assert (pilot.service_url)                        , "no service_url"

    # --------------------------------------------------------------------------
    #
    # inspect a unit on that pilot
    #
    unit_id = pilot.units.keys ()[0]
    unit    = pilot.units[unit_id]
    assert unit
    time.sleep (1) # get the unit running *fingers crossed*
    assert (unit.state    == RUNNING),     "%s != RUNNING" % unit.state
    assert (unit.pilot_id == pilot.id),    "%s != %s"      % (unit.pilot_id, pilot.id)

    # --------------------------------------------------------------------------
    #
    # inspect the workload
    #
    assert (workload)
    assert (workload.state == DISPATCHED), "%s != Dispatched" % workload.state
    assert (len(workload.tasks) == 2),     "%s != %s" % (len(workload.tasks),     2)
    assert (len(workload.relations) == 0), "%s != %s" % (len(workload.relations), 0)

    # --------------------------------------------------------------------------
    #
    # inspect a task
    #
    task_id = workload.tasks.keys()[1]
    task    = workload.tasks[task_id]
    assert (task)
    assert (task.tag                    == "task_2"),       "%s != 'task_2'"     % task.tag
    assert (task.state                  == DISPATCHED),     "%s != Dispatched"   % task.state
    assert (task.description.executable == "/bin/sleep"),   "%s != '/bin/sleep'" % task.description.executable
    assert (len(task.units) == 1),         "%s != %s" % (len(task.units),     1)


    # --------------------------------------------------------------------------
    #
    # inspect a unit (this time from task, not from pilot!)
    #
    unit_id = task.units.keys()[0]
    unit    = task.units[unit_id]
    assert (unit)
    assert (unit.state                  == RUNNING     ),   "%s != Dispatched"   % unit.state
    assert (unit.description.executable == "/bin/sleep"),   "%s != '/bin/sleep'" % unit.description.executable
    assert (unit.task.id                == task.id     ),   "%s != %s"           % (unit.task.id, task.id)
    assert (unit.native_id                             ),   "no native id"
    assert (unit.executable                            ),   "no executable"
    assert (unit.slots                                 ),   "no slots"
    assert (unit.start_time                            ),   "no start_time"
    assert (unit.agent_start_time                      ),   "no agent_start_time"
    assert (unit.tag == task.tag                       ),   "%s != %s"           % (unit.tag, task.tag)
    assert (unit.arguments                             ),   "no arguments"
    assert (unit.job_id                                ),   "no job_id"
    assert (unit.end_queue_time                        ),   "no end_queue_time"

    # --------------------------------------------------------------------------
    #
    # bye, bye, bye Junimond ...
    #
    workload_mgr.cancel_workload (workload.id)   # same as workload.cancel ()
    overlay_mgr .cancel_overlay  (overlay.id)



