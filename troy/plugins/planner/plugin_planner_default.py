# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'planner',
    'name'        : 'default',
    'version'     : '0.1',
    'description' : 'This is the default planner.'
  }

from overlay import Overlay
from overlay import PilotDescription

# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS(object):
    """
    This class implements the default planner for TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__(self):

        print "create the default planner plugin"

    # --------------------------------------------------------------------------
    #
    def derive_overlay(self, workload):

        # Create an overlay
        ovl = Overlay()

        # Add pilots into it
        for p in range(42):
            d = PilotDescription({'size':42})
            ovl.add_pilot(d)

        return ovl

#
# ------------------------------------------------------------------------------