
__author__    = "RADICAL Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils as ru

from   radical.owms.constants import *
import radical.owms


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'planner_derive',
    'name'        : 'maxcores',
    'version'     : '0.1',
    'description' : 'This plugin derives an overlay size by counting cores'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (radical.owms.PluginBase):
    """
    This plugin determines the overlay size by simply adding the sizes of all
    workload tasks.
    
    **Configuration Options:** None
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__(self):

        radical.owms.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def derive_overlay(self, workload):
        """
        Counts the cores needed to run the workload, assuming that all tasks are
        to be running concurrently.
        """

        # Ask for as many pilots as tasks*cores
        cores = 0

        for task_id in workload.tasks :
            cores += workload.tasks[task_id].cores

        ovl_descr = radical.owms.OverlayDescription ({'cores' : cores})

        radical.owms._logger.info ("planner  derive ol: derive overlay for workload: %s" % ovl_descr)

        return ovl_descr


# ------------------------------------------------------------------------------

