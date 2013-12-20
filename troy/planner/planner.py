

import threading
import radical.utils as ru

import troy
from   troy.constants import *


# ------------------------------------------------------------------------------
#
class Planner(object):
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
    def __init__(self, planner='default', session=None):
        """
        Create a new planner instance for this workload.  

        Use the default planner plugin if not indicated otherwise
        """

        if  not session :
            session = troy.Session ()

        # initialize state, load plugins
        self._session     = session
        self._plugin_mgr  = ru.PluginManager('troy')

        # FIXME: error handling
        self._planner = self._plugin_mgr.load('planner', planner)
        self._planner.init ()

        if  not self._planner : raise RuntimeError ("Could not load planner plugin")

        self._planner.init (session.cfg)


    # --------------------------------------------------------------------------
    #
    def derive_overlay(self, workload_id):
        """
        create overlay plan (description) from workload
        """

        # Get the workload from the repo
        workload = troy.WorkloadManager.get_workload(workload_id)

        # Workload doesn't need to be PLANNED, but if it is only DESCRIBED,
        # it can't be parametrized.
        if workload.state not in [PLANNED, DESCRIBED]:
            raise ValueError("workload '%s' not in DESCRIBED or PLANNED "
                             "state" % workload.id)
        elif workload.state is DESCRIBED and workload.parametrized:
            raise ValueError("Parametrized workload '%s' not PLANNED yet."
                             % workload.id)

        # derive overlay from workload
        overlay = self._planner.derive_overlay(workload)

        # Put the overlay into the system registry so others can access it
        troy.OverlayManager.register_overlay(overlay)

        # Only pass the ID back
        return overlay.id

    # --------------------------------------------------------------------------
    #
    def expand_workload(self, workload_id):
        """
        Expand cardinality parameters in workload.
        """

        # Get the workload from the repo
        workload = troy.WorkloadManager.get_workload(workload_id)

        # make sure the workflow is 'fresh', so we can translate it
        if workload.state != DESCRIBED:
            raise ValueError("workload '%s' not in DESCRIBED state" %
                             workload.id)

        # Expand (optional) cardinality in workload
        self._planner.expand_workload(workload)

        # Workload is now ready to go to the workload manager
        workload.state = PLANNED

# ------------------------------------------------------------------------------

