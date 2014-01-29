
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
    def _parse_staging_directive (self, txt) :
        """
        returns [src, tgt, op] as relative or absolute paths or URLs.  This
        parsing is backward compatible with the simple staging directives used
        in troy previously -- any strings which do not contain staging operators
        will be interpreted as simple paths (identical for src and tgt,
        operation set to '=', which is interpreted as ).

        Supported directives:

           src >  tgt -- stage  task input ./src to remote remote.host as ./tgt
           src >> tgt -- append task input ./src to remote remote.host    ./tgt
           tgt <  src -- stage  task output from remote host ./src to     ./tgt
           tgt << src -- append task output from remote host ./src to     ./tgt
        """

        rs = ru.ReString (txt)

        if  rs // '^(?P<one>.+?)\s*(?P<op><|<<|>|>>)\s*(?P<two>.+)$' :
            res = rs.get ()
            return (res['one'], res['two'], res['op'])

        else :
            return (txt, txt, '=')


    # --------------------------------------------------------------------------
    #
    def stage_in_workload (self, workload) :
      # print "staging_in workload %s" % (workload.id)
        for task_id in workload.tasks :
            self.stage_in_task (workload.tasks[task_id])
        return

    def stage_in_task (self, task) :
      # print "staging_in task %s" % (task.id)
        for unit_id in task.units :
            self.stage_in_unit (task.units[unit_id])
        return

    def stage_in_unit (self, unit) :

        # stage in only once
        if  unit.staged_in :
            return

        # do nothing if nothing to do
        if  not len(unit.inputs) :
            return

        pilot = troy.Pilot (unit.pilot_id)
      # print "staging_in unit %s on %s (%s)" % (unit.id, pilot.id, pilot.resource)

        if  not unit.working_directory :
            raise RuntimeError ("no working directory defined for %s - cannot stage-in" % unit.id)

        for fin in unit.inputs :
            if  not isinstance (fin, basestring) :
                raise TypeError ("Input files need to be strings, not %s" % type(fin))

            one, two, op = self._parse_staging_directive (fin)
            if  op in ['>>'] :
                raise ValueError ("op '>>' (append) not yet supported for input staging")

            if  op not in ['>', '='] :
                raise ValueError ("invalid staging op '%s' for input staging" % op)

            troy._logger.debug ("staging_in  %s > %s / %s / %s" \
                             %  (one, pilot.resource, unit.working_directory, two))
            unit.task.workload.manager._dispatcher.stage_file_in (one, pilot.resource, 
                    unit.working_directory, two)

        unit.staged_in = True


    # --------------------------------------------------------------------------
    #
    def stage_out_workload (self, workload) :
      # print "staging_out workload %s" % (workload.id)
        for task_id in workload.tasks :
            self.stage_out_task (workload.tasks[task_id])
        return

    def stage_out_task (self, task) :
      # print "staging_out task %s" % (task.id)
        for unit_id in task.units :
            self.stage_out_unit (task.units[unit_id])
        return

    def stage_out_unit (self, unit) :

        # stage in only once
        if  unit.staged_out :
            return

        # do nothing if nothing to do
        if  not len(unit.outputs) :
            return

        pilot = troy.Pilot (unit.pilot_id)


        if  not unit.working_directory :
            raise RuntimeError ("no working directory defined for %s - cannot stage-in" % unit.id)

        for fout in unit.outputs :
            if  not isinstance (fout, basestring) :
                raise TypeError ("Input files need to be strings, not %s" % type(fout))

            one, two, op = self._parse_staging_directive (fout)
            if  op in ['<<'] :
                raise ValueError ("op '<<' (append) not yet supported for output staging")

            if  op not in ['<', '='] :
                raise ValueError ("invalid staging op '%s' for output staging" % op)

            troy._logger.debug ("staging_out %s < %s / %s / %s" \
                             %  (one, pilot.resource, unit.working_directory, two))
            unit.task.workload.manager._dispatcher.stage_file_out (one, pilot.resource, 
                    unit.working_directory, two)

        unit.staged_out = True


# ------------------------------------------------------------------------------

