

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

            t = workload.tasks[tid]

            for unit_id in t['units'] :
                unit       = t['units'][unit_id]
                unit_descr = unit['description']

                if  not 'pilot' in unit :
                    raise RuntimeError ("Cannot dispatch unscheduled unit %s" % unit.id)

                pilot = unit['pilot']
                troy._logger.info ('workload dispatch : dispatch %-18s to %s' \
                                % (unit_id, pilot._get_instance('bigjob')))
                
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

                sj = bigjob.subjob ()
                sj.submit_job (bj_pilot_url, bj_cu_descr)


                unit['dispatcher'] = self
                unit['instance']   = sj


    # --------------------------------------------------------------------------
    #
    def unit_get_state (self, sj) :

        # hahaha python switch statement hahahahaha
        sj_state = sj.get_state ()

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

