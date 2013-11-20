

from   troy.constants import *


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

        print "create the default workload_scheduler plugin"


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
                print "workload schedule : assign unit %-18s to %s" % (unit_id, overlay.pilots[target_pid].id)
                t['units'][unit_id]['pilot'] = overlay.pilots[target_pid]
        


# ------------------------------------------------------------------------------

