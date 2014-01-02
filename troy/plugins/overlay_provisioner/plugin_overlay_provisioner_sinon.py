

import os
import saga
import sinon
import radical.utils as ru

from   troy.constants import *
import troy


DBURL  = 'mongodb://ec2-184-72-89-141.compute-1.amazonaws.com:27017/'
FGCONF = 'https://raw.github.com/saga-project/saga-pilot/master/configs/futuregrid.json'


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'overlay_provisioner', 
    'name'        : 'sinon', 
    'version'     : '0.1',
    'description' : 'this is a plugin which provisions sinon pilots.'
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

        troy._logger.info ("init the sinon overlay provisioner plugin")
        
        self._sinon  = sinon.Session (database_url = DBURL)


    # --------------------------------------------------------------------------
    #
    def provision (self, overlay) :
        """
        provision a given overlay -- inspect that overlay, dig out the pilots
        and their description, check state, and instantiate them via the backend
        system.

        For each pilot, we need to also keep the pilot manager and the unit
        manager -- otherwise we are not able to reconnec to to pilots and units.
        So whenever a pilot is created, we immediately also create a unit
        manager, ad pass it around with the PM and pilot instance.
        """

        # we simply assign all pilots to localhost
        for pid in overlay.pilots.keys() :

            troy_pilot = overlay.pilots[pid]
 
            # only BOUND pilots have a target resource assigned.
            if  troy_pilot.state not in [BOUND] :
                raise RuntimeError ("Can only provision BOUND pilots (%s)" % troy_pilot.state)

            # translate information into sinon speak
            sinon_pilot_descr          = sinon.ComputePilotDescription()
            sinon_pilot_descr.resource = saga.Url (troy_pilot._resource).host
            sinon_pilot_descr.cores    = troy_pilot.description['size']

            sinon_pilot_descr.run_time          = 0  # FIXME
            sinon_pilot_descr.working_directory = "/tmp/sinon"  # FIXME

            sinon_um    = sinon.UnitManager  (session   = self._sinon, 
                                              scheduler = 'direct_submission')
            sinon_pm    = sinon.PilotManager (session   = self._sinon, 
                                              resource_configurations = FGCONF)
            sinon_pilot = sinon_pm.submit_pilots (sinon_pilot_descr)

            sinon_um.add_pilots (sinon_pilot)

            troy_pilot._set_instance (instance_type = 'sinon', 
                                 provisioner   = self, 
                                 instance      = [sinon_um,     sinon_pm,     sinon_pilot], 
                                 native_id     = [sinon_um.uid, sinon_pm.uid, sinon_pilot.uid])

            troy._logger.info ('overlay  provision: provision pilot  %s : %s ' \
                            % (troy_pilot, troy_pilot._get_instance ('sinon')[2]))


    # --------------------------------------------------------------------------
    #
    def pilot_reconnect (self, native_id) :
        """
        the pilot lost the instance, and needs to reconnect...
        This is what is getting called on troy.Pilot._get_instance, if that
        troy.Pilot doesn't have that instance anymore...
        """

        sinon_um_id    = native_id[0]
        sinon_pm_id    = native_id[1]
        sinon_pilot_id = native_id[2]

        sinon_um       = self._sinon.get_unit_managers  (sinon_um_id)
        sinon_pm       = self._sinon.get_pilot_managers (sinon_pm_id)
        sinon_pilot    = sinon_pm.get_pilots            (sinon_pilot_id)

        return [sinon_um, sinon_pm, sinon_pilot]
    
 
    # --------------------------------------------------------------------------
    #
    def pilot_get_info (self, pilot) :
        """
        pilot inspection: get all possible information for the pilot, and return
        in a dict.  This dict SHOULD contain 'state' at the very least -- but
        check the pilot_inspection unit test for more recommended attributes.
        """
 
 
        # find out what we can about the pilot...
        [sinon_um, sinon_pm, sinon_pilot] = pilot._get_instance ('sinon')

        info = {
                'uid'              : sinon_pilot.uid, 
                'description'      : sinon_pilot.description, 
                'state'            : sinon_pilot.state, 
                'state_details'    : sinon_pilot.state_details, 
                'resource_details' : sinon_pilot.resource_details, 
                'unit_ids'         : dict(),
              # 'unit_ids'         : sinon_pilot.units,  # FIXME
              # 'unit_managers'    : sinon_pilot.unit_managers, 
                'pilot_manager'    : sinon_pilot.pilot_manager, 
                'submission_time'  : sinon_pilot.submission_time, 
                'start_time'       : sinon_pilot.start_time, 
                'stop_time'        : sinon_pilot.stop_time}
        
      # # FIXME
      # for sinon_unit_id in sinon_pilot.units :
      #     
      #     unit = troy.ComputeUnit (_native_id=[sinon_um.uid, sinon_unit_id], 
      #                              _pilot_id=pilot.id)
      #     info['units'][unit.id] = unit
 
        # translate sinon state to troy state
        # hahaha python switch statement hahahahaha
        info['state'] =  {sinon.states.PENDING  : PROVISIONED, 
                          sinon.states.RUNNING  : PROVISIONED, 
                          sinon.states.ACTIVE   : PROVISIONED, 
                          sinon.states.DONE     : COMPLETED, 
                          sinon.states.CANCELED : CANCELED, 
                          sinon.states.FAILED   : FAILED, 
                          sinon.states.UNKNOWN  : UNKNOWN}.get (sinon_pilot.state, UNKNOWN)
 
        return info
 
 
    # --------------------------------------------------------------------------
    #
    def pilot_cancel (self, pilot) :
 
        [sinon_um, sinon_pm, sinon_pilot] = pilot._get_instance ('sinon')
        sinon_pilot.cancel ()


# ------------------------------------------------------------------------------

