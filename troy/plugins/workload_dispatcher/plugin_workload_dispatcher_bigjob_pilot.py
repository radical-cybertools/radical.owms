

import pilot as pilot_module

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_dispatcher', 
    'name'        : 'bigjob_pilot', 
    'version'     : '0.1',
    'description' : 'this is a dispatcher which submits to bigjob pilots.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the bigjob_pilot workload dispatcher for TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        self.description = PLUGIN_DESCRIPTION
        self.name        = "%(name)s_%(type)s" % self.description


    # --------------------------------------------------------------------------
    #
    def init (self, cfg):

        troy._logger.info ("init the bigjob_pilot workload dispatcher plugin")
        
        self.cfg = cfg.as_dict ().get (self.name, {})


    # --------------------------------------------------------------------------
    #
    def dispatch (self, workload, overlay) :

        for tid in workload.tasks.keys () :

            task = workload.tasks[tid]

            for uid in task.units.keys () :

                unit = task.units[uid]

                if  unit.state not in [BOUND] :
                    raise RuntimeError ("Can only dispatch units in BOUND state (%s)" % unit.state)


                unit_descr = unit.description
                pilot_id   = unit['pilot_id']
                pilot      = troy.Pilot (pilot_id, _instance_type='bigjob_pilot')
                troy._logger.info ('workload dispatch : dispatch %-18s to %s' \
                                % (uid, pilot._get_instance('bigjob_pilot')))
                
                # we need to map some task description keys to bigjob_pilot
                # description keys
                keymap = { 'executable' : 'Executable' ,
                           'arguments'  : 'Arguments'  }

                bj_cu_descr = pilot_module.ComputeUnitDescription ()
                for key in unit_descr :

                    # ignore Troy level keys
                    if  key in ['tag'] :
                        continue

                  # if  key in keymap :
                  #     key = keymap[key]

                  # if  key not in keymap :
                  #     raise RuntimeError ("key '%s' is not supported by
                  #     bigjob_pilot backend" % key)

                    bj_cu_descr[key] = unit_descr[key]

                # FIXME: sanity check for pilot type
                bj_pilot  = pilot._get_instance ('bigjob_pilot')
                bj_cu     = bj_pilot.submit_compute_unit (bj_cu_descr)
                bj_cu_url = bj_cu.get_url ()

                unit._set_instance ('bigjob_pilot', self, bj_cu, bj_cu_url)


    # --------------------------------------------------------------------------
    #
    def unit_reconnect (self, native_id) :

        troy._logger.debug ("reconnect to bigjob_pilot subjob %s" % native_id)
        bj_cu = pilot_module.ComputeUnit (cu_url=native_id)
        troy._logger.debug ("reconnect to bigjob_pilot subjob %s done" % native_id)

        return bj_cu


    # --------------------------------------------------------------------------
    #
    def unit_get_info (self, unit) :

        # find out what we can about the pilot...
        bj_cu = unit._get_instance ('bigjob_pilot')

        info = bj_cu.get_details ()

        # translate bj state to troy state
        if  'state' in info :
            # hahaha python switch statement hahahahaha
            info['state'] =  {"New"     : DISPATCHED, 
                              "Running" : RUNNING, 
                              "Staging" : RUNNING, 
                              "Failed"  : FAILED, 
                              "Done"    : DONE, 
                              "Unknown" : UNKNOWN}.get (info['state'], UNKNOWN)

      # print 'unit_get_info: %s' % info

        return info


    # --------------------------------------------------------------------------
    #
    def unit_cancel (self, sj) :

        sj.cancel ()


# ------------------------------------------------------------------------------

