

from   troy.constants import *


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

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        print "create the default workload_dispatcher plugin"


    # --------------------------------------------------------------------------
    #
    def dispatch (self, workload, overlay) :

        for tid in workload.tasks.keys () :

            t = workload.tasks[tid]

            for cu_id in t['cus'] :
                cu_descr = t['cus'][cu_id]['description']
                pilot    = t['cus'][cu_id]['pilot']
                print 'workload dispatch : dispatch %-18s to %s' % (cu_id, pilot.instance)
              # pilot.submit_job (cu_descr)



        exit
        print " --------------------------- "
        pass


# ------------------------------------------------------------------------------

