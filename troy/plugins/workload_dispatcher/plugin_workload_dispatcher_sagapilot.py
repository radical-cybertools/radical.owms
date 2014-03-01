

import os
import sagapilot     as sp
import radical.utils as ru
from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_dispatcher', 
    'name'        : 'sagapilot', 
    'version'     : '0.1',
    'description' : 'this is a dispatcher which submits to sagapilot pilots.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (troy.PluginBase):
    """
    This plugin dispatches workloads (and their compute units) to SAGA-Pilot pilots,
    uring SAGA-Pilot's pilot API.

    **Configuration Options:**

    * `coordination_url`: the redis URL to be used by SAGA-Pilot.  The environment
        variable COORDINATION_URL is used as fallback.
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def init (self):

        self._coord = None

        if  'coordination_url' in self.cfg :
            self._coord = self.cfg['coordination_url']

        elif 'COORDINATION_URL' in os.environ :
            self._coord = os.environ['COORDINATION_URL'] 

        else :
            troy._logger.error ("No COORDINATION_URL set for sagapilot backend")
            troy._logger.info  ("example: export COORDINATION_URL=redis://<pass>@gw68.quarry.iu.teragrid.org:6379")
            troy._logger.info  ("Contact Radica@Ritgers for the redis password")
            raise RuntimeError ("Cannot use sagapilot backend - no COORDINATION_URL -- see debug log for details")

        self._sp  = sp.Session (database_url = self._coord)


    # --------------------------------------------------------------------------
    #
    def dispatch (self, workload, overlay) :
        """
        Dispatch a given workload: examine all tasks in the WL to find the
        defined CUs, and dispatch them to the pilot system.  
        """

        for tid in workload.tasks.keys () :

            task = workload.tasks[tid]

            for uid in task.units.keys () :

                unit = task.units[uid]

                # sanity check for CU state -- only in BOUND state we can 
                # rely on a pilot being assigned to the CU.
                if  unit.state not in [BOUND] :
                    raise RuntimeError ("Can only dispatch units in BOUND state (%s)" % unit.state)


                # get the unit description, and the target pilot ID
                unit_descr = unit.as_dict ()
                pilot_id   = unit['pilot_id']

                # reconnect to the given pilot -- this is likely to pull the
                # instance from a cache, so should not cost too much.
                pilot      = troy.Pilot (self.session, pilot_id, _instance_type='sagapilot')
                troy._logger.info ('workload dispatch : dispatch %-18s to %s' \
                                % (uid, pilot._get_instance('sagapilot')[1]))
                
                # translate our information into sagapilot speak, and dispatch
                # a cu for the CU

                keymap = {
                    'tag'               : 'name', 
                    'executable'        : 'executable', 
                    'arguments'         : 'arguments', 
                    'environment'       : 'environment', 
                    'cores'             : 'cores', 
                  # 'inputs'            : 'input_data', 
                  # 'outputs'           : 'output_data', 
                    'working_directory' : 'working_directory_priv'
                  }

                sp_cu_descr = sp.ComputeUnitDescription ()
                for key in unit_descr :
                    if  key in keymap :
                        sp_cu_descr[keymap[key]] = unit_descr[key]


                # FIXME: sanity check for pilot type
                [sp_um, sp_pm, sp_pilot] = pilot._get_instance ('sagapilot')
                sp_cu = sp_um.submit_units (sp_cu_descr)

                # attach the backend instance to the unit, for later state
                # checks etc. We leave it up to the unit to decide if it wants
                # to cache the instance, or just the ID and then later
                # reconnect.
                unit._set_instance ('sagapilot', self, 
                                    instance  = [sp_um,     sp_cu],
                                    native_id = [sp_um.uid, sp_cu.uid])


    # --------------------------------------------------------------------------
    #
    def unit_reconnect (self, native_id) :
        """
        the unit lost the instance, and needs to reconnect...
        This is what is getting called on troy.Unit._get_instance, if that
        troy.Unit doesn't have that instance anymore...
        """

        troy._logger.debug ("reconnect to sagapilot cu %s" % native_id)
        sp_um_id = native_id[0]
        sp_cu_id = native_id[1]

        sp_um    = self._sp.get_unit_managers (sp_um_id)
        sp_cu    = sp_um.get_units (sp_cu_id)

        return [sp_um, sp_cu]


    # --------------------------------------------------------------------------
    #
    def unit_get_info (self, unit) :
        """
        unit inspection: get all possible information for the unit, and return
        in a dict.  This dict SHOULD contain 'state' at the very least -- but
        check the pilot_inspection unit test for more recommended attributes.
        """

        # find out what we can about the pilot...
        [sp_um, sp_cu] = unit._get_instance ('sagapilot')

        info = {'uid'              : sp_cu.uid,
                'description'      : sp_cu.description,
                'state'            : sp_cu.state,
                'stdout'           : sp_cu.stdout,
                'stderr'           : sp_cu.stderr,
                'log'              : sp_cu.log,
                'execution_details': sp_cu.execution_details,
                'submission_time'  : sp_cu.submission_time,
                'start_time'       : sp_cu.start_time,
                'stop_time'        : sp_cu.stop_time}


        # translate sagapilot state to troy state
        if  'state' in info :
            troy._logger.debug ('sagapilot level cu state: %s' % info['state'])
            # hahaha python switch statement hahahahaha
            info['state'] =  {sp.states.PENDING                 : PENDING, 
                              sp.states.PENDING_EXECUTION       : PENDING, 
                              sp.states.PENDING_INPUT_TRANSFER  : RUNNING, 
                              sp.states.TRANSFERRING_INPUT      : RUNNING, 
                              sp.states.RUNNING                 : RUNNING, 
                              sp.states.PENDING_OUTPUT_TRANSFER : RUNNING, 
                              sp.states.TRANSFERRING_OUTPUT     : RUNNING, 
                              sp.states.DONE                    : DONE, 
                              sp.states.CANCELED                : CANCELED, 
                              sp.states.FAILED                  : FAILED, 
                              sp.states.UNKNOWN                 : UNKNOWN}.get (info['state'], UNKNOWN)

      # print 'unit_get_info: %s' % info
        # unit_get_info: {'log'               : None, 
        #                 'state'             : 'Done', 
        #                 'uid'               : '52f22c8af2291a13649baf23', 
        #                 'submission_time'   : datetime.datetime(2014, 2, 5, 12, 20, 26, 744000), 
        #                 'execution_details' : [u'localhost:3'], 
        #                 'stop_time'         : datetime.datetime(2014, 2, 5, 12, 20, 41, 890000), 
        #                 'start_time'        : datetime.datetime(2014, 2, 5, 12, 20, 40, 884000), 
        #                 'description'       : <sagapilot.compute_unit_description.ComputeUnitDescription object at 0x27ea990>}

        # register sagapilot events when they have a valid time stamp.  This may
        # register them multiple times though, but duplication is filtered out
        # on time keeping level
        if 'submission_time' in info and info['submission_time'] :
            unit.timed_event ('monitor', 'submission', 
                              tags  = ['sagapilot', 'submission_time'], 
                              timer = info['submission_time'])

        if 'start_time' in info and info['start_time'] :
            unit.timed_event ('monitor', 'start',  
                              tags  = ['sagapilot', 'start_time'], 
                              timer = info['start_time'])

        if 'stop_time' in info and info['stop_time'] :
            unit.timed_event ('monitor', 'stop',  
                              tags  = ['sagapilot', 'stop_time'], 
                              timer = info['stop_time'])

        if  info['state'] == FAILED :
            troy._logger.error ('CU %s failed' % unit.id)
            troy._logger.info ('log: \n----\n%s\n---\n' % info['log'])
            troy._logger.info ('stderr: \n----\n%s\n---\n' % info['stderr'])
            troy._logger.info ('stdout: \n----\n%s\n---\n' % info['stdout'])


        return info


    # --------------------------------------------------------------------------
    #
    def unit_cancel (self, unit) :
        """
        bye bye bye Junimond, es ist vorbei, bye bye...
        """

        [sp_um, sp_cu] = unit._get_instance ('sagapilot')
        sp_cu.cancel ()


# ------------------------------------------------------------------------------

