
__author__    = "Mark Santcroos"
__copyright__ = "Copyright 2013, RADICAL @ Rutgers"
__license__   = "MIT"


import pprint
import radical.utils.testing as rut

import radical.owms


# ------------------------------------------------------------------------------
#
def test_derive_overlay():
    """
    test overlay derivation
    """
    tc = rut.get_test_config()
    wl_dict = tc.workload_dict

    wl = radical.owms.Workload()
    planner = radical.owms.Planner()
  # pprint.pprint(wl_dict)

    if not 'tasks' in wl_dict:
        assert False, "no tasks in workload dict"

    if not len(wl_dict['tasks']):
        assert False, "zero tasks in workload dict"

    for task_dict in wl_dict['tasks']:
        task_description = radical.owms.TaskDescription(task_dict)
        wl.add_task(task_description)

    for relation_dict in wl_dict['relations']:
        relation_description = radical.owms.RelationDescription(relation_dict)
        wl.add_relation(relation_description)

    overlay_id = planner.derive_overlay(wl.id)

    overlay = radical.owms.OverlayManager.get_overlay(overlay_id)

    if  not overlay.description.cores :
        assert False, "No cores requested"

    if  not overlay.description.wall_time :
        assert False, "Walltime is zero"

