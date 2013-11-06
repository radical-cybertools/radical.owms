# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'planner',
    'name'        : 'default',
    'version'     : '0.1',
    'description' : 'This is the default planner.'
  }

import troy.overlay as to


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

        ovl_descr = to.OverlayDescription ( 
            {
                # Ask for as many pilots as tasks
                'cores' : len(workload.tasks), 
                # Minutes obviously
                'wall_time' : (1 << 1) + (1 << 3) + (1 << 5)
            })

        ovl_descr._attributes_dump ()

        # Create an overlay
        return to.Overlay(ovl_descr)


# ------------------------------------------------------------------------------

