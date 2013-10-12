
# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_scheduler', 
    'name'        : 'default', 
    'version'     : '0.1',
    'type'        : 'workload_scheduler', 
    'description' : 'this is an empty scheduler which basically does nothing.'
  }

# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the (empty) default workload scheduler algorithm for
    TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        print "create the default workload_scheduler plugin"

        self._workload = None
        self._overlay  = None


    # --------------------------------------------------------------------------
    #
    def init (self, workload, overlay) :

        self._workload = workload
        self._overlay  = overlay



    # --------------------------------------------------------------------------
    #
    def run (self) :

        # do nothing
        return self._workload


