

from   troy.constants import *
import troy
import time
import random

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

        troy._logger.info ("create the DEBUG overlay_translator plugin")


    # --------------------------------------------------------------------------
    #
    def translate (self, overlay) :
        print "########################################"
        print " making pilots of random sizes"
        print "########################################"

        # we simply use one pilot for te whole thing...
      # for i in range (0, overlay.description.cores) :
        for i in range(2):
            p_descr  = troy.PilotDescription ({'size' : random.randint(1,10)})
            pilot_id = overlay._add_pilot (p_descr)

        troy._logger.info ("overlay  translate: define   pilot %3d: %s" % (1, pilot_id))


# ------------------------------------------------------------------------------

