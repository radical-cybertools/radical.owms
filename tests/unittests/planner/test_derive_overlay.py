
__author__    = "Mark Santcroos"
__copyright__ = "Copyright 2013, RADICAL @ Rutgers"
__license__   = "MIT"


import pprint
import radical.utils.testing as rut

import troy


# ------------------------------------------------------------------------------
#
def test_derive_overlay():
    """
    test overlay derivation
    """
    tc = rut.get_test_config()
    wl_dict = tc.workload_dict

    wl = troy.Workload()
    planner = troy.Planner()
    pprint.pprint(wl_dict)

    if not 'tasks' in wl_dict:
        assert False, "no tasks in workload dict"

    if not len(wl_dict['tasks']):
        assert False, "zero tasks in workload dict"

    for task_dict in wl_dict['tasks']:
        task_description = troy.TaskDescription(task_dict)
        wl.add_task(task_description)

    for relation_dict in wl_dict['relations']:
        relation_description = troy.RelationDescription(relation_dict)
        wl.add_relation(relation_description)

    troy.WorkloadManager.register_workload(wl)

    overlay_id = planner.derive_overlay(wl.id)

    overlay = troy.OverlayManager.get_overlay(overlay_id)

    if  not overlay.description.cores :
        assert False, "No cores requested"

    if  not overlay.description.wall_time :
        assert False, "Walltime is zero"

