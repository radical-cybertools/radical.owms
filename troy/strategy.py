
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils as ru

import troy


# ------------------------------------------------------------------------------
#
def execute_workload (workload, planner, overlay_mgr, workload_mgr, 
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

    # for initialization, we re-use the planner session
    strategy.init_plugin (planner.session, 'strategy')

    # this method accepts workloads and workload IDs
    if  isinstance   (workload, basestring) :
        workload_id = workload
    elif isinstance  (workload, troy.Workload) :
        workload_id = workload.id
    else :
        raise TypeError ("strategy apply to troy workloads, not to %s" \
                      % type(workload))

    # hand over control the selected strategy plugin, 
    # so it can do what it has to do.
    strategy.execute (workload_id, planner, overlay_mgr, workload_mgr)


