
# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_scheduler', 
    'name'        : 'default', 
    'version'     : '0.1',
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


    # --------------------------------------------------------------------------
    #
    def schedule (self, workload, overlay) :

        pass
      # with workload.lock and overlay.lock () :

            # do nothing
      #     pass


# ------------------------------------------------------------------------------

