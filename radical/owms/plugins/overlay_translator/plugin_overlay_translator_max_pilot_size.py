
__author__    = "RADICAL Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils as ru

from   radical.owms.constants import *
import radical.owms

_DEFAULT_PILOT_SIZE = UNLIMITED

# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'          : 'overlay_translator',
    'name'          : 'max_pilot_size',
    'version'       : '0.1',
    'description'   : 'this translator creates n pilots of maximal size.',
    'configuration' : [('pilot size', 'INT as size of each pilot, or radical.owms.UNLIMITED" (default: UNLIMITED)')]
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (radical.owms.PluginBase):
    """
    This class implements the default overlay translator algorithm for
    radical.owms, which splits the requested overlay size over N pilots of configured
    size n.

    **Configuration Options:**

    * `pilot_size`: size for each pilot.  If the overlay size is not a multiple
      of `pilot_size`, the total number of cores will be larger than overlay
      size.  The pilot backend is expected to honor the pilot size, and not to
      create smaller or larger pilots.
      Example:

          "pilot_size" : 32
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        radical.owms.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def translate (self, overlay) :
        """
        check if the overlay's description has a size specified.  If so,
        translate that into the necessary number of pilots of the configured
        size.
        """


        # a pilot can be at max 8 cores large.  Yes, we made this up...
        if 'pilot_size' in self.cfg :
            pilot_size = int(self.cfg['pilot_size'])
        else :
            pilot_size = _DEFAULT_PILOT_SIZE

        if  pilot_size == UNLIMITED :
            # don't split the overlay at all
            pilot_size =  int(overlay.description.cores)

        radical.owms._logger.info ("overlay  translate: max pilot size set to %d" % pilot_size)

        pilot_cnt = 0
        while (pilot_cnt * pilot_size) < overlay.description.cores :

            pilot_descr = radical.owms.PilotDescription ({'size'     : pilot_size,
                                                  'walltime' : overlay.description.walltime})
            pilot_id    = overlay._add_pilot (pilot_descr)
            pilot_cnt  += 1
            radical.owms._logger.info ("overlay  translate: define   pilot %3d: %s (%s)" % (1, pilot_id, pilot_descr))


# ------------------------------------------------------------------------------

