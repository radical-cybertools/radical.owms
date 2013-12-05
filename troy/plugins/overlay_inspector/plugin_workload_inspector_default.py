

import threading

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'overlay_inspector', 
    'name'        : 'default', 
    'version'     : '0.1',
    'description' : 'this is an empty inspector which basically does nothing.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the (empty) default overlay inspector for TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        self.description = PLUGIN_DESCRIPTION
        self.name        = self.description['name']


    # --------------------------------------------------------------------------
    #
    def init (self, cfg):

        troy._logger.info ("init the default overlay inspector plugin")
        self.cfg = cfg


    # --------------------------------------------------------------------------
    #
    def inspoect (self, overlay) :

        return overlay


# ------------------------------------------------------------------------------

