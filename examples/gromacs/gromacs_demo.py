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
import troy


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    # Create a session for TROY, and dig out the demo config settings
    session     = troy.Session ()
    demo_config = session.get_config ('gromacs_demo')

    demo_id     =     demo_config['demo_id']
    resources   =     demo_config['resources']
    backend     =     demo_config['pilot_backend']
    remote_home =     demo_config['home']
    remote_user =     demo_config['user']
    bagsize     = int(demo_config['bagsize'])
    steps       = int(demo_config['steps'])

    # configure our troy session
    session.user_cfg['overlay_scheduler_round_robin'] = {
        'resources'   : resources
    }
    session.user_cfg['planner_concurrent'] = {
        'a' : 'b',
        'concurrency' : 100
    }
    session.user_cfg['overlay_translator_max_pilot_size'] = {
        'pilot_size'  : 4
    }

    # Manage credentials.
    c1         = troy.Context ('ssh')
    c1.user_id = remote_user
    session.add_context (c1)

    # Planning makes initial mapping of workload to overlay
    planner = troy.Planner (planner = 'concurrent',
                            session = session)

    # Responsible for managing the pilot overlay
    overlay_mgr = troy.OverlayManager(scheduler    = 'round_robin',
                                      translator   = 'max_pilot_size',
                                      provisioner  = backend,
                                      session      = session)

    # Responsible for application workload
    workload_mgr = troy.WorkloadManager(scheduler  = 'first',
                                        translator = troy.AUTOMATIC,
                                        dispatcher = backend,
                                        session    = session)

    # Create a task for every radicalist
    task_descriptions = list()
    for n in range(bagsize):

        task_descr                   = troy.TaskDescription()
        task_descr.tag               = "%d" % n
        task_descr.executable        = '%s' % demo_config['mdrun']
        task_descr.arguments         = ['-nsteps', steps]

        task_descr.inputs            = ['topol.tpr']
        task_descr.outputs           = ['%s_state.cpt.%d   < state.cpt'   % (demo_id, n), 
                                        '%s_confout.gro.%d < confout.gro' % (demo_id, n), 
                                        '%s_ener.edr.%d    < ener.edr'    % (demo_id, n), 
                                        '%s_traj.trr.%d    < traj.trr'    % (demo_id, n), 
                                     #  '%s_md.log.%d      < md.log'      % (demo_id, n),
                                       ]
        task_descr.working_directory = "%s/troy_demo/tasks/%d/" % (remote_home, n)

        task_descriptions.append(task_descr)


    # create a workload from all those task descriptions
    workload_id = workload_mgr.create_workload(task_descriptions)

    # execute the workload with the given execution strategy
    troy.execute_workload (workload_id, planner, overlay_mgr, workload_mgr, 
                           strategy='basic_early_binding')

    # Woohooo!  Magic has happened!

