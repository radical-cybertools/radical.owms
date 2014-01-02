

import sinon
import radical.utils as ru

from   troy.constants import *
import troy

DBURL  = 'mongodb://ec2-184-72-89-141.compute-1.amazonaws.com:27017/'
FGCONF = 'https://raw.github.com/saga-project/saga-pilot/master/configs/futuregrid.json'

# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_dispatcher', 
    'name'        : 'sinon_pilot', 
    'version'     : '0.1',
    'description' : 'this is a dispatcher which submits to sinon pilots.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        self.description = PLUGIN_DESCRIPTION
        self.name        = "%(name)s_%(type)s" % self.description


    # --------------------------------------------------------------------------
    #
    def init (self, cfg):

        troy._logger.info ("init the sinon_pilot workload dispatcher plugin")
        
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
                pilot      = troy.Pilot (pilot_id, _instance_type='sinon_pilot')
                troy._logger.info ('workload dispatch : dispatch %-18s to %s' \
                                % (uid, pilot._get_instance('sinon_pilot')))
                
                # we need to map some task description keys to bigjob_pilot
                # description keys
                keymap = { 'executable' : 'Executable' ,
                           'arguments'  : 'Arguments'  }

                sinon_cu_descr = sinon.ComputeUnitDescription ()
                for key in unit_descr :

                    # ignore Troy level keys
                    if  key in ['tag'] :
                        continue

                  # if  key in keymap :
                  #     key = keymap[key]

                  # if  key not in keymap :
                  #     raise RuntimeError ("key '%s' is not supported by
                  #     bigjob_pilot backend" % key)

                    sinon_cu_descr[key] = unit_descr[key]

                # FIXME: sanity check for pilot type
                sinon_pilot  = pilot._get_instance ('sinon_pilot')
                sinon_cu     = sinon_pilot.submit_units (sinon_cu_descr)

                unit._set_instance ('sinon_pilot', self, sinon_cu, sinon_cu.uid)


    # --------------------------------------------------------------------------
    #
    def unit_reconnect (self, native_id) :

        troy._logger.debug ("reconnect to sinon_pilot subjob %s" % native_id)
        bj_cu = sinon.ComputeUnit (cu_url=native_id)
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

