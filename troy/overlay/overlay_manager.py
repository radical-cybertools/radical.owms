
__author__ = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__ = "MIT"


"""
Manages the pilot-based overlays for TROY.
"""

import threading
import radical.utils      as ru

import troy
from   troy.constants import *


# -----------------------------------------------------------------------------
#
class OverlayManager (object) :
    """
    Generates and instantiates an overlay. An overlay consists of pilot
    descriptions and instances.

    Capabilities provided:

    * Get information about resources [from ResourceInformation(Bundle)]:
      - Queues:
        . Name;
        . allowed walltime;
        . prediction on queuing time depending on the job size.
    * Get general information about workload: 
      - Total time required for its execution [from Planner];
      - total space required for its execution [from Planner]:
        . # of cores.
    * Get information about compute unit (CU) [from WorkloadManager]:
      - Time required;
      - Space required:
        . # of cores.
      - Grouping with other CUs.
    * describe pilots.
    * Schedule pilots on resources.
    * Provision pilots on resources [by means of Provisioner].

    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self, informer    = 'default',
                        scheduler   = 'default',
                        provisioner = 'default') :
        """
        Create a new overlay manager instance.

        Use default plugins if not otherwise indicated.  Note that the
        provisioner plugin is actually not owned by the OverlayManager, but by
        the pilots of the Overlay managed by the OverlayManager.
        """

        # initialize state, load plugins
        self._registry   = troy._Registry ()
        self._plugin_mgr = radical.utils.PluginManager ('troy')

        # FIXME: error handling
        self._informer   = self._plugin_mgr.load ('overlay_informer',    informer)
        self._scheduler  = self._plugin_mgr.load ('overlay_scheduler',   scheduler)
        self._dispatcher = self._plugin_mgr.load ('overlay_provisioner', dispatcher)


    # --------------------------------------------------------------------------
    #
    @classmethod
    def register_overlay (cls, overlay) :
        ru.Registry.register (overlay)


    # --------------------------------------------------------------------------
    #
    @classmethod
    def unregister_overlay (cls, overlay_id) :
        ru.Registry.unregister (overlay_id)


    # --------------------------------------------------------------------------
    #
    @classmethod
    def get_overlay (cls, overlay_id) :
        """
        We don't care about locking at this point -- so we simply release the
        overlay immediately...
        """
        wl = ru.Registry.acquire (overlay_id, ru.READONLY)
        ru.Registry.release (overlay_id)

        return wl

# -----------------------------------------------------------------------------

