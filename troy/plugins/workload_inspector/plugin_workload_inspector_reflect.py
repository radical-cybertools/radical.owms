

import radical.utils as ru

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_inspector', 
    'name'        : 'reflect', 
    'version'     : '0.1',
    'description' : 'this is an empty inspector which basically does nothing.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (troy.PluginBase):

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def inspect (self, workload) :

        troy._logger.info ('workload inspect : inspect workload ;)')
        return workload


# ------------------------------------------------------------------------------

