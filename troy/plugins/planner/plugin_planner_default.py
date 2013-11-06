# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'planner',
    'name'        : 'default',
    'version'     : '0.1',
    'description' : 'This is the default planner.'
  }

from overlay import Overlay


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
    def expand_workload(self, workload):

        # Do nothing for now
        pass

    # --------------------------------------------------------------------------
    #
    def derive_overlay(self, workload):

        # Create an overlay
        ovl = Overlay()

        # Ask for as many pilots as tasks
        ovl.cores = len(workload.tasks)

        # Minutes obviously
        ovl.wall_time = (1 << 1) + (1 << 3) + (1 << 5)

        return ovl

#
# ------------------------------------------------------------------------------
