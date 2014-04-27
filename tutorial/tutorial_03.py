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
task_descr.working_directory = "%(home)s/radical_owms_tutorial/radical_owms_tutorial_03_%(cardinal)s/"
workload = radical.owms.Workload (session, task_descr)


# ------------------------------------------------------------------------------
#
# create managers within session (and its configs)
#
planner      = radical.owms.Planner         (session)
overlay_mgr  = radical.owms.OverlayManager  (session)
workload_mgr = radical.owms.WorkloadManager (session)


# ------------------------------------------------------------------------------
#
# execute workload with our own strategy (which is just basic late binding,
# really..
#
radical.owms._logger.info ('apply custom strategy to workload %s!' % workload.id)

# combine or split tasks in the workload (this expands cardinality)
workload_mgr.expand_workload (workload.id)

# derive initial description of the overlay based on the workload
overlay_descr = planner.derive_overlay (workload.id)
print "overlay_descr: %s" % overlay_descr

# create an overlay based on that description -- that overlay does not yet have
# any pilots.
overlay = radical.owms.Overlay (overlay_mgr.session, overlay_descr)
print "overlay id   : %s" % overlay.id

# translate overlay description into N pilot descriptions
overlay_mgr.translate_overlay (overlay.id)
print overlay.pilots

#######################################################################
# 
# NOTE: we schedule instantiate the pilots before scheduling the units
#
# decide which resources to use for constructing the overlay
overlay_mgr.schedule_overlay (overlay.id)
print overlay.pilots

# instantiate pilots on specified resources
overlay_mgr.provision_overlay (overlay.id)
print overlay.pilots
#
#######################################################################

# ------------------------------------------------------------------------------
# 
# we are done with the overlay -- it exists (even if pilots may still be in the
# queue), and we can transform / dispatch the workload.

# translate /split workload into ComputeUnits etc
workload_mgr.translate_workload (workload.id, overlay.id)
print workload.tasks

# schedule the workload onto the overlay
workload_mgr.bind_workload (workload.id, overlay.id,
                            bind_mode=radical.owms.LATE)
print workload.tasks

# both the overlay and the workload are now scheduled/bound -- we
# can expect the unit working directories to be createable, at the
# least, and can thus trigger stage-in for the workload.
workload_mgr.stage_in_workload (workload.id)

# execute the tasks on the Pilots
workload_mgr.dispatch_workload (workload.id, overlay.id)
print workload.tasks

# Of course nothing will fail due to radical.owms's magic robustness and
# and we therefore just wait until its done!
workload.wait ()

# check for success
if workload.state == radical.owms.DONE :
    radical.owms._logger.info  ("workload %s done" % workload.id)
else :
    radical.owms._logger.error ("workload %s failed - abort" % workload.id)

# once the workload is done, we stage data out...
workload_mgr.stage_out_workload (workload.id)
print workload.tasks

# ------------------------------------------------------------------------------
# make sure to cancel the overlay
overlay_mgr.cancel_overlay (overlay.id)
print overlay.pilots


# ------------------------------------------------------------------------------

