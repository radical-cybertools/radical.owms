
__author__    = "Andre Merzky"
__copyright__ = "Copyright 2013, The SAGA Project"
__license__   = "MIT"


import pprint
import radical.utils as ru

import troy

# ------------------------------------------------------------------------------
#
def test_workload_create () :
    """ 
    test workload creation
    """
    tc = ru.get_test_config ()
    wl_dict = tc.workload_dict
    wl      = troy.Workload ()
    pprint.pprint (wl_dict)

    if  not 'tasks' in wl_dict :
        assert False, "no tasks in workload dict" 

    if  not len(wl_dict['tasks']) :
        assert False, "zero tasks in workload dict" 

    for task_dict in wl_dict['tasks'] :
        task_description = troy.TaskDescription (task_dict)
        wl.add_task (task_description)



