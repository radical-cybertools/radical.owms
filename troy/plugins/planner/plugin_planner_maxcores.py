

import radical.utils as ru

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'planner',
    'name'        : 'maxcores',
    'version'     : '0.1',
    'description' : 'This is the default planner, which plans an maximum sized overlay'
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
    def expand_workload(self, workload):

        # Do nothing for now
        
        troy._logger.info ("planner  expand wl: expand workload : %s" % workload)


    # --------------------------------------------------------------------------
    #
    def derive_overlay(self, workload):

        # Ask for as many pilots as tasks*cores
        cores = 0

        for task_id in workload.tasks :
            cores += workload.tasks[task_id].cores

        ovl_descr = troy.OverlayDescription ({'cores' : cores })

        troy._logger.info ("planner  derive ol: derive overlay for workload: %s" % ovl_descr)

        return ovl_descr


# ------------------------------------------------------------------------------

