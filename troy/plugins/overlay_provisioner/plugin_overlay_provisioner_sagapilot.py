

import os
import saga
import getpass
import sagapilot     as sp
import radical.utils as ru
from   troy.constants import *
import troy


FGCONF    = 'https://raw.github.com/saga-project/saga-pilot/master/configs/futuregrid.json'
TROY_CONF = "file://localhost/%s/resource.py" % os.path.dirname (troy.__file__)


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'overlay_provisioner', 
    'name'        : 'sagapilot', 
    'version'     : '0.1',
    'description' : 'this is a plugin which provisions sagapilot pilots.'
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

        for pid in overlay.pilots.keys() :

            troy_pilot = overlay.pilots[pid]
 
            # only BOUND pilots have a target resource assigned.
            if  troy_pilot.state not in [BOUND] :
                raise RuntimeError ("Can only provision BOUND pilots (%s)" % troy_pilot.state)

            # translate information into sagapilot speak
            pilot_descr          = sp.ComputePilotDescription()
            pilot_descr.resource = troy_pilot.resource
            pilot_descr.cores    = troy_pilot.description['size']

            resource_url = saga.Url (troy_pilot.resource)
            userid       = getpass.getuser()
            home         = os.environ['HOME']
            queue        = None
            walltime     = 24 * 60 # 1 day as default

            troy._logger.info ('overlay  provision: provision   pilot  %s : %s ' \
                            % (pid, resource_url))

            # FIXME: 
            for key in self.global_cfg.keys () :

                if  key.startswith ('compute:')        and \
                    'sagapilot_id' in self.global_cfg[key] and \
                    self.global_cfg[key]['endpoint'] == resource_url.host :

                    pilot_descr.resource = self.global_cfg[key]['sagapilot_id']

                    userid   = self.global_cfg[key].get ('username', userid)
                    home     = self.global_cfg[key].get ('home',     home)
                    queue    = self.global_cfg[key].get ('queue',    queue)
                    walltime = self.global_cfg[key].get ('walltime', walltime)

                    break

            pilot_descr.working_directory = "%s/troy_agents/" % home
            pilot_descr.queue    = queue

            pilot_descr.run_time = 300

            sp_um    = sp.UnitManager  (session   = self._sp, 
                                              scheduler = 'direct_submission')
            sp_pm    = sp.PilotManager (session   = self._sp, 
                                              resource_configurations = TROY_CONF)
            sp_pilot = sp_pm.submit_pilots (pilot_descr)


            sp_um.add_pilots (sp_pilot)

            troy_pilot._set_instance (instance_type = 'sagapilot', 
                                      provisioner   = self, 
                                      instance      = [sp_um,     sp_pm,     sp_pilot], 
                                      native_id     = [sp_um.uid, sp_pm.uid, sp_pilot.uid])

            troy._logger.info ('overlay  provision: provisioned pilot  %s : %s (%s)' \
                            % (troy_pilot, 
                               troy_pilot._get_instance ('sagapilot')[2], 
                               troy_pilot.resource))


    # --------------------------------------------------------------------------
    #
    def pilot_reconnect (self, native_id) :
        """
        the pilot lost the instance, and needs to reconnect...
        This is what is getting called on troy.Pilot._get_instance, if that
        troy.Pilot doesn't have that instance anymore...
        """

        sp_um_id    = native_id[0]
        sp_pm_id    = native_id[1]
        sp_pilot_id = native_id[2]

        sp_um       = self._sp.get_unit_managers  (sp_um_id)
        sp_pm       = self._sp.get_pilot_managers (sp_pm_id)
        sp_pilot    = sp_pm.get_pilots            (sp_pilot_id)

        return [sp_um, sp_pm, sp_pilot]
    
 
    # --------------------------------------------------------------------------
    #
    def pilot_get_info (self, pilot) :
        """
        pilot inspection: get all possible information for the pilot, and return
        in a dict.  This dict SHOULD contain 'state' at the very least -- but
        check the pilot_inspection unit test for more recommended attributes.
        """
 
 
        # find out what we can about the pilot...
        [sp_um, sp_pm, sp_pilot] = pilot._get_instance ('sagapilot')

        info = {
                'uid'              : sp_pilot.uid, 
                'description'      : sp_pilot.description, 
                'state'            : sp_pilot.state, 
                'state_details'    : sp_pilot.state_details, 
                'resource_details' : sp_pilot.resource_details, 
                'unit_ids'         : dict(),
              # 'unit_ids'         : sp_pilot.units,  # FIXME
              # 'unit_managers'    : sp_pilot.unit_managers, 
                'pilot_manager'    : sp_pilot.pilot_manager, 
                'submission_time'  : sp_pilot.submission_time, 
                'start_time'       : sp_pilot.start_time, 
                'stop_time'        : sp_pilot.stop_time}
        
      # # FIXME
      # for sp_unit_id in sp_pilot.units :
      #     
      #     unit = troy.ComputeUnit (_native_id=[sp_um.uid, sp_unit_id], 
      #                              _pilot_id=pilot.id)
      #     info['units'][unit.id] = unit
 
        # translate sagapilot state to troy state
        # hahaha python switch statement hahahahaha
        info['state'] =  {sp.states.PENDING  : PROVISIONED, 
                          sp.states.RUNNING  : PROVISIONED, 
                          sp.states.ACTIVE   : PROVISIONED, 
                          sp.states.DONE     : COMPLETED, 
                          sp.states.CANCELED : CANCELED, 
                          sp.states.FAILED   : FAILED, 
                          sp.states.UNKNOWN  : UNKNOWN}.get (sp_pilot.state, UNKNOWN)
 
        return info
 
 
    # --------------------------------------------------------------------------
    #
    def pilot_cancel (self, pilot) :
 
        [sp_um, sp_pm, sp_pilot] = pilot._get_instance ('sagapilot')
        sp_pilot.cancel ()


# ------------------------------------------------------------------------------

