

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
class PLUGIN_CLASS (troy.PluginBase):
    """
    This class implements the (empty) default workload dispatcher for TROY.
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def dispatch (self, workload, overlay) :

        for tid in workload.tasks.keys () :

            t = workload.tasks[tid]

            for unit_id in t['units'] :
                unit       = t['units'][unit_id]
                unit_descr = unit.description
                pid            = unit.pilot_id
                pilot          = troy.Pilot (pid)
                pilot_instance = pilot._get_instance ('default')
                unit_instance  = pilot_instance.submit_unit (unit_descr)
                troy._logger.info ('workload dispatch : dispatch %-23s to %s' % (unit_id, pid))

                unit._set_instance ('default', self, unit_instance, unit_instance.id)


    # --------------------------------------------------------------------------
    #
    def unit_get_info (self, unit) :

        # find out what we can about the pilot...
        u = unit._get_instance ('default')

        info = dict()

        # hahaha python switch statement hahahahaha
        info['state'] =  {"New"      : DISPATCHED, 
                          "Running"  : RUNNING, 
                          "Failed"   : FAILED, 
                          "Done"     : DONE, 
                          "Canceled" : CANCELED}.get (u.state, UNKNOWN)

        info['slots']            = 1
        info['start_time']       = u.start
        info['agent_start_time'] = -1
        info['job_id']           = u.id 
        info['end_queue_time']   = -1 

        return info


    # --------------------------------------------------------------------------
    #
    def unit_cancel (self, u) :

        u.cancel ()




# ------------------------------------------------------------------------------

