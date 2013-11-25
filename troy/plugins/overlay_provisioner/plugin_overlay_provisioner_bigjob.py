
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

_idx = 0

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

        troy._logger.info ("create the bigjob overlay_provisioner plugin")

        if  not 'COORDINATION_URL' in os.environ :
            raise RuntimeError ("Cannot use bigjob backend - no CCORDINATION_URL set")

        self._coord = os.environ['COORDINATION_URL']


    # --------------------------------------------------------------------------
    #
    def provision (self, overlay) :

        # we simply assign all pilots to localhost
        for pid in overlay.pilots.keys() :
            pilot = overlay.pilots[pid]
 
            if  pilot.state not in [BOUND] :
                raise RuntimeError ("Can only provision pilots in BOUND state (%s)" % pilot.state)

            global _idx
            
            # FIXME: ceck state
            bj_manager     = bigjob.bigjob (coordination_url=self._coord)
            bj_manager_url = bj_manager.get_url ()
            bj_pilot_url   = bj_manager.start_pilot_job (pilot._resource)

            _idx += 1

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

