
# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'planner',
    'name'        : 'bundles',
    'version'     : '0.1',
    'description' : 'This is the bundles planner.'
  }


from   troy.constants import *
import troy

from   bundle import BundleManager


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS(object):
    """
    This class implements the default planner for TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__(self):

        self.description = PLUGIN_DESCRIPTION
        self.name        = "%(name)s_%(type)s" % self.description


    # --------------------------------------------------------------------------
    #
    def init(self, cfg):

        troy._logger.info ("init the bundle planner plugin")
        
        self.cfg = cfg.as_dict ().get (self.name, {})

        self.init_bundles()


    # --------------------------------------------------------------------------
    #
    def init_bundles(self):

        # bundle_credential members { 'port', 'hostname', 'username',
        #                             'password' 'key_filename', 'h_flag' }

        troy._logger.info('Initializing Bundle Manager')

        self.bm = BundleManager()

        cg = self.cfg.get_config('bundle')
        finished_job_trace = cg['finished_job_trace'].get_value()

        for sect in self.cfg.compute_sections:
            cs = self.cfg.get_config(sect)

            cred = { 'port': int(cs['port'].get_value()),
                     'hostname': cs['endpoint'].get_value(),
                     'cluster_type': cs['type'].get_value(),
                     'username': cs['username'].get_value(),
                     'password': cs['password'].get_value(),
                     'key_filename': cs['ssh_key'].get_value(),
                     'h_flag': cs['h_flag'].get_value()
            }
            self.bm.add_cluster(cred, finished_job_trace)

        self.cluster_list = self.bm.get_cluster_list()

        if not self.cluster_list:
            raise RuntimeError ('No clusters available in Bundle Manager. You might want to check your config file.')

    # --------------------------------------------------------------------------
    #
    def check_resource_availability(self, overlay_desc):

        resource_request = { 'p_procs': overlay_desc.cores, 'est_runtime': overlay_desc.wall_time }

        predictions = {}
        for cluster in self.cluster_list:
            predictions[cluster] = self.bm.resource_predict(cluster, resource_request)

        # Find entries that are not -1
        usable = filter(lambda x: x != -1, predictions.values())
        if not usable:
            raise RuntimeError ('No resources available that can fulfill this request!')

    # --------------------------------------------------------------------------
    #
    def expand_workload(self, workload):

        # Do nothing for now
        troy._logger.info("expand workload: %s" %  workload)

    # --------------------------------------------------------------------------
    #
    def derive_overlay(self, workload, guard=LOWER_LIMIT):

        # Determine the number of cores required
        if guard == UPPER_LIMIT:
            # We don't have any concurrency mechanisms yet,
            # so assume all concurrent.
            cores = len(workload.tasks)
        elif guard == LOWER_LIMIT:
            # We don't have any concurrency mechanisms yet,
            # so lower limit is 1
            cores = 1
        else:
            raise RuntimeError('Unknown guard: "%d') % guard

        ovl_descr = troy.OverlayDescription (
            {
                # Ask for as many pilots as tasks
                'cores' : cores,
                # Minutes obviously
                'wall_time' : (1 << 1) + (1 << 3) + (1 << 5)
            })

        troy._logger.info('planner derive ol: derive overlay for workload: '
                          '%s' % ovl_descr)

        # Check if there is at least one bundle that can satisfy our request
        # TODO: How to communicate back to application?
        self.check_resource_availability(ovl_descr)

        # Create an overlay
        return troy.Overlay(ovl_descr)



# ------------------------------------------------------------------------------

