
# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
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
    def __init__ (self, *args, **kwargs) :

        print "initializing the default workload_scheduler plugin (%s) (%s)" \
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
    def run (self) :

        # do nothing
        return self._workload


