
__author__    = "RADICAL Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils as ru

from   radical.owms.constants import *
import radical.owms


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_expander',
    'name'        : 'noop',
    'version'     : '0.1',
    'description' : 'This is the default workload expander, which does nothing'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (radical.owms.PluginBase):
    """
    This plugin leaves the workload unchanged.
    
    **Configuration Options:** None
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__(self):

        radical.owms.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def expand_workload(self, workload):
        """
        Do nothing.
        """

        radical.owms._logger.info ("expand workload: noop: %s" % workload)


# ------------------------------------------------------------------------------

