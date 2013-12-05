

import os
import saga
import bigjob
import weakref

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'overlay_provisioner', 
    'name'        : 'bigjob', 
    'version'     : '0.1',
    'description' : 'this is a scheduler which provisions bigjob pilots.'
  }

# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the bigjob overlay provisioner for
    TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        self.description = PLUGIN_DESCRIPTION
        self.name        = self.description['name']

        raise RuntimeError ("Plugin is disabled")


    # --------------------------------------------------------------------------
    #
    def init (self, cfg):

        troy._logger.info ("init the bigjob overlay provisioner plugin")

        if  not 'COORDINATION_URL' in os.environ :
            troy._logger.error ("No COORDINATION_URL set for bigjob backend")
            troy._logger.info  ("example: export COORDINATION_URL=redis://<pass>@gw68.quarry.iu.teragrid.org:6379")
            troy._logger.info  ("Contact Radica@Ritgers for the redis password")
            raise RuntimeError ("Cannot use bigjob backend - no COORDINATION_URL set -- see debug log for details")

        self._coord = os.environ['COORDINATION_URL']

        self.cfg = cfg


    # --------------------------------------------------------------------------
    #
    def provision (self, overlay) :

        # we simply assign all pilots to localhost
        for pid in overlay.pilots.keys() :
            pilot = overlay.pilots[pid]
 
            if  pilot.state not in [BOUND] :
                raise RuntimeError ("Can only provision pilots in BOUND state (%s)" % pilot.state)

            # FIXME: ceck state
            bj_manager     = bigjob.bigjob (coordination_url=self._coord)
            bj_manager_url = bj_manager.get_url ()
            bj_pilot_url   = bj_manager.start_pilot_job (pilot._resource)

            pilot._set_instance ('bigjob', self, [bj_pilot_url, bj_manager], bj_manager.get_url ())

            troy._logger.info ('overlay  provision: provision pilot  %s : %s ' \
                            % (pilot, pilot._get_instance ('bigjob')))


    # --------------------------------------------------------------------------
    #
    def pilot_reconnect (self, native_id) :

        bj_manager     = bigjob.bigjob (coordination_url=self._coord, 
                                        pilot_url=native_id)
        bj_manager_url = bj_manager.get_url ()
        bj_pilot_url   = saga.Url (bj_manager_url).path[1:]

        return [bj_pilot_url, bj_manager]


    # --------------------------------------------------------------------------
    #
    def pilot_get_info (self, pilot) :


        # find out what we can about the pilot...
        bj_pilot_url, bj_manager = pilot._get_instance ('bigjob')

        info     = bj_manager.get_details ()
        unit_ids = bj_manager.list_subjobs ()

        info['units'] = dict ()
        for unit_id in unit_ids :
            cu = troy.ComputeUnit (_native_id=unit_id, _pilot_id=pilot.id)
            info['units'][unit_id] = cu

        # translate bj state to troy state
        if  'state' in info :
            # hahaha python switch statement hahahahaha
            info['state'] =  {"New"    : DESCRIBED, 
                              "Running": PROVISIONED, 
                              "Failed" : FAILED, 
                              "Done"   : DONE, 
                              "Unknown": UNKNOWN}.get (info['state'], UNKNOWN)

        return info


    # --------------------------------------------------------------------------
    #
    def pilot_cancel (self, pilot) :

        bj_pilot_url, bj_manager = pilot._get_instance ('bigjob')
        bj_manager.cancel ()


# ------------------------------------------------------------------------------

