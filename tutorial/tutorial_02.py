#!/usr/bin/env python

__author__    = "TROY Development Team"
__copyright__ = "Copyright 2014, RADICAL"
__license__   = "MIT"


import sys
import troy


# ------------------------------------------------------------------------------
#
# Configure session, get application config elements
#
configs  = sys.argv[1:]
session  = troy.Session (configs)
strategy = session.cfg.get ('troy_strategy', troy.AUTOMATIC)


# ------------------------------------------------------------------------------
#
# define tasks and construct workload
#
task_descr = troy.TaskDescription()
task_descr.executable  =  "%(mdrun)s"
task_descr.cardinality =  "%(bag_size)s"
task_descr.inputs      =  ["input/topol.tpr > topol.tpr"]
task_descr.outputs     =  ["output/%(session_id)s_state.cpt.%(cardinal)s   < state.cpt",
                           "output/%(session_id)s_confout.gro.%(cardinal)s < confout.gro",
                           "output/%(session_id)s_ener.edr.%(cardinal)s    < ener.edr",
                           "output/%(session_id)s_traj.trr.%(cardinal)s    < traj.trr",
                           "output/%(session_id)s_md.log.%(cardinal)s      < md.log"]
task_descr.working_directory = "%(home)s/troy_tutorial/troy_tutorial_02_%(cardinal)s/"
workload = troy.Workload (session, task_descr)


# ------------------------------------------------------------------------------
#
# create managers within session (and its configs)
#
planner      = troy.Planner         (session)
overlay_mgr  = troy.OverlayManager  (session)
workload_mgr = troy.WorkloadManager (session)


# ------------------------------------------------------------------------------
#
# execute workload
#
troy.execute_workload (workload, planner, overlay_mgr, workload_mgr,
                       strategy=strategy)

# ------------------------------------------------------------------------------

