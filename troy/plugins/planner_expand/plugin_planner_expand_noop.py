
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils as ru

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'expand',
    'name'        : 'noop',
    'version'     : '0.1',
    'description' : 'This is the default workload expander, which does nothing'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (troy.PluginBase):
    """
    This plugin leaves the workload unchanged.
    
    **Configuration Options:** None
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__(self):

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def expand_workload(self, workload):
        """
        Do nothing.
        """

        troy._logger.info ("planner  expand wl: noop expand workload : %s" % workload)


# ------------------------------------------------------------------------------

