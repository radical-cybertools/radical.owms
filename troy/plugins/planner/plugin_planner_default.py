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
    def derive_overlay(self, workload):

        #with workload.lock:

            # do nothing
            #pass


        ovl = Overlay()

        return ovl


#
# ------------------------------------------------------------------------------