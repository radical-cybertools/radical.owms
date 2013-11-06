
__author__    = "Andre Merzky"
__copyright__ = "Copyright 2013, The SAGA Project"
__license__   = "MIT"


import radical.utils.testing as rut

import troy

# ------------------------------------------------------------------------------
#
def test_overlay_create () :
    """ 
    test overlay creation
    """
    tc = rut.get_test_config ()
    wl_dict = tc.overlay_dict
    wl      = troy.overlay ()

    if  not 'tasks' in wl_dict :
        assert False, "no tasks in overlay dict" 

    if  not len(wl_dict['tasks']) :
        assert False, "zero tasks in overlay dict" 

    for task_dict in wl_dict['tasks'] :
        task_description = troy.TaskDescription (task_dict)
        wl.add_task (task_description)
