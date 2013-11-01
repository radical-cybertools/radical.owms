

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
    def __init__ (self, planner='default') :
        """
        Create a new planner instance for this workload.  

        Use the default planner plugin if not indicated otherwise
        """

        # initialize state, load plugins
        self._plugin_mgr  = ru.PluginManager ('troy')

        # FIXME: error handling
        self._planner = self._plugin_mgr.load  ('planner', planner)


    # --------------------------------------------------------------------------
    #
    def plan (self, workload) :
        """
        create overlay plan (description) from workload
        """

        overlay  = None

        # make sure the workflow is 'fresh', so we can translate it
        if  workload.state != DESCRIBED :
            raise ValueError ("workload '%s' not in DESCRIBED state" % workload.id)

        # derive overlay from workload
        overlay = self._planner.derive_overlay(workload)

        return overlay.id


# ------------------------------------------------------------------------------

