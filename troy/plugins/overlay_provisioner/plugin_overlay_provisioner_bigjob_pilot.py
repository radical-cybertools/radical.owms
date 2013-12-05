
import os
import saga
import pilot as pilot_module
import weakref

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'overlay_provisioner', 
    'name'        : 'bigjob_pilot', 
    'version'     : '0.1',
    'description' : 'this is a scheduler which provisions bigjob pilots.'
  }

# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the bigjob_pilot overlay provisioner for
    TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        self.description = PLUGIN_DESCRIPTION
        self.name        = "%(name)s_%(type)s" % self.description


    # --------------------------------------------------------------------------
    #
    def init (self, cfg):

        troy._logger.info ("init the bigjob_pilot overlay provisioner plugin")
        
        self.cfg = cfg.as_dict ().get (self.name, {})

        if  not 'COORDINATION_URL' in os.environ :
            troy._logger.error ("No COORDINATION_URL set for bigjob_pilot backend")
            troy._logger.info  ("example: export COORDINATION_URL=redis://<pass>@gw68.quarry.iu.teragrid.org:6379")
            troy._logger.info  ("Contact Radica@Ritgers for the redis password")
            raise RuntimeError ("Cannot use bigjob_pilot backend - no COORDINATION_URL set -- see debug log for details")

        self._coord     = os.environ['COORDINATION_URL'] 
        self.cp_service = pilot_module.PilotComputeService (self._coord)


    # --------------------------------------------------------------------------
    #
    def provision (self, overlay) :

        # we simply assign all pilots to localhost
        for pid in overlay.pilots.keys() :
            pilot = overlay.pilots[pid]
 
            if  pilot.state not in [BOUND] :
                raise RuntimeError ("Can only provision pilots in BOUND state (%s)" % pilot.state)

            # FIXME: ceck state
            pilot_descr = pilot_module.PilotComputeDescription ()
            pilot_descr.service_url         = pilot._resource
            pilot_descr.number_of_processes = pilot.description['size']

            bj_pilot = self.cp_service.create_pilot (pilot_descr)

            pilot._set_instance (instance_type = 'bigjob_pilot', 
                                 provisioner   = self, 
                                 instance      = bj_pilot, 
                                 native_id     = bj_pilot.get_url ())

            troy._logger.info ('overlay  provision: provision pilot  %s : %s ' \
                            % (pilot, pilot._get_instance ('bigjob_pilot')))


    # --------------------------------------------------------------------------
    #
    def pilot_reconnect (self, native_id) :

        bj_pilot = pilot_module.PilotCompute (pilot_url=native_id)

        return bj_pilot
 
 
    # --------------------------------------------------------------------------
    #
    def pilot_get_info (self, pilot) :
 
 
        # find out what we can about the pilot...
        bj_pilot= pilot._get_instance ('bigjob_pilot')
 
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
 
        bj_pilot = pilot._get_instance ('bigjob_pilot')
        bj_pilot.cancel ()


# ------------------------------------------------------------------------------

