

import radical.utils as ru

from   troy.constants import *
import troy


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
class PLUGIN_CLASS (troy.PluginBase):
    """
    This class implements the (stupid) default overlay translator algorithm for
    TROY.
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def translate (self, overlay) :


        # a pilot can be at max 8 cores large.  Yes, we made this up...
        if 'pilot_size' in self.cfg :
            pilot_size = int(self.cfg['pilot_size'])
        else :
            pilot_size = 8

        pilot_cnt = 0
        while (pilot_cnt * pilot_size) < overlay.description.cores :

            pilot_descr = troy.PilotDescription ({'size' : pilot_size})
            pilot_id    = overlay._add_pilot (pilot_descr)
            pilot_cnt  += 1
            troy._logger.info ("overlay  translate: define   pilot %3d: %s (%s)" % (1, pilot_id, pilot_descr))


# ------------------------------------------------------------------------------

