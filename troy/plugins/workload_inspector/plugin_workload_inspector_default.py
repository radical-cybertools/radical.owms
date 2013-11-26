

import threading

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_inspector', 
    'name'        : 'default', 
    'version'     : '0.1',
    'description' : 'this is an empty inspector which basically does nothing.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the (empty) default workload inspector for TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        troy._logger.info ("create the default workload_inspector plugin")


    # --------------------------------------------------------------------------
    #
    def inspect (self, workload) :

        troy._logger.info ('workload inspect : inspect workload ;)')
        return workload


# ------------------------------------------------------------------------------

