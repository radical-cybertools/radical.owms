

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_scheduler', 
    'name'        : 'default', 
    'version'     : '0.1',
    'description' : 'this is an empty scheduler which basically does nothing.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the (empty) default workload scheduler algorithm for
    TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        self.description = PLUGIN_DESCRIPTION
        self.name        = "%(name)s_%(type)s" % self.description


    # --------------------------------------------------------------------------
    #
    def init (self, cfg):

        troy._logger.info ("init the default wokload scheduler plugin")
        
        self.cfg = cfg.as_dict ().get (self.name, {})


    # --------------------------------------------------------------------------
    #
    def schedule (self, workload, overlay) :

        # schedule to first available pilot

        if  not overlay.pilots.keys() :
            raise RuntimeError ('no pilots in overlay')

        pilot_id = overlay.pilots.keys()[0]
        # schedule to first 'next' pilot
        for tid in workload.tasks.keys () :

            task = workload.tasks[tid]

            for unit_id in task.units :

                troy._logger.info ("workload schedule : assign unit %-18s to %s" % (unit_id, pilot_id))
                unit = task.units[unit_id]
                unit._bind (pilot_id)

                troy._logger.info ("workload schedule : assign unit %-18s to %s" % (unit_id, pilot_id))
        


# ------------------------------------------------------------------------------

