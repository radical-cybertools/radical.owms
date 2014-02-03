

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

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :
        """
        invoked when plugin is loaded. Only do sanity checks, no other
        initialization
        """

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def init (self):
        """
        invoked by user of plugin, i.e. a overlay manager.  May get invoked
        multiple times -- plugins are singletons, and thus shared amongst all
        overlay managers!
        """

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
                unit_descr = unit.description
                pilot_id   = unit['pilot_id']

                # reconnect to the given pilot -- this is likely to pull the
                # instance from a cache, so should not cost too much.
                pilot      = troy.Pilot (pilot_id, _instance_type='sagapilot')
                troy._logger.info ('workload dispatch : dispatch %-18s to %s' \
                                % (uid, pilot._get_instance('sagapilot')[1]))
                
                # translate our information into bigjob speak, and dispatch
                # a cu for the CU
                sp_cu_descr = sp.ComputeUnitDescription ()
                for key in unit_descr :

                    # ignore Troy level keys
                    # FIXME: this should be a positive filter, not a negative
                    # one, to shield against evolving troy...
                    if  key in ['tag', 'inputs', 'outputs', 'stdin', 'stdout'] :
                        continue

                    elif key in ['working_directory'] :
                        sp_cu_descr['WorkingDirectoryPriv'] = unit_descr[key]

                    else :
                        sp_cu_descr[key] = unit_descr[key]


                # FIXME: sanity check for pilot type
                [sp_um, sp_pm, sp_pilot] = pilot._get_instance ('sp')
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
                'state_details'    : sp_cu.state_details,
                'execution_details': sp_cu.execution_details,
                'submission_time'  : sp_cu.submission_time,
                'start_time'       : sp_cu.start_time,
                'stop_time'        : sp_cu.stop_time}


        # translate sagapilot state to troy state
        if  'state' in info :
            # hahaha python switch statement hahahahaha
            info['state'] =  {sp.states.PENDING  : PENDING, 
                              sp.states.RUNNING  : RUNNING, 
                              sp.states.ACTIVE   : RUNNING, 
                              sp.states.DONE     : DONE, 
                              sp.states.CANCELED : CANCELED, 
                              sp.states.FAILED   : FAILED, 
                              sp.states.UNKNOWN  : UNKNOWN}.get (info['state'], UNKNOWN)

      # print 'unit_get_info: %s' % info

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

