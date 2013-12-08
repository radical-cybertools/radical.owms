

import radical.utils as ru

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_dispatcher', 
    'name'        : 'default', 
    'version'     : '0.1',
    'description' : 'this is an empty dispatcher which basically does nothing.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the (empty) default workload dispatcher for TROY.
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        self.description = PLUGIN_DESCRIPTION
        self.name        = "%(name)s_%(type)s" % self.description


    # --------------------------------------------------------------------------
    #
    def init (self, cfg):

        troy._logger.info ("init the default workload dispatcher plugin")
        
        self.cfg = cfg.as_dict ().get (self.name, {})


    # --------------------------------------------------------------------------
    #
    def dispatch (self, workload, overlay) :

        for tid in workload.tasks.keys () :

            t = workload.tasks[tid]

            for unit_id in t['units'] :
                unit_descr = t['units'][unit_id]['description']
                pilot      = t['units'][unit_id]['pilot']
                troy._logger.info ('workload dispatch : dispatch %-23s to %s' % (unit_id, pilot.instance))


# ------------------------------------------------------------------------------

