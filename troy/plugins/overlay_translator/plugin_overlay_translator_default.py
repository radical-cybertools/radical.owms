

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'overlay_translator', 
    'name'        : 'default', 
    'version'     : '0.1',
    'description' : 'this is an empty trabslator which is stupid.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the (stupid) default overlay translator algorithm for
    TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        pass


    # --------------------------------------------------------------------------
    #
    def init (self, cfg):

        troy._logger.info ("init the default overlay translator plugin")
        self.cfg = cfg


    # --------------------------------------------------------------------------
    #
    def translate (self, overlay) :

        # we simply use one pilot for te whole thing...
      # for i in range (0, overlay.description.cores) :
        p_descr  = troy.PilotDescription ({'size' : 1})
        pilot_id = overlay._add_pilot (p_descr)
        troy._logger.info ("overlay  translate: define   pilot %3d: %s" % (1, pilot_id))


# ------------------------------------------------------------------------------

