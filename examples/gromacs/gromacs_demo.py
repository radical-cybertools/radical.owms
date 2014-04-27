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

    # --------------------------------------------------------------------------
    # 
    # TROY CONFIGURATION: what plugins are being used, whet resources are
    # targeted, etc
    #
    resources      = "slurm+ssh://tg803521@stampede.tacc.utexas.edu,pbs+ssh://merzky@india.futuregrid.org"
  # resources      = "slurm+ssh://stampede.tacc.utexas.edu"
  # resources      = "pbs+ssh://india.futuregrid.org"
  # resources      = "pbs+ssh://hotel.futuregrid.org"
  # resources      = "pbs+ssh://alamo.futuregrid.org"
  # resources      = "pbs+ssh://sierra.futuregrid.org"
  # resources      = "fork://localhost"

    pilot_backend  = 'radical.pilot'
    
    plugin_strategy            = 'early_binding' # early, late
    plugin_planner             = 'concurrent'          # concurrent, bundles, maxcores
    plugin_overlay_translator  = 'max_pilot_size'      # max_pilot_size
    plugin_overlay_scheduler   = 'round_robin'         # rr, local
    plugin_overlay_provisioner = pilot_backend         # rp, bj, local
    plugin_workload_translator = troy.AUTOMATIC        # direct
    plugin_workload_scheduler  = 'round_robin'         # rr, first, ttc
    plugin_workload_dispatcher = pilot_backend         # rp, bj, local

    # Create a session for TROY, and configure some plugins
    session = troy.Session (user_cfg = {
                                           'resources' : demo_config['resources'],
                                           'troy'                           : {
                                               'plugin_planner'             : plugin_planner,
                                               'plugin_strategy'            : plugin_strategy,
                                               'log_level'                  : log_level,
                                               'planner'                    : {
                                                   'concurrent'             : {
                                                       'concurrency'        : concurrency,
                                                       },
                                                   },
                                               },
                                           'overlay_manager'                : {
                                               'plugin_overlay_translator'  : plugin_overlay_translator,
                                               'plugin_overlay_scheduler'   : plugin_overlay_scheduler,
                                               'plugin_overlay_provisioner' : plugin_overlay_provisioner,
                                               'overlay_scheduler'          : {
                                                   'round_robin'            : {
                                                       'resources'          : resources
                                                       },
                                                   },
                                               'overlay_translator'         : {
                                                   'max_pilot_size'         : {
                                                       'pilot_size'         : pilot_size,
                                                       },
                                                   },
                                               },
                                           'workload_manager'               : {
                                               'plugin_workload_translator' : plugin_workload_translator,
                                               'plugin_workload_scheduler'  : plugin_workload_scheduler,
                                               'plugin_workload_dispatcher' : plugin_workload_dispatcher,
                                               },
                                        })

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
      # task_descr.executable        = "/bin/echo"
      # task_descr.arguments         = ['hello troy']
        task_descr.executable        = "%(mdrun)s"
        task_descr.working_directory = "%(home)s/troy_demo/tasks/" + "%d/" % n
        task_descr.inputs            = ['input/topol.tpr > topol.tpr']
        task_descr.outputs           = ['output/%s_state.cpt.%d   < state.cpt'   % (demo_id, n),
                                        'output/%s_confout.gro.%d < confout.gro' % (demo_id, n),
                                        'output/%s_ener.edr.%d    < ener.edr'    % (demo_id, n),
                                        'output/%s_traj.trr.%d    < traj.trr'    % (demo_id, n),
                                        'output/%s_md.log.%d      < md.log'      % (demo_id, n),
                                       ]
       
        task_descriptions.append (task_descr)


    # create a troy.Workload from all those task descriptions
    workload = troy.Workload (session, task_descriptions)


    # --------------------------------------------------------------------------
    #
    # create the troy manager objects: planner, overlay manager and workload 
    # manager
    #
    # the troy.Planner accepts a workload, and derives an overlay to execute it
    planner = troy.Planner (session)

    # The order of actions on the planner, overlay manager and workload manager
    # is orchestrated by a troy execution strategy (which represents a specific
    # trace in the original troy design).
    planner.execute_workload (workload)

    # Woohooo!  Magic has happened!

