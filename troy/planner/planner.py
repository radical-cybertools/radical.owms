

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
    def __init__(self, planner = AUTOMATIC, 
                       session = None):
        """
        Create a new planner instance for this workload.  

        Use the default planner plugin if not indicated otherwise
        """

        if  session :
            self._session = session
        else:
            self._session = troy.Session ()

        self.plugins = dict ()
        self.plugins['planner' ] = planner

        self._plugin_mgr = None


    # --------------------------------------------------------------------------
    #
    def _init_plugins (self, workload=None) :

        if  self._plugin_mgr :
            # we don't allow changes once plugins are loaded and used, for state
            # consistency
            return

      # troy._logger.debug ("initializing planner (%s)" % self.plugins)

        # for each plugin set to 'AUTOMATIC', do the clever thing
        if  self.plugins['planner' ]  == AUTOMATIC :
            self.plugins['planner' ]  = 'maxcores'


        # load plugins
        self._plugin_mgr = ru.PluginManager ('troy')
        self._planner    = self._plugin_mgr.load ('planner', self.plugins['planner'])

        if  not self._planner : 
            raise RuntimeError ("Could not load planner plugin")

        self._planner.init_plugin (self._session)

        troy._logger.info ("initialized  planner (%s)" % self.plugins)


    # --------------------------------------------------------------------------
    #
    def derive_overlay (self, workload_id):
        """
        create overlay plan (description) from workload
        """

        # Get the workload from the repo
        workload = troy.WorkloadManager.get_workload(workload_id)

        # Workload doesn't need to be PLANNED, but if it is only DESCRIBED,
        # it can't be parametrized.
        if  workload.state not in [PLANNED, DESCRIBED]:
            raise ValueError("workload '%s' not in DESCRIBED or PLANNED "
                             "state" % workload.id)
        elif workload.state is DESCRIBED and workload.parametrized:
            raise ValueError("Parametrized workload '%s' not PLANNED yet."
                             % workload.id)

        # make sure manager is initialized
        self._init_plugins (workload)

        # derive overlay from workload
        overlay_descr = self._planner.derive_overlay (workload)

        # mark the origin of the overlay description
        overlay_descr['workload_id'] = workload_id

        # Only pass the ID back
        return overlay_descr

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

        self._init_plugins (workload)

        # Expand (optional) cardinality in workload
        self._planner.expand_workload(workload)

        # Workload is now ready to go to the workload manager
        workload.state = PLANNED

# ------------------------------------------------------------------------------

