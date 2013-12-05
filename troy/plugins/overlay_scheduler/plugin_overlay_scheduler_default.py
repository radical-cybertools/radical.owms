

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'overlay_scheduler', 
    'name'        : 'default', 
    'version'     : '0.1',
    'description' : 'this is an empty scheduler which basically does nothing.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the (empty) default overlay scheduler algorithm for
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

        troy._logger.info ("init the default overlay scheduler plugin")
        
        self.cfg = cfg.as_dict ().get (self.name, {})


    # --------------------------------------------------------------------------
    #
    def schedule (self, overlay) :

        # we simply assign all pilots to localhost
        for pid in overlay.pilots.keys() :

            pilot = overlay.pilots[pid]
            pilot._bind ('fork://localhost')

            troy._logger.info ('overlay  schedule : schedule pilot %s to localhost' % pilot.id)


# ------------------------------------------------------------------------------

