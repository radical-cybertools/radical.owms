
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


"""
Synapse demo for 19 dec 2013
"""



import os
import sys
import time
import shlex
import getpass
import synapse

import troy

app_num   = 4
app_size  = 100
app_depth = 100000
app_id    = 'mongodb://ec2-184-72-89-141.compute-1.amazonaws.com:27017/synapse_mandelbrot/1'
bj_coord  = 'redis://%s@gw68.quarry.iu.teragrid.org:6379' % os.environ['REDIS_PASSWORD']

# app_id    = 'mongodb://localhost:27017/synapse_mandelbrot/1'
# bj_coord  = 'redis://localhost/'

os.environ['COORDINATION_URL'] = bj_coord

# ------------------------------------------------------------------------------
def synapsify (td, mode) :

    # re-create command line, ...
    command = "%s %s" % (td.executable, ' '.join(td.arguments))

    # ... apply synapsification mode, ...
    command = synapse.synapsify (command, mode)


    # ... then nicely split the resulting command line, and ...
    elems   = shlex.split (command)

    # set the new executable and arguments
    td.executable = elems[0]
    td.arguments  = elems[1:]

    return td # for call chanining


# ------------------------------------------------------------------------------
#
if __name__ == '__main__' :
    """
    We create two workload chunks and two overlays -- one for the master with
    the default plugins, so that the master will run locally, and one for the
    workers on india.
    """

    start   = time.time ()
    mode    = None # synapse.PROFILE
    session = troy.Session ()

    # troy managers for master
    m_planner      = troy.Planner         (session)
    m_overlay_mgr  = troy.OverlayManager  (session)
    m_workload_mgr = troy.WorkloadManager (session)

    # troy managers for workers
    w_planner      = troy.Planner         (session)
    w_overlay_mgr  = troy.OverlayManager  (session)
    w_workload_mgr = troy.WorkloadManager (session)


    # --------------------------------------------------------------------------
    # Create and dispatch the master workload first.
    m_workload    = troy.Workload (session)
    m_workload_id = m_workload.id

    td = troy.TaskDescription ({'tag'       : 'master',
                                'executable': 'mandelbrot_master.py',
                                'arguments' : ['--master_id=%s' % app_id,
                                               '-n=%s'          % app_num,
                                               '-s=%s'          % app_size,
                                               '-d=%s'          % app_depth]})
    m_workload.add_task (synapsify (td, mode))

    m_overlay_descr = m_planner.derive_overlay (m_workload_id)
    m_overlay       = troy.Overlay (session, m_overlay_descr)
    m_overlay_id    = m_overlay.id

    m_overlay_mgr.translate_overlay         (m_overlay_id)
    m_overlay_mgr.schedule_overlay          (m_overlay_id)
    m_overlay_mgr.provision_overlay         (m_overlay_id)

    m_workload_mgr.expand_workload          (m_workload_id)
    m_workload_mgr.translate_workload       (m_workload_id, m_overlay_id)
    m_workload_mgr.bind_workload            (m_workload_id, m_overlay_id)
    m_workload_mgr.dispatch_workload        (m_workload_id, m_overlay_id)

    # we wait until the master is running, otherwise theworkers will not find
    # any work.  We need to check state for all workload CUs -- but of course we
    # will probably only see one CU...
    m_units = list()
    for     m_task_id, m_task in m_workload.tasks.items() :
        for m_unit_id, m_unit in m_task.units.items() :
            m_units.append (m_unit)

    while troy.RUNNING not in [m_unit.state for m_unit in m_units] :
        time.sleep (1)
        troy._logger.info  ("wait for master to come up")

    m_workload.state


    # --------------------------------------------------------------------------
    # now create and dispatch worker workload (essentially bag of tasks)
    w_workload    = troy.Workload (session)
    w_workload_id = w_workload.id

    for i in range (0, app_num) :
        td = troy.TaskDescription ({'tag'       : 'worker_%d' % i,
                                    'executable': 'mandelbrot_worker.py',
                                    'arguments' : ['--master_id=%s'   % app_id,
                                                   '-n=%s'            % app_num,
                                                   '-s=%s'            % app_size,
                                                   '-d=%s'            % app_depth, 
                                                   '--worker_id=%d'   % i]})
        w_workload.add_task (synapsify (td, mode))

    w_overlay_descr = w_planner.derive_overlay (w_workload_id)
    w_overlay       = troy.Overlay (session, w_overlay_descr)
    w_overlay_id    = w_overlay.id

    w_overlay_mgr.translate_overlay         (w_overlay_id)
    w_overlay_mgr.schedule_overlay          (w_overlay_id)
    w_overlay_mgr.provision_overlay         (w_overlay_id)

    w_workload_mgr.expand_workload          (w_workload_id)
    w_workload_mgr.translate_workload       (w_workload_id, w_overlay_id)
    w_workload_mgr.bind_workload            (w_workload_id, w_overlay_id)
    w_workload_mgr.dispatch_workload        (w_workload_id, w_overlay_id)

    # we wait until the worker workload is done, but don't really care about the
    # states of the individual CUs
    while w_workload.state not in [troy.DONE, troy.FAILED, troy.CANCELED] :
        time.sleep (1)
        troy._logger.info  ("wait for workers to finish")



    # --------------------------------------------------------------------------
    # at that point, the master should also finish (eventually)
    while m_workload.state not in [troy.DONE, troy.FAILED, troy.CANCELED] :
        time.sleep (1)
        troy._logger.info  ("wait for master  to finish")


    # --------------------------------------------------------------------------
    # We are done -- clean up
    m_workload_mgr.cancel_workload (m_workload_id)
    w_workload_mgr.cancel_workload (w_workload_id)
    m_overlay_mgr .cancel_overlay  (m_overlay_id)
    w_overlay_mgr .cancel_overlay  (w_overlay_id)


    # --------------------------------------------------------------------------

    print "ttc: %.2f (%s %s %s)" % (time.time() - start, 
                                       app_size, app_depth, app_num)


    # --------------------------------------------------------------------------

