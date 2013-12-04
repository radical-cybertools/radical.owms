

import threading

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_translator', 
    'name'        : 'default', 
    'version'     : '0.1',
    'description' : 'this is an empty translator which basically does nothing.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the (empty) default workload translator for TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        pass


    # --------------------------------------------------------------------------
    #
    def init (self, cfg):

        troy._logger.info ("init the default wokload translator plugin")
        self.cfg = cfg


    # --------------------------------------------------------------------------
    #
    def translate (self, workload, overlay=None) :

        for tid in workload.tasks.keys () :

            task = workload.tasks[tid]

            # we simply and stupidly translate one task into one unit description
            cu_descr = troy.ComputeUnitDescription (task.description.as_dict ())
            cu_id    = task._add_unit (cu_descr)
            troy._logger.info ('workload translate: derive unit %-18s for %s' % (cu_id, task.id))



# ------------------------------------------------------------------------------

