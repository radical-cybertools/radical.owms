

# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'name'        : 'round_robin', 
    'version'     : '0.1',
    'type'        : 'workload_scheduler', 
    'description' : 'simple scheduler, assigns CUs to pilots in round-robin fashion.'
  }

# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the (trivial) round-robin workload scheduler algorithm for
    TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self, *args, **kwargs) :

        print "initializing the round-robin workload_scheduler plugin (%s) (%s)" \
            % (args, kwargs)

        self._workload = None
        self._overlay  = None

        if 'workload' in kwargs :
            self._workload = kwargs['workload']
        elif len (args) :
            self._workload = args[0]
        else :
            print "no workload given?  Duh!"


        if 'overlay' in kwargs :
            self._overlay = kwargs['overlay']
        elif len (args) :
            self._overlay = args[0]
        else :
            print "no overlay  given?  Duh!"


    # --------------------------------------------------------------------------
    #
    def run () :
        # do nothing
        return self._workload


