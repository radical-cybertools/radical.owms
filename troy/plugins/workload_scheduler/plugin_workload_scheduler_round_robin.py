

from   troy.constants import *


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_scheduler', 
    'name'        : 'round_robin', 
    'version'     : '0.1',
    'description' : 'simple scheduler, assigns CUs to pilots in round-robin fashion.'
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

        print "create the round-robin workload_scheduler plugin"


    # --------------------------------------------------------------------------
    #
    def schedule (self, workload, overlay) :

        global _idx

        if  not len(overlay.pilots) :
            raise ValueError ('no pilots on overlay')

        # schedule to first 'next' pilot
        for tid in workload.tasks.keys () :

            t = workload.tasks[tid]

            for cu_id in t['cus'] :

                if  _idx > len(overlay.pilots) :
                    _idx = 0

                pilot = overlay.pilots[_idx]
                print "workload scedule  : assign cu %-18s to %s" % (cu_id, pilot.id)
                t['cus'][cu_id]['pilot'] = pilot

                _idx += 1


# ------------------------------------------------------------------------------

