

import pilot         as pilot_module
import radical.utils as ru

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
class PLUGIN_CLASS (troy.PluginBase):

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :
        """
        invoked when plugin is loaded. Only do sanity checks, no other
        initialization
        """

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def dispatch (self, workload, overlay) :
        """
        Dispatch a given workload: examine all tasks in the WL to find the
        defined CUs, and dispatch them to the pilot system.  
        """

        for tid in workload.tasks.keys () :

            task = workload.tasks[tid]

            for uid in task.units.keys () :

                unit = task.units[uid]

              # # stage-in for unit.  For that to work, we have to make sure to
              # # set the working_directory for the unit (if that was not set
              # # explicitly before)
              # workload.manager._stager.stage_in_unit (unit)

                # sanity check for CU state -- only in BOUND state we can 
                # rely on a pilot being assigned to the CU.
                if  unit.state not in [BOUND] :
                    raise RuntimeError ("Can only dispatch units in BOUND state (%s)" % unit.state)


                # get the unit description, and the target pilot ID
                unit_descr = unit.description
                pilot_id   = unit['pilot_id']

                # reconnect to the given pilot -- this is likely to pull the
                # instance from a cache, so should not cost too much.
                pilot      = troy.Pilot (pilot_id, _instance_type='bigjob_pilot')
                troy._logger.info ('workload dispatch : dispatch %-18s to %s' \
                                % (uid, pilot._get_instance('bigjob_pilot')))
                
                # translate our information into bigjob speak, and dispatch
                # a subjob for the CU
                bj_cu_descr = pilot_module.ComputeUnitDescription ()
                for key in unit_descr :

                    # ignore Troy level keys
                    if  key in ['tag'] :
                        continue

                    bj_cu_descr[key] = unit_descr[key]

                # FIXME: sanity check for pilot type
                bj_pilot  = pilot._get_instance ('bigjob_pilot')
                bj_cu     = bj_pilot.submit_compute_unit (bj_cu_descr)
                bj_cu_url = bj_cu.get_url ()

                # attach the backend instance to the unit, for later state
                # checks etc. We leave it up to the unit to decide if it wants
                # to cache the instance, or just the ID and then later
                # reconnect.
                unit._set_instance ('bigjob_pilot', self, bj_cu, bj_cu_url)


    # --------------------------------------------------------------------------
    #
    def unit_reconnect (self, native_id) :
        """
        the unit lost the instance, and needs to reconnect...
        This is what is getting called on troy.Unit._get_instance, if that
        troy.Unit doesn't have that instance anymore...
        """

        troy._logger.debug ("reconnect to bigjob_pilot subjob %s" % native_id)
        bj_cu = pilot_module.ComputeUnit (cu_url=native_id)

        return bj_cu


    # --------------------------------------------------------------------------
    #
    def unit_get_info (self, unit) :
        """
        unit inspection: get all possible information for the unit, and return
        in a dict.  This dict SHOULD contain 'state' at the very least -- but
        check the pilot_inspection unit test for more recommended attributes.
        """

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
    def unit_cancel (self, unit) :
        """
        bye bye bye Junimond, es ist vorbei, bye bye...
        """

        sj = unit._get_instance ('bigjob_pilot')
        sj.cancel ()


# ------------------------------------------------------------------------------

