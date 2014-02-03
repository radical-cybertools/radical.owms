
__author__ = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__ = "MIT"


import radical.utils as ru

from   troy.constants import *
import troy

from   bundle import BundleManager

"""
Notes

. Bundles is ortogonal to other functionalities. E.g. we might want to have
  a planner that uses some specific algorithms in order to define a min/max
  for the walltime of a pilot. These algorithm are mutually exclusive and, as
  such, they need to be incapsulated into a plugin, possibly loaded and
  unloaded during the same session. The problem is that both these plugings
  may need bundled functionalities in order to work properly. We may want to
  fugure out implementations that do not need bundles but I would not put
  bundles into their own plugin. This is way too complex and leads to
  collapsing the concept of code isolation (e.g. block, module) into that of
  plugin, somehting that seems to me overengineering.

"""

# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'planner',
    'name'        : 'bundles',
    'version'     : '0.1',
    'description' : 'This is the bundles planner.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (troy.PluginBase):

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__(self):

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def init(self):

        troy._logger.debug ("init plugin %s (bundles)" % self.name)
        self.init_bundles()


    # --------------------------------------------------------------------------
    #
    def init_bundles(self):

        # bundle_credential members { 'port', 'hostname', 'username',
        #                             'password' 'key_filename', 'h_flag' }

        troy._logger.info('Initializing Bundle Manager')

        self.bm = BundleManager()

        cg = self.session.get_config ('troy:bundle')
        finished_job_trace = cg['finished_job_trace']

        # FIXME: not sure if the new resource config contains all needed data...
        for sect in self.session.get_config ('troy:resources'):
            cs = self.session.cfg.get_config(sect)

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

