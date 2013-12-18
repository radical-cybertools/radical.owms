
import os
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
    'name'        : 'sinon_pilot', 
    'version'     : '0.1',
    'description' : 'this is a plugin which provisions sinon pilots.'
  }

# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the sinon_pilot overlay provisioner forTROY.
    """

    __metaclass__ = ru.Singleton

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        self.description = PLUGIN_DESCRIPTION
        self.name        = "%(name)s_%(type)s" % self.description

    # --------------------------------------------------------------------------
    #
    def init (self, cfg):

        troy._logger.info ("init the sinon_pilot overlay provisioner plugin")
        
        self.cfg = cfg.as_dict ().get (self.name, {})

        self._db_url    = DBURL
        self.cp_service = sinon.PilotComputeService (self._coord)

        self._session = sinon.Session(database_url=DBURL)
        self._pmgr    = sinon.PilotManager(session=session, resource_configurations=FGCONF)

    # --------------------------------------------------------------------------
    #
    def provision (self, overlay) :

        # we simply assign all pilots to localhost
        for pid in overlay.pilots.keys() :
            pilot = overlay.pilots[pid]
 
            if  pilot.state not in [BOUND] :
                raise RuntimeError ("Can only provision pilots in BOUND state (%s)" % pilot.state)

            # FIXME: ceck state
            pilot_descr = sinon.ComputePilotDescription()
            pilot_descr.resource = pilot._resource
            pilot_descr.cores    = pilot.description['size']

            sinon_pilot = self._pmgr.submit_pilots(pilot_descr)

            pilot._set_instance (instance_type = 'sinon_pilot', 
                                 provisioner   = self, 
                                 instance      = sinon_pilot, 
                                 native_id     = sinon_pilot.uid())

            troy._logger.info ('overlay  provision: provision pilot  %s : %s ' \
                            % (pilot, pilot._get_instance ('sinon_pilot')))


    # --------------------------------------------------------------------------
    #
    def pilot_reconnect (self, native_id) :

        sinon_pilot = self._pmgr.get_pilots(pilot_ids=native_id)
        return sinon_pilot
 
    # --------------------------------------------------------------------------
    #
    def pilot_get_info (self, pilot) :
 
        # find out what we can about the pilot...
        sinon_pilot = pilot._get_instance ('bigjob_pilot')
 
        info     = dict ()
        bj_units = bj_pilot.list_compute_units ()
 
        info['units'] = dict ()
        for bj_unit in bj_units :
            unit = troy.ComputeUnit (_native_id=bj_unit.get_url (), _pilot_id=pilot.id)
            info['units'][unit.id] = unit
 
        # translate bj state to troy state
        # hahaha python switch statement hahahahaha
        info['state'] =  {"New"    : DESCRIBED, 
                          "Running": PROVISIONED, 
                          "Failed" : FAILED, 
                          "Done"   : DONE, 
                          "Unknown": UNKNOWN}.get (bj_pilot.get_state (), UNKNOWN)
 
        return info
 
 
    # --------------------------------------------------------------------------
    #
    def pilot_cancel (self, pilot) :
 
        pilot = pilot._get_instance ('sinon_pilot')
        sinon_pilot.cancel()


# ------------------------------------------------------------------------------

