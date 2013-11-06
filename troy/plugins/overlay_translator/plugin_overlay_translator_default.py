

from   troy.constants import *


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'overlay_translator', 
    'name'        : 'default', 
    'version'     : '0.1',
    'description' : 'this is an empty trabslator which is stupid.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the (stupid) default overlay translator algorithm for
    TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        print "create the default overlay_translator plugin"


    # --------------------------------------------------------------------------
    #
    def translate (self, overlay) :

        # we simply use one pilot for te whole thing...
        for i in range (0, overlay.description.cores) :
            p_descr = to.PilotDescription ({'size' : 1})
            pilot   = to.Pilot (p_descr)
            print "overlay  translate: define   pilot %3d: %s" % (i, pilot)
            overlay._add_pilot (pilot)


# ------------------------------------------------------------------------------

