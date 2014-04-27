

import os
import radical.pilot     as rp
import radical.utils as ru
from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_dispatcher', 
    'name'        : 'radical.pilot', 
    'version'     : '0.1',
    'description' : 'this is a dispatcher which submits to radical.pilot pilots.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (troy.PluginBase):
    """
    This plugin dispatches workloads (and their compute units) to RADICAL-Pilot pilots,
    uring RADICAL-Pilot's pilot API.

    **Configuration Options:**

    * `coordination_url`: the redis URL to be used by RADICAL-Pilot.  The environment
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
            troy._logger.error ("No COORDINATION_URL set for radical.pilot backend")
            troy._logger.info  ("example: export COORDINATION_URL=redis://<pass>@gw68.quarry.iu.teragrid.org:6379")
            troy._logger.info  ("Contact Radica@Ritgers for the redis password")
            raise RuntimeError ("Cannot use radical.pilot backend - no COORDINATION_URL -- see debug log for details")

        self._sp  = rp.Session (database_url = self._coord)


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
                pilot      = troy.Pilot (self.session, pilot_id, _instance_type='radical.pilot')
                troy._logger.info ('workload dispatch : dispatch %-18s to %s' \
                                % (uid, pilot._get_instance('radical.pilot')[1]))
                
                # translate our information into radical.pilot speak, and dispatch
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

                rp_cu_descr = rp.ComputeUnitDescription ()
                for key in unit_descr :
                    if  key in keymap :
                        rp_cu_descr[keymap[key]] = unit_descr[key]


                # FIXME: sanity check for pilot type
                [rp_um, rp_pm, rp_pilot] = pilot._get_instance ('radical.pilot')
                rp_cu = rp_um.submit_units (rp_cu_descr)

                # attach the backend instance to the unit, for later state
                # checks etc. We leave it up to the unit to decide if it wants
                # to cache the instance, or just the ID and then later
                # reconnect.
                unit._set_instance ('radical.pilot', self, 
                                    instance  = [rp_um,     rp_cu],
                                    native_id = [rp_um.uid, rp_cu.uid])


    # --------------------------------------------------------------------------
    #
    def unit_reconnect (self, native_id) :
        """
        the unit lost the instance, and needs to reconnect...
        This is what is getting called on troy.Unit._get_instance, if that
        troy.Unit doesn't have that instance anymore...
        """

        troy._logger.debug ("reconnect to radical.pilot cu %s" % native_id)
        rp_um_id = native_id[0]
        rp_cu_id = native_id[1]

        rp_um    = self._sp.get_unit_managers (rp_um_id)
        rp_cu    = rp_um.get_units (rp_cu_id)

        return [rp_um, rp_cu]


    # --------------------------------------------------------------------------
    #
    def unit_get_info (self, unit) :
        """
        unit inspection: get all possible information for the unit, and return
        in a dict.  This dict SHOULD contain 'state' at the very least -- but
        check the pilot_inspection unit test for more recommended attributes.
        """

        # find out what we can about the pilot...
        [rp_um, rp_cu] = unit._get_instance ('radical.pilot')

        info = {'uid'              : rp_cu.uid,
                'description'      : rp_cu.description,
                'state'            : rp_cu.state,
                'stdout'           : rp_cu.stdout,
                'stderr'           : rp_cu.stderr,
                'log'              : rp_cu.log,
                'execution_details': rp_cu.execution_details,
                'submission_time'  : rp_cu.submission_time,
                'start_time'       : rp_cu.start_time,
                'stop_time'        : rp_cu.stop_time}


        # translate radical.pilot state to troy state
        if  'state' in info :
            troy._logger.debug ('radical.pilot level cu state: %s' % info['state'])
            # hahaha python switch statement hahahahaha
            info['state'] =  {rp.states.PENDING                 : PENDING, 
                              rp.states.PENDING_EXECUTION       : PENDING, 
                              rp.states.PENDING_INPUT_TRANSFER  : RUNNING, 
                              rp.states.TRANSFERRING_INPUT      : RUNNING, 
                              rp.states.RUNNING                 : RUNNING, 
                              rp.states.PENDING_OUTPUT_TRANSFER : RUNNING, 
                              rp.states.TRANSFERRING_OUTPUT     : RUNNING, 
                              rp.states.DONE                    : DONE, 
                              rp.states.CANCELED                : CANCELED, 
                              rp.states.FAILED                  : FAILED, 
                              rp.states.UNKNOWN                 : UNKNOWN}.get (info['state'], UNKNOWN)

      # print 'unit_get_info: %s' % info
        # unit_get_info: {'log'               : None, 
        #                 'state'             : 'Done', 
        #                 'uid'               : '52f22c8af2291a13649baf23', 
        #                 'submission_time'   : datetime.datetime(2014, 2, 5, 12, 20, 26, 744000), 
        #                 'execution_details' : [u'localhost:3'], 
        #                 'stop_time'         : datetime.datetime(2014, 2, 5, 12, 20, 41, 890000), 
        #                 'start_time'        : datetime.datetime(2014, 2, 5, 12, 20, 40, 884000), 
        #                 'description'       : <radical.pilot.compute_unit_description.ComputeUnitDescription object at 0x27ea990>}

        # register radical.pilot events when they have a valid time stamp.  This may
        # register them multiple times though, but duplication is filtered out
        # on time keeping level
        if 'submission_time' in info and info['submission_time'] :
            unit.timed_event ('monitor', 'submission', 
                              tags  = ['radical.pilot', 'submission_time'], 
                              timer = info['submission_time'])

        if 'start_time' in info and info['start_time'] :
            unit.timed_event ('monitor', 'start',  
                              tags  = ['radical.pilot', 'start_time'], 
                              timer = info['start_time'])

        if 'stop_time' in info and info['stop_time'] :
            unit.timed_event ('monitor', 'stop',  
                              tags  = ['radical.pilot', 'stop_time'], 
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

        [rp_um, rp_cu] = unit._get_instance ('radical.pilot')
        rp_cu.cancel ()


# ------------------------------------------------------------------------------

