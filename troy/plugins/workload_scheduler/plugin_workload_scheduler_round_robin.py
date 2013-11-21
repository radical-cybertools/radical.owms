

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_scheduler', 
    'name'        : 'round_robin', 
    'version'     : '0.1',
    'description' : 'simple scheduler, assigns units to pilots in round-robin fashion.'
  }

_idx = 0

# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the (trivial) round-robin workload scheduler algorithm for
    TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        troy._logger.info ("create the round-robin workload_scheduler plugin")


    # --------------------------------------------------------------------------
    #
    def schedule (self, workload, overlay) :

        global _idx

        if  not len(overlay.pilots.keys()) :
            raise ValueError ('no pilots on overlay')

        # schedule to first 'next' pilot
        for tid in workload.tasks.keys () :

            t = workload.tasks[tid]

            for unit_id in t['units'] :

                if  _idx > len(overlay.pilots.keys()) :
                    _idx = 0

                target_pid = overlay.pilots.keys()[_idx]

                pilot = overlay.pilots[target_pid]
                troy._logger.info ("workload schedule : assign unit %-18s to %s" % (unit_id, pilot.id))
                t['units'][unit_id]['pilot_id'] = pilot.id

                _idx += 1


# ------------------------------------------------------------------------------

