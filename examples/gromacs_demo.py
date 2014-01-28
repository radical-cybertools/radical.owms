
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2014, RADICAL"
__license__   = "MIT"


"""
    Demo application for 1 feb 2014
    - Bag of Task (BoT)

"""

import os
import time
import troy
import getpass


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    # set up local pwd
#    try :
#        os.mkdir("/tmp/troy_demo/")
#    except :
#        pass # might exist
#
    #os.chdir("/tmp/troy_demo/")

    # Create a session for TROY.
    session = troy.Session(
        {
            'planner_concurrent': {
                'concurrency': 100
            },
          # 'workload_dispatcher_bigjob_pilot': {
          #     'coordination_url' : BJ_COORD_URL
          # },
          # 'overlay_provisioner_bigjob_pilot': {
          #     'coordination_url' : BJ_COORD_URL
          # },
        })

    demo_config = session.get_config ('gromacs_demo')

  # # Add resources to the session.
  # session.user_cfg['overlay_scheduler_round_robin'] = {
  #     'resources': 'pbs+ssh://india.futuregrid.org/'
  # }

    # Manage credentials.
    # TODO: set it to args.protocol (default ssh).
    c1 = troy.Context ('ssh')
    c1.user_id = demo_config['user']
    session.add_context (c1)

    # Responsible for application workload
    workload_mgr = troy.WorkloadManager(dispatcher = demo_config['pilot_backend'],
                                        session    = session)

    # Responsible for managing the pilot overlay
    overlay_mgr = troy.OverlayManager(scheduler    = 'round_robin',
                                      provisioner  = demo_config['pilot_backend'],
                                      session      = session)

    # Planning makes initial mapping of workload to overlay
    planner = troy.Planner (planner='concurrent',
                            session=session)

    # Create a task for every radicalist
    task_descriptions = list()
    steps = 256
    bagsize = 10
    for n in range(bagsize):

        task_descr                   = troy.TaskDescription()
        task_descr.tag               = "%d" % n
        task_descr.executable        = '%s' % demo_config['mdrun']
        task_descr.arguments         = ['-nsteps', steps]

        task_descr.inputs            = ['topol.tpr']
        task_descr.outputs           = ['state.cpt.%d   < state.cpt'   % n, 
                                        'confout.gro.%d < confout.gro' % n, 
                                        'ener.edr.%d    < ener.edr'    % n, 
                                        'traj.trr.%d    < traj.trr'    % n, 
                                        'md.log.%d      < md.log'      % n]
        task_descr.working_directory = "%s/troy_demo/tasks/%d/" % (demo_config['home'], n)

        print task_descr

        task_descriptions.append(task_descr)


    workload_id = workload_mgr.create_workload(task_descriptions)

    # execute the workload with the given execution strategy
    troy.execute_workload(workload_id, planner, overlay_mgr, workload_mgr, strategy='basic')

    # Woohooo!  Magic has happened!

