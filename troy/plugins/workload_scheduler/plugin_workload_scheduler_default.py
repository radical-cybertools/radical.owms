

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

            for cu_id in t['cus'] :
                print "workload schedule : assign cu %-18s to %s" % (cu_id, overlay.pilots[0].id)
                t['cus'][cu_id]['pilot'] = overlay.pilots[0]
        


# ------------------------------------------------------------------------------

