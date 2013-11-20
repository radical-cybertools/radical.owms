

import threading

from   troy.constants import *


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

        troy._logger.info ("create the default workload_translator plugin")


    # --------------------------------------------------------------------------
    #
    def translate (self, workload, overlay=None) :

        for tid in workload.tasks.keys () :

            t = workload.tasks[tid]

            # we simply and stupidly translate one task into one unit description
            t['units'][tid] = dict()
            t['units'][tid]['description'] = t.description.as_dict ()
            troy._logger.info ('workload translate: derive unit %-18s for %s' % (tid, t.id))



# ------------------------------------------------------------------------------

