

import radical.utils as ru

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'overlay_scheduler', 
    'name'        : 'round_robin', 
    'version'     : '0.1',
    'description' : 'this is an empty scheduler which basically does nothing.'
  }

_idx = 0

# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the (empty) round_robin overlay scheduler algorithm for
    TROY.
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

        troy._logger.info ("init the round_robin overlay scheduler plugin")
        
        self.cfg = cfg.as_dict ().get (self.name, {})

        if 'resources'    in self.cfg :
            self.resources = self.cfg['resources'].split (',')
        else :
            self.resources = ['fork://localhost']


    # --------------------------------------------------------------------------
    #
    def schedule (self, overlay) :

        global _idx

        for pid in overlay.pilots.keys() :

            if  _idx >= len(self.resources) :
                _idx  = 0

            resource  = self.resources[_idx]
            _idx     += 1

            pilot = overlay.pilots[pid]
            pilot._bind (resource)

            troy._logger.info ('overlay  schedule : schedule pilot %s to %s' % (resource, pilot.id))


# ------------------------------------------------------------------------------

