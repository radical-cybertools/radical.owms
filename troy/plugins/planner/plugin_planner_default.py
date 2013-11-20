# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'planner',
    'name'        : 'default',
    'version'     : '0.1',
    'description' : 'This is the default planner.'
  }

import troy.overlay       as to
from   troy.constants import *
from bundle import BundleManager

# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS(object):
    """
    This class implements the default planner for TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__(self):

        print "create the default planner plugin"

        self.init_bundles()

    # --------------------------------------------------------------------------
    #
    def init_bundles(self):

        self.bundle_config = '/Users/mark/proj/troy/bundle_credentials-mark.conf'

        print 'Initializing Bundle Manager using config: %s' % self.bundle_config

        self.bm = BundleManager()
        self.bm.load_cluster_credentials(self.bundle_config)

        self.cluster_list = self.bm.get_cluster_list()

        if not self.cluster_list:
            raise('No clusters available in Bundle Manager')

    # --------------------------------------------------------------------------
    #
    def check_resource_availability(self, overlay_desc):

        resource_request = { 'p_procs': overlay_desc.cores, 'est_runtime': overlay_desc.wall_time }

        predictions = {}
        for cluster in self.cluster_list:
            predictions[cluster] = self.bm.resource_predict(cluster, resource_request)
        print predictions

        # Find entries that are not -1
        usable = filter(lambda x: x != -1, predictions.values())
        if not usable:
            raise('No resources available that can fulfill this request!')

    # --------------------------------------------------------------------------
    #
    def expand_workload(self, workload):

        # Do nothing for now
        
        print "planner  expand wl: expand workload : %s" % workload

    # --------------------------------------------------------------------------
    #
    def derive_overlay(self, workload):

        ovl_descr = to.OverlayDescription (
            {
                # Ask for as many pilots as tasks
                'cores' : len(workload.tasks), 
                # Minutes obviously
                'wall_time' : (1 << 1) + (1 << 3) + (1 << 5)
            })

        print "planner  derive ol: derive overlay for workload: %s" % ovl_descr

        # Check if there is at least one bundle that can satisfy our request
        self.check_resource_availability(ovl_descr)

        # Create an overlay
        return to.Overlay(ovl_descr)


# ------------------------------------------------------------------------------

