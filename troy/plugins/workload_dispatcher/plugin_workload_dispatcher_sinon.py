

import sinon
import radical.utils as ru

from   troy.constants import *
import troy

DBURL  = 'mongodb://ec2-184-72-89-141.compute-1.amazonaws.com:27017/'
FGCONF = 'https://raw.github.com/saga-project/saga-pilot/master/configs/futuregrid.json'

# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_dispatcher', 
    'name'        : 'sinon', 
    'version'     : '0.1',
    'description' : 'this is a dispatcher which submits to sinon pilots.'
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

        troy._logger.info ("init the sinon workload dispatcher plugin")
        
        self._sinon  = sinon.Session (database_url = DBURL)


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
                pilot      = troy.Pilot (pilot_id, _instance_type='sinon')
                troy._logger.info ('workload dispatch : dispatch %-18s to %s' \
                                % (uid, pilot._get_instance('sinon')[1]))
                
                # translate our information into bigjob speak, and dispatch
                # a cu for the CU
                sinon_cu_descr = sinon.ComputeUnitDescription ()
                for key in unit_descr :

                    # ignore Troy level keys
                    if  key in ['tag'] :
                        continue

                    sinon_cu_descr[key] = unit_descr[key]

                # FIXME: sanity check for pilot type
                [sinon_um, sinon_pm, sinon_pilot] = pilot._get_instance ('sinon')
                sinon_cu = sinon_um.submit_units (sinon_cu_descr)

                # attach the backend instance to the unit, for later state
                # checks etc. We leave it up to the unit to decide if it wants
                # to cache the instance, or just the ID and then later
                # reconnect.
                unit._set_instance ('sinon', self, 
                                    instance  = [sinon_um,     sinon_cu],
                                    native_id = [sinon_um.uid, sinon_cu.uid])


    # --------------------------------------------------------------------------
    #
    def unit_reconnect (self, native_id) :
        """
        the unit lost the instance, and needs to reconnect...
        This is what is getting called on troy.Unit._get_instance, if that
        troy.Unit doesn't have that instance anymore...
        """

        troy._logger.debug ("reconnect to sinon cu %s" % native_id)
        sinon_um_id = native_id[0]
        sinon_cu_id = native_id[1]

        sinon_um    = self._sinon.get_unit_managers (sinon_um_id)
        sinon_cu    = sinon_um.get_units (sinon_cu_id)

        return [sinon_um, sinon_cu]


    # --------------------------------------------------------------------------
    #
    def unit_get_info (self, unit) :
        """
        unit inspection: get all possible information for the unit, and return
        in a dict.  This dict SHOULD contain 'state' at the very least -- but
        check the pilot_inspection unit test for more recommended attributes.
        """

        # find out what we can about the pilot...
        [sinon_um, sinon_cu] = unit._get_instance ('sinon')

        info = {'uid'              : sinon_cu.uid,
                'description'      : sinon_cu.description,
                'state'            : sinon_cu.state,
                'state_details'    : sinon_cu.state_details,
                'execution_details': sinon_cu.execution_details,
                'submission_time'  : sinon_cu.submission_time,
                'start_time'       : sinon_cu.start_time,
                'stop_time'        : sinon_cu.stop_time}


        # translate sinon state to troy state
        if  'state' in info :
            # hahaha python switch statement hahahahaha
            info['state'] =  {sinon.states.PENDING  : PENDING, 
                              sinon.states.RUNNING  : RUNNING, 
                              sinon.states.ACTIVE   : RUNNING, 
                              sinon.states.DONE     : DONE, 
                              sinon.states.CANCELED : CANCELED, 
                              sinon.states.FAILED   : FAILED, 
                              sinon.states.UNKNOWN  : UNKNOWN}.get (info['state'], UNKNOWN)

      # print 'unit_get_info: %s' % info

        return info


    # --------------------------------------------------------------------------
    #
    def unit_cancel (self, unit) :
        """
        bye bye bye Junimond, es ist vorbei, bye bye...
        """

        [sinon_um, sinon_cu] = unit._get_instance ('sinon')
        sinon_cu.cancel ()


# ------------------------------------------------------------------------------

