

import threading
import radical.utils   as ru

import troy
from   troy.constants import *


# ------------------------------------------------------------------------------
#
class Planner (object) :
    """
    The `Planner` class represents the upper layer, i.e. the application facing
    layer, of Troy, and thus hosts the API that ultimately will be used by end
    users.  That API allows to submit application workloads, and to monitor
    their execution progress.

    Internally, the planner will transform the given workload into an internal
    representation upon which the follow-up transformations of the
    :class:`WorkloadManager` class will operate.  It will further derive an
    overlay description suitable to run the workload, which downstream will be
    enacted by the :class:`OverlayManager`.
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, workload_id, planner='default') :
        """
        Create a new planner instance for this workload.  

        Use the default planner plugin if not indicated otherwise
        """

        # make this instance lockable
        self.lock = threading.RLock ()

        # initialize state, load plugins
        self._workload_id = workload_id
        self._registry    = troy._Registry ()
        self._plugin_mgr  = ru.PluginManager ('troy')

        # FIXME: error handling
        self._planner = self._plugin_mgr.load  ('planner', planner)

        # make sure the workload exists
        workload = self._registry.acquire (self._workload_id)
        workload = self._registry.release (self._workload_id)


    # --------------------------------------------------------------------------
    #
    def plan (self) :
        """
        create overlay plan (description) from workload
        """

        workload = self._registry.acquire (self._workload_id)

        try :

            # make sure the workflow is 'fresh', so we can translate it
            if  workload.state != NEW :
                raise ValueError ("workload '%s' not in NEW state" % workload.id)

            # derive overlay from workload
            overlay = self._planner.derive_overlay (workload)

            # register the new overlay
            self._registry.register (overlay)

        finally :
            self._registry.release (self._workload_id)




# ------------------------------------------------------------------------------
#
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

