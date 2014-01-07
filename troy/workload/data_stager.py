
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils      as ru
import troy.utils         as tu
from   troy.constants import *
import troy


"""
Stage_in  for a given unit, once the unit is in BOUND state.
Stage_out for a given unit, once the unit is in final state.
"""


# ------------------------------------------------------------------------------
#
class DataStager (object) :
    """
    FIXME
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self, session=None) : 
        """
        FIXME
        """

        if  session :
            self._session = session
        else:
            self._session = troy.Session ()


    # --------------------------------------------------------------------------
    #
    def stage_in_workload (self, workload) :
        print "staging_in workload %s" % (workload.id)
        for task_id in workload.tasks :
            self.stage_in_task (workload.tasks[task_id])
        return

    def stage_in_task (self, task) :
        print "staging_in task %s" % (task.id)
        for unit_id in task.units :
            self.stage_in_unit (task.units[unit_id])
        return

    def stage_in_unit (self, unit) :

        # stage in only once
        if  unit.staged_in :
            return

        pilot = troy.Pilot (unit.pilot_id)
        print "staging_in unit %s on %s (%s)" % (unit.id, pilot.id, pilot.resource)

        if  not unit.working_directory :
            raise RuntimeError ("no working directory defined for %s - cannot stage-in" % unit.id)

        for fin in unit.inputs :
            print "staging_in %s to %s / %s" % (fin, pilot.resource, unit.working_directory)
            unit.task.workload.manager._dispatcher.stage_file_in (fin, pilot.resource, unit.working_directory)
            unit.staged_in = True
        return



    # --------------------------------------------------------------------------
    #
    def stage_out_workload (self, workload) :
        print "staging_out workload %s" % (workload.id)
        for task_id in workload.tasks :
            self.stage_out_task (workload.tasks[task_id])
        return

    def stage_out_task (self, task) :
        print "staging_out task %s" % (task.id)
        for unit_id in task.units :
            self.stage_out_unit (task.units[unit_id])
        return

    def stage_out_unit (self, unit) :

        # stage in only once
        if  unit.staged_out :
            return

        pilot = troy.Pilot (unit.pilot_id)
        print "staging_out unit %s on %s (%s)" % (unit.id, pilot.id, pilot.resource)

        if  not unit.working_directory :
            raise RuntimeError ("no working directory defined for %s - cannot stage-in" % unit.id)

        for fout in unit.outputs :
            unit.task.workload.manager._dispatcher.stage_file_out (pilot.resource, unit.working_directory, fout)
            print "staging_out %s from %s / %s" % (fout, pilot.resource, unit.working_directory)
            unit.staged_out = True
        return


# ------------------------------------------------------------------------------

