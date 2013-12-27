
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils as ru

import troy


# ------------------------------------------------------------------------------
#
def execute_workload (workload_id, planner, overlay_mgr, workload_mgr, 
                      strategy='default') : 

    """
    Execute the given workload -- i.e., translate, bind and dispatch it, and
    then wait until its execution is completed.  For that to happen, we also
    need to plan, translate, schedule and dispatch an overlay, obviously...
    """

    plugin_mgr = ru.PluginManager ('troy')
    strategy   = plugin_mgr.load  ('strategy', strategy)

    if  not strategy  : 
        raise RuntimeError ("Could not load troy strategy plugin")

    # for initialization, we re-use the workload manager session
    strategy.init_plugin (workload_mgr._session)

    # hand over control over workload to the manager plugin, so it can do
    # what it has to do.
    strategy.execute (workload_id, planner, overlay_mgr, workload_mgr)


