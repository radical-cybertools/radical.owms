

import radical.utils as ru

from   radical.owms.constants import *
import radical.owms


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'overlay_scheduler', 
    'name'        : 'round_robin', 
    'version'     : '0.1',
    'description' : 'this is an empty scheduler which basically does nothing.'
  }

_idx  = 0

# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (radical.owms.PluginBase):
    """
    This plugin schedules pilots over a set of resources in reound-robin
    fashion.

    **Configuration Options:**

    * `resources`: list of resources to cycle over.  The list is a string with
      comma separated resource names (no spaces!).  Example:

          "resources" : "pbs+ssh://india.futuregrid.org,ssh://localhost"
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        radical.owms.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def init (self):

        if 'resources'    in self.cfg :
            self.resources = self.cfg['resources'].split (',')
            radical.owms._logger.debug ("round_robin over %s" % self.resources )
        else :
            self.resources = ['fork://localhost']
            radical.owms._logger.debug ("round_robin on localhost only")


    # --------------------------------------------------------------------------
    #
    def schedule (self, overlay) :

        global _idx

        if  not len(self.resources) :
            raise RuntimeError ("No resources to schedule over")


        for pid in overlay.pilots.keys() :

            if  _idx >= len(self.resources) :
                _idx  = 0

            resource  = self.resources[_idx]
            _idx     += 1

            pilot = overlay.pilots[pid]
            pilot._bind (resource)

            radical.owms._logger.info ('overlay  schedule : bind pilot %s to %s' \
                            % (pilot.id, resource))


# ------------------------------------------------------------------------------

