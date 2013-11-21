

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

        troy._logger.info ("create the default workload_scheduler plugin")


    # --------------------------------------------------------------------------
    #
    def schedule (self, workload, overlay) :

        # schedule to first available pilot
        for tid in workload.tasks.keys () :

            t = workload.tasks[tid]

            if  not overlay.pilots.keys() :
                raise RuntimeError ('no pilots in overlay')

            target_pid = overlay.pilots.keys()[0]
            for unit_id in t['units'] :
                troy._logger.info ("workload schedule : assign unit %-18s to %s" \
                                % (unit_id, target_pid))
                t['units'][unit_id]['pilot'] = overlay.pilots[target_pid]
                overlay.pilots[target_pid].assigned_units.append (unit_id)
        


# ------------------------------------------------------------------------------

