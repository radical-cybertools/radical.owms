

import bigjob

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_dispatcher', 
    'name'        : 'bigjob', 
    'version'     : '0.1',
    'description' : 'this is a dispatcher which submits to bigjob pilots.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the bigjob workload dispatcher for TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        troy._logger.info ("create the bigjob workload_dispatcher plugin")


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
                pilot_id   = unit['_pilot_id']
                pilot      = troy.Pilot (pilot_id)
                troy._logger.info ('workload dispatch : dispatch %-18s to %s' \
                                % (uid, pilot._get_instance('bigjob')))
                
                # FIXME: sanity check for pilot type
                bj_pilot_url, bj_manager = pilot._get_instance ('bigjob')

                # we need to map some task description keys to bigjob
                # description keys
                keymap = { 'executable' : 'Executable' ,
                           'arguments'  : 'Arguments'  }

                bj_cu_descr = bigjob.description ()
                for key in unit_descr :

                    # ignore Troy level keys
                    if  key in [TAG] :
                        continue

                  # if  key in keymap :
                  #     key = keymap[key]

                  # if  key not in keymap :
                  #     raise RuntimeError ("key '%s' is not supported by bigjob backend" % key)

                    bj_cu_descr.set_attribute (key, unit_descr[key])

                bj_cu = bigjob.subjob ()
                bj_cu.submit_job (bj_pilot_url, bj_cu_descr)
                bj_cu_url = bj_cu.get_url ()

                unit._set_instance ('bigjob', self, bj_cu, bj_cu_url)



    # --------------------------------------------------------------------------
    #
    def unit_reconnect (self, native_id) :

        bj_cu = bigjob.subjob (subjob_url=native_id)

        return bj_cu


    # --------------------------------------------------------------------------
    #
    def unit_get_state (self, sj) :

        sj_state = sj.get_state ()

        # hahaha python switch statement hahahahaha
        return {"New"    : DESCRIBED, 
                "Running": RUNNING, 
                "Staging": RUNNING, 
                "Failed" : FAILED, 
                "Done"   : DONE, 
                "Unknown": UNKNOWN}.get (sj.get_state (), UNKNOWN)


    # --------------------------------------------------------------------------
    #
    def unit_cancel (self, sj) :

        sj.cancel ()


# ------------------------------------------------------------------------------

