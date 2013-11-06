

from   troy.constants import *


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_dispatcher', 
    'name'        : 'default', 
    'version'     : '0.1',
    'description' : 'this is an empty dispatcher which basically does nothing.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the (empty) default workload dispatcher for TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        print "create the default workload_dispatcher plugin"


    # --------------------------------------------------------------------------
    #
    def dispatch (self, workload, overlay) :

        # do nothing
        pass


# ------------------------------------------------------------------------------

