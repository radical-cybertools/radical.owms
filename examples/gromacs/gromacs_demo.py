#!/usr/bin/env python

__author__    = "TROY Development Team"
__copyright__ = "Copyright 2014, RADICAL"
__license__   = "MIT"


import sys
import troy


"""
    Demo application for 1 Feb 2014, a MD Bag of Task with data staging

    A suitable virtualenv can be created by sourcing 'prepare_demo.sh' -- this
    will create a temporary repository space under `troy_install`, and
    a virtualenv with all required dependencies under `troy_virtualenv`.

    Additionally, you will need a demo configuration file, like this::

        {
            "demo_id"       : "demo_stampede_3_256",
            "steps"         : 256,
            "bag_size"      : 3,
            "pilot_size"    : 4,
            "concurrency"   : 100,
        
            # target host configuration for futuregrid
            "user"          : "merzky",
            "mdrun"         : "/N/u/marksant/bin/mdrun",
            "home"          : "/N/u/merzky/",
            
            "log_level"     : "INFO"
        }

    The `demo_id` is used as prefix for the output data staged back to
    localhost; `steps` is the number of iteration steps for each task;
    `bag_size` is the number of MD tasks running; `pilot_size` and `concurrency`
    govern the task distribution over the pilots. 

    The additional host configuration info are somewhat redundant with resource
    information available on Troy and other layers -- but are required for data
    staging, which is at this point not well integrated in the Pilot layer
    interactions.  For further Troy configuration options, you may want to check
    out `examples/troy.cfg`.

    The demo supports the execution of different `traces`, by the virtue of
    selecting different plugins, pilot backends, execution strategies, and
    target resources.  See code section `TROY CONFIGURATION` below.

    You can run the demo by calling::

        python gromacs_demo.py [config_file]

    where `config_file` defaults to `./gromacs_demo.cfg`.

"""


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    # --------------------------------------------------------------------------
    #
    # configuration of demo options (i.e. application options)
    #
    # for convenience, we store the configuration also in a simple json config
    # file
    if  len(sys.argv) > 1 :
        demo_config_file = sys.argv[1]
    else :
        demo_config_file = 'gromacs_demo.cfg'

    # read the demo config
    import radical.utils 
    print "reading configuration from %s" % demo_config_file
    demo_config = radical.utils.read_json  (demo_config_file)

    # dig out config settings
    demo_id     =     demo_config['demo_id']
    steps       = int(demo_config['steps'])         # mdrun parameter
    bag_size    = int(demo_config['bag_size'])      # number of mdrun tasks
    pilot_size  = int(demo_config['pilot_size'])    # number of cores per pilot
    concurrency = int(demo_config['concurrency'])   # % of concurrent tasks
    log_level   =     demo_config['log_level']      # troy logging detail

    # we also have some configuration parameters which eventually should not be
    # needed anymore.  At this point, those information are still specific to
    # the target resource, mostly for out-of-band data staging (troy stages data
    # via saga, not via the pilot systems).
    mdrun       =     demo_config['mdrun']          # application executable
    remote_home =     demo_config['home']           # user home on resource
    remote_user =     demo_config['user']           # user name on resource


    # --------------------------------------------------------------------------
    # 
    # TROY CONFIGURATION: what plugins are being used, whet resources are
    # targeted, etc
    #
    resources      = "slurm+ssh://stampede.tacc.utexas.edu"
  # resources      = "pbs+ssh://india.futuregrid.org"
  # resources      = "pbs+ssh://india.futuregrid.org,pbs+ssh://sierra.futuregrid.org,"
  # resources      = "fork://localhost"
    pilot_backend  = 'bigjob_pilot'
    
    plugin_strategy            = 'basic_early_binding' # early, late
    plugin_planner             = 'concurrent'          # concurrent, bundles, maxcores
    plugin_overlay_translator  = 'max_pilot_size'      # max_pilot_size
    plugin_overlay_scheduler   = 'round_robin'         # rr, local
    plugin_overlay_provisioner = pilot_backend         # sinon, bj, local
    plugin_workload_translator = troy.AUTOMATIC        # direct
    plugin_workload_scheduler  = 'round_robin'         # rr, first, ttc
    plugin_workload_dispatcher = pilot_backend         # sinon, bj, local

    # Create a session for TROY, and configure some plugins
    session = troy.Session (cfg = {'overlay_scheduler_round_robin' : {
                                       'resources'   : resources
                                       },
                                   'planner_concurrent' : {
                                       'concurrency' : concurrency,
                                       },
                                   'overlay_translator_max_pilot_size' : {
                                       'pilot_size'  : pilot_size,
                                       },
                                   'troy' : {
                                       'log_level'   : log_level,
                                       },
                                  })

    # Also add some security credentials to the session (we assume ssh keys set
    # up for this demo, so only need to specify the user name on the target
    # resource).
    c1         = troy.Context ('ssh')
    c1.user_id = remote_user
    session.add_context (c1)


    # --------------------------------------------------------------------------
    #
    # create our application workload
    #
    # create the requested number of mdrun task descriptions
    print "defining %d tasks" % bag_size
    task_descriptions = list()
    for n in range(bag_size):

        task_descr                   = troy.TaskDescription()
        task_descr.tag               = "%d" % n
        task_descr.executable        = mdrun
        task_descr.arguments         = ['-nsteps', steps]
        task_descr.working_directory = "%s/troy_demo/tasks/%d/" % (remote_home, n)
        task_descr.inputs            = ['input/topol.tpr > topol.tpr']
        task_descr.outputs           = ['output/%s_state.cpt.%d   < state.cpt'   % (demo_id, n),
                                        'output/%s_confout.gro.%d < confout.gro' % (demo_id, n),
                                        'output/%s_ener.edr.%d    < ener.edr'    % (demo_id, n),
                                        'output/%s_traj.trr.%d    < traj.trr'    % (demo_id, n),
                                        'output/%s_md.log.%d      < md.log'      % (demo_id, n),
                                       ]

        task_descriptions.append (task_descr)


    # create a troy.Workload from all those task descriptions
    workload = troy.Workload (task_descriptions)


    # --------------------------------------------------------------------------
    #
    # create the troy manager objects: planner, overlay manager and workload 
    # manager
    #
    # the troy.Planner accepts a workload, and derives an overlay to execute it
    planner = troy.Planner (planner = plugin_planner,
                            session = session)


    # the troy.OverlayManager translates an overlay transcription into an
    # overlay, then schedules and provisions it.
    overlay_mgr = troy.OverlayManager (translator   = plugin_overlay_translator,
                                       scheduler    = plugin_overlay_scheduler,
                                       provisioner  = plugin_overlay_provisioner,
                                       session      = session)


    # the troy.WorkloadManager transforms a workload, schedules it over an
    # overlay, and dispatches it to the pilots.
    workload_mgr = troy.WorkloadManager (translator  = plugin_workload_translator,   
                                         scheduler   = plugin_workload_scheduler,
                                         dispatcher  = plugin_workload_dispatcher,
                                         session     = session)

    # The order of actions on the planner, overlay manager and workload manager
    # is orchestrated by a troy execution strategy (which represents a specific
    # trace in the original troy design).
    troy.execute_workload (workload     = workload, 
                           planner      = planner, 
                           overlay_mgr  = overlay_mgr, 
                           workload_mgr = workload_mgr, 
                           strategy     = plugin_strategy)

    # Woohooo!  Magic has happened!

