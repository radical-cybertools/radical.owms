
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils as ru
import troy

# ------------------------------------------------------------------------------
#
def execute_workload (workload, config. 
                      strategy=troy.AUTOMATIC) : 
    """
    Parse and execute a given workload, i.e., translate, bind and dispatch it,
    and then wait until its execution is completed.  For that to happen, we also
    need to plan, translate, schedule and dispatch an overlay, obviously...
    """

    session  = troy.Session (config)
    strategy = troy.AUTOMATIC

    if  'plugin_strategy' in session.cfg :
        strategy = session.cfg['plugin_strategy']

    if  strategy == troy.AUTOMATIC :
        strategy =  'basic_late_binding'


    planner      = troy.Planner         (session)
    overlay_mgr  = troy.OverlayManager  (session)
    workload_mgr = troy.WorkloadManager (session)

    if  isinstance (workload, basestring) :
        # we assume this string points to a file containing a workload description 
        parsed_workload = workload_mgr.parse_workload (workload)
    elif  isinstance (workload, troy.Workload) :
        parsed_workload = workload
    else :
        raise TypeError ("workload needs to be a troy.Workload or a filename "
                         "pointing to a workload description, not '%s'" 
                         % type (workload))


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


