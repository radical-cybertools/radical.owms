

import radical.utils as ru

from   troy.constants import *
import troy

_DEFAULT_PILOT_SIZE = 8

# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'          : 'overlay_translator', 
    'name'          : 'max_pilot_size', 
    'version'       : '0.1',
    'description'   : 'this translator creates n pilots of maximal size.',
    'configuration' : [('pilot size', 'INT, size of each pilot (default: %d)' % _DEFAULT_PILOT_SIZE )]
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (troy.PluginBase):
    """
    This class implements the default overlay translator algorithm for
    TROY, which splits the requested overlay size over N pilots of configured
    size n.
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
            pilot_size = _DEFAULT_PILOT_SIZE

        troy._logger.info ("overlay  translate: max pilot size set to %d" % pilot_size(

        pilot_cnt = 0
        while (pilot_cnt * pilot_size) < overlay.description.cores :

            pilot_descr = troy.PilotDescription ({'size'      : pilot_size, 
                                                  'wall_time' : overlay.description.wall_time})
            pilot_id    = overlay._add_pilot (pilot_descr)
            pilot_cnt  += 1
            troy._logger.info ("overlay  translate: define   pilot %3d: %s (%s)" % (1, pilot_id, pilot_descr))


# ------------------------------------------------------------------------------

