#!/usr/bin/env python

__author__    = "RADICAL Development Team"
__copyright__ = "Copyright 2014, RADICAL"
__license__   = "MIT"


import sys
import radical.owms


# ------------------------------------------------------------------------------
#
# Configure session, get application config elements
#
configs  = sys.argv[1:]
session  = radical.owms.Session (configs)


# ------------------------------------------------------------------------------
#
# define tasks and construct workload
#
task_descr = radical.owms.TaskDescription()
task_descr.executable  =  "%(mdrun)s"
task_descr.cardinality =  "%(bag_size)s"
task_descr.inputs      =  ["input/topol.tpr > topol.tpr"]
task_descr.outputs     =  ["output/%(session_id)s_state.cpt.%(cardinal)s   < state.cpt",
                           "output/%(session_id)s_confout.gro.%(cardinal)s < confout.gro",
                           "output/%(session_id)s_ener.edr.%(cardinal)s    < ener.edr",
                           "output/%(session_id)s_traj.trr.%(cardinal)s    < traj.trr",
                           "output/%(session_id)s_md.log.%(cardinal)s      < md.log"]
task_descr.working_directory = "%(home)s/radical_owms_tutorial/radical_owms_tutorial_02_%(cardinal)s/"
workload = radical.owms.Workload (session, task_descr)


# ------------------------------------------------------------------------------
#
# create a radical.owms planner within session (and its configs)
#
planner = radical.owms.Planner (session)


# ------------------------------------------------------------------------------
#
# execute workload
#
planner.execute_workload (workload)

# ------------------------------------------------------------------------------

