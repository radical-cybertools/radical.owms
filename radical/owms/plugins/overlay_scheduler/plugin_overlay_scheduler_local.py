

import radical.utils as ru

from   radical.owms.constants import *
import radical.owms


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'overlay_scheduler', 
    'name'        : 'local', 
    'version'     : '0.1',
    'description' : 'this is a scheduler which assigns al pilots to localhost.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (radical.owms.PluginBase):
    """
    This plugin schedules all pilots on `localhost`.

    **Configuration Options:** None
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        radical.owms.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def schedule (self, overlay) :
        """
        we simply assign all pilots to localhost
        """

        for pid in overlay.pilots.keys() :

            pilot = overlay.pilots[pid]
            pilot._bind ('fork://localhost')

            radical.owms._logger.info ('overlay  schedule : schedule pilot %s to localhost' % pilot.id)


# ------------------------------------------------------------------------------

