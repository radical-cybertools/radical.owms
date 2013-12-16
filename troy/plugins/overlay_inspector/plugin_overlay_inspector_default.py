

import radical.utils as ru

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
class PLUGIN_CLASS (troy.PluginBase):
    """
    This class implements the (empty) default overlay inspector for TROY.
    """

    __metaclass__ = ru.Singleton
    
    
    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def inspoect (self, overlay) :

        return overlay


# ------------------------------------------------------------------------------

