

import os
import bigjob
import radical.utils as ru

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

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        self.description = PLUGIN_DESCRIPTION
        self.name        = "%(name)s_%(type)s" % self.description

        raise RuntimeError ("Plugin is disabled")


    # --------------------------------------------------------------------------
    #
    def init (self, cfg):

        self._coord = None

        if  'COORDINATION_URL' in os.environ :
            self._coord = os.environ['COORDINATION_URL'] 

        elif 'coordination_url' in self.cfg :
            self._coord = self.cfg['coordination_url']

        else :
            troy._logger.error ("No COORDINATION_URL set for bigjob_pilot backend")
            troy._logger.info  ("example: export COORDINATION_URL=redis://<pass>@gw68.quarry.iu.teragrid.org:6379")
            troy._logger.info  ("Contact Radica@Ritgers for the redis password")
            raise RuntimeError ("Cannot use bigjob_pilot backend - no COORDINATION_URL -- see debug log for details")

        self.cfg = cfg.as_dict ().get (self.name, {})


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
            bj_pilot_url   = bj_manager.start_pilot_job (pilot.resource)

            pilot._set_instance ('bigjob', self, [bj_pilot_url, bj_manager], bj_manager.get_url ())

            troy._logger.info ('overlay  provision: provision pilot  %s : %s ' \
                            % (pilot, pilot._get_instance ('bigjob')))


    # --------------------------------------------------------------------------
    #
    def pilot_reconnect (self, native_id) :

        bj_manager     = bigjob.bigjob (coordination_url=self._coord, 
                                        pilot_url=native_id)
        bj_manager_url = bj_manager.get_url ()
        bj_pilot_url   = ru.Url (bj_manager_url).path[1:]

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

