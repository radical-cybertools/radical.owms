

import threading


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_translator', 
    'name'        : 'default', 
    'version'     : '0.1',
    'description' : 'this is an empty translator which basically does nothing.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the (empty) default workload translator for TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        print "create the default workload_translator plugin"


    # --------------------------------------------------------------------------
    #
    def translate (self, workload, overlay=None) :

        # make sure we have a simple with-scoped lock below
        if  overlay :
            overlay_lock = overlay.lock ()
        else :
            overlay_lock = threading.RLock ()


      # with workload.lock () and overlay.lock () :
            
            # for t in workload.tasks :
            #     t.compute_units = []
            #     t.compute_units[0] = t.description

            # do nothing
      #     pass


# ------------------------------------------------------------------------------

