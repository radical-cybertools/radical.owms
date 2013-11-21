
import radical.utils.testing as rut

import troy

# ------------------------------------------------------------------------------
#
def test_pilot_inspection () :
    """ test pilot inspection """

    # we first need to create a pilot to inspect -- which means we need to
    # create an overlay.  Use the configured one... 
    test_donf    = rut.get_test_config ()
    overlay_dict = test_donf.overlay_dict
    overlay      = troy.Overlay ({troy.CORES : 1})

    if  not 'pilots' in overlay_dict :
        assert False, "no pilots in overlay dict" 

    if  not len(overlay_dict['pilots']) :
        assert False, "zero pilots in overlay dict" 

    for pilot_dict in overlay_dict['pilots'] :
        pilot_description = troy.PilotDescription (pilot_dict)
        pilot             = troy.Pilot (pilot_description)
        overlay._add_pilot (pilot)

    troy.OverlayManager.register_overlay (overlay)

    overlay_mgr = troy.OverlayManager ()
    overlay_mgr.translate_overlay (overlay.id)
    overlay_mgr.schedule_overlay  (overlay.id)
    overlay_mgr.provision_overlay (overlay.id)
    

    # now we can try to inspect it:
    assert (str(pilot.resource) == 'fork://localhost'), "%s != 'fork://localhost'" % pilot.resource
    assert (str(pilot.size) == '2')                   , "%s != '2'"                % pilot.size  
    assert (None == pilot.processes_per_node)
    assert (None == pilot.working_directory)
    assert (None == pilot.project)
    assert (None == pilot.queue)
    assert (None == pilot.wall_time_limit)
    assert (None == pilot.affinity_datacenter_label)
    assert (None == pilot.affinity_machine_label)

    overlay_mgr.cancel_overlay (overlay.id)


