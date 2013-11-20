

from   troy.constants import *


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'overlay_scheduler', 
    'name'        : 'default', 
    'version'     : '0.1',
    'description' : 'this is an empty scheduler which basically does nothing.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the (empty) default overlay scheduler algorithm for
    TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        print "create the default overlay_scheduler plugin"


    # --------------------------------------------------------------------------
    #
    def schedule (self, overlay) :

        # we simply assign all pilots to localhost
        for pid in overlay.pilots.keys() :
            pilot = overlay.pilots[pid]
            print 'overlay  schedule : schedule pilot %s to localost' % pilot.id
            pilot._bind ('ssh://localhost')


# ------------------------------------------------------------------------------

