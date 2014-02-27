

import radical.utils as ru

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
class PLUGIN_CLASS (troy.PluginBase):
    """
    This workload scheduler will evenly distribute tasks over the set of known
    pilots.  It does not take pilot sizes into account, nor pilot state, nor
    does it care about task relationships or data dependencies.  It is not
    a clever plugin.

    **Configuration Options:** None
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def schedule (self, workload, overlay) :
        """
        round-robin over pilots, givem them one unit in each turn.
        """

        global _idx

        if  not len(overlay.pilots.keys()) :
            raise ValueError ('no pilots on overlay')

        # schedule to first 'next' pilot
        for tid in workload.tasks.keys () :

            task = workload.tasks[tid]

            for unit_id in task.units :

                if  _idx >= len(overlay.pilots.keys()) :
                    _idx  = 0

                pilot_id  = overlay.pilots.keys()[_idx]
                _idx     += 1

                unit = task.units[unit_id]
                unit._bind (pilot_id)

                troy._logger.info ("workload schedule : assign unit %-18s to %s" % (unit_id, pilot_id))


# ------------------------------------------------------------------------------

