
import radical.utils.testing as rut

import troy

# ------------------------------------------------------------------------------
#
def test_pilot_inspection () :
    """ test pilot inspection """

    # we first need to create a pilot to inspect -- which means we need to
    # create an overlay.  Use the configured one... 
    test_conf    = rut.get_test_config ()

    # --------------------------------------------------------------------------

    overlay_dict = test_conf.overlay_dict
    overlay      = troy.Overlay ({troy.CORES : 1})

    if  not 'pilots' in overlay_dict :
        assert False, "no pilots in overlay dict" 

    if  not len(overlay_dict['pilots']) :
        assert False, "zero pilots in overlay dict" 

    pilot = None
    for pilot_dict in overlay_dict['pilots'] :
        pilot_description = troy.PilotDescription (pilot_dict)
        pilot             = troy.Pilot (pilot_description)
        overlay._add_pilot (pilot)

    troy.OverlayManager.register_overlay (overlay)

    overlay_mgr = troy.OverlayManager ()
    overlay_mgr.translate_overlay (overlay.id)
    overlay_mgr.schedule_overlay  (overlay.id)
    overlay_mgr.provision_overlay (overlay.id)

    # --------------------------------------------------------------------------


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
    

    # now we can try to inspect it:
    assert pilot
    assert (str(pilot.resource) == 'fork://localhost'), "%s != 'fork://localhost'" % pilot.resource
    assert (str(pilot.size)  == '2')                  , "%s != '2'"                % pilot.size  
    assert (len(pilot.units) ==  1 )                  , "%d !=  1"                 % len (pilot.units)
    print pilot.units
    assert (None == pilot.processes_per_node)
    assert (None == pilot.working_directory)
    assert (None == pilot.project)
    assert (None == pilot.queue)
    assert (None == pilot.wall_time_limit)
    assert (None == pilot.affinity_datacenter_label)
    assert (None == pilot.affinity_machine_label)

    workload_mgr.cancel_workload (workload.id)   # same as workload.cancel ()
    overlay_mgr .cancel_overlay  (overlay.id)



