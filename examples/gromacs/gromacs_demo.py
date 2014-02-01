#!/usr/bin/env python

__author__    = "TROY Development Team"
__copyright__ = "Copyright 2014, RADICAL"
__license__   = "MIT"


"""
    Demo application for 1 Feb 2014, a MD Bag of Task with data staging

    Prepare/run with the following set of commands (the exact path to the packages
    may vary for you):

        virtualenv ve
        source     ve/bin/activate
        pip install ~/projects/troy/           # fix/data_staging branch
        pip install ~/projects/sagapilot/      # devel or master
        pip install ~/projects/saga-python/    # devel
        pip install ~/projects/radical.utils/  # devel
        pip install paramiko bigjob
        time ./gromacs_demo.py

    All of the dependencies will also be installed by pip, as dependencies for
    troy, but (a) sagapilot is not yet in pypi, and (b) at this point we need
    some of the deps in their devel branches.

    You will need the following additional settings in ~/.troy.cfg:

        [gromacs_demo]

        pilot_backend = sinon
        bagsize       = 3
        steps         = 256

        demo_id       = india_sinon_3_256
        user          = merzky
        mdrun         = /N/u/marksant/bin/mdrun
        home          = /N/u/merzky/
        resources     = pbs+ssh://india.futuregrid.org

"""

import os
import sys
import troy
import pprint
import radical.utils as ru


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    # for convenience, we store the configuration also in a simple json config
    # file
    if  len(sys.argv) > 1 :
        demo_config_file = sys.argv[1]
    else :
        demo_config_file = 'gromacs_demo.cfg'

    # read the demo config
    print "reading configuration from %s" % demo_config_file
    demo_config = ru.read_json (demo_config_file)

    # dig out config settings
    demo_id     =     demo_config['demo_id']
    backend     =     demo_config['pilot_backend']  # bigjob or sinon
    bagsize     = int(demo_config['bagsize'])       # number of mdrun tasks
    steps       = int(demo_config['steps'])         # mdrun parameter
    resources   =     demo_config['resources']      # for pilot scheduling
    log_level   =     demo_config['log_level']      # troy logger detail

    # we also have some configuration parameters which eventually should not be
    # needed anymore.  At this point, those information are still specific to
    # the target resource, mostly for out-of-band data staging (troy stages data
    # via saga, not via the pilot systems).
    remote_home =     demo_config['home']           # user home on resource
    remote_user =     demo_config['user']           # user name on resource
    mdrun       =     demo_config['mdrun']          # application executable


    # Create a session for TROY, and configure the plugins we are going to use
    session = troy.Session (cfg = {'overlay_scheduler_round_robin' : {
                                       'resources'   : resources
                                       },
                                   'troy' : {
                                       'log_level'   : log_level,
                                       },
                                  })

    # Also add some security credentials to the session (we assume ssh keys set
    # up for this demo, so only need to specify the user name on the target
    # resource)
    c1         = troy.Context ('ssh')
    c1.user_id = remote_user
    session.add_context (c1)


    # create the requested number of mdrun task descriptions
    print "defining %d tasks" % bagsize
    task_descriptions = list()
    for n in range(bagsize):

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


    # the troy.Planner accepts a workload, and derives an overlay to execute it
    planner = troy.Planner (planner = 'concurrent',
                            session = session)


    # the troy.OverlayManager translates an overlay transcription into an
    # overlay, then schedules and provisions it.
    overlay_mgr = troy.OverlayManager (scheduler    = 'round_robin',
                                       translator   = 'max_pilot_size',
                                       provisioner  = backend,
                                       session      = session)


    # the troy.WorkloadManager transforms a workload, schedules it over an
    # overlay, and dispatches it to the pilots.
    workload_mgr = troy.WorkloadManager (scheduler  = 'first',
                                         translator = troy.AUTOMATIC,
                                         dispatcher = backend,
                                         session    = session)

    # The order of actions on the planner, overlay manager and workload manager
    # is orchestrated by a troy execution strategy (which represents a specific
    # trace in the original troy design).
    troy.execute_workload (workload.id, planner, overlay_mgr, workload_mgr, 
                           strategy='basic_early_binding')

    # Woohooo!  Magic has happened!

