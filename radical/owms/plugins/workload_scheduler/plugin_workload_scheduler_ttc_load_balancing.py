

import radical.utils as ru

from   radical.owms.constants import *
import radical.owms


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_scheduler', 
    'name'        : 'ttc_load_balancing', 
    'version'     : '0.01',
    'description' : 'debug scheduler, throws out tons of info'
  }

_idx = 0

# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (radical.owms.PluginBase):
    """
    This workload scheduler will evenly distribute tasks over the set of known
    pilots.  It does not take pilot sizes into account, nor pilot state, nor
    does it care about task relationships or data dependencies.  It is not
    a clever plugin.

    **Configuration Options:** None
    This assumes that one of the earlier radical.owms plugins, or the user, is abvle to
    determine reasonably TTC estimates -- otherwise the plugin will behave like
    round-robin.  This plugin does not take the number of cores into account,
    neither for the pilots, nor for the CUs, nor does the plugin look at the
    *actual* pilot load (i.e. does not check if CUs have finished meanwhile).

    **Configuration Options:** None
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        radical.owms.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def schedule (self, workload, overlay) :
        """
        Iterate over the workload's CUs, and give them to the pilot which at
        this point accumulated the least load.  Add the CUs TTC to the pilots
        load property.
        """
      # print "########################################"
      # print "# Unit information"
      # print "########################################"
        
        for t_id in workload.tasks.keys():
          # print "t_id", t_id
            task = workload.tasks[t_id]
            for u_id in task.units.keys():
              # print "u_id", u_id
                unit = task.units[u_id]
              # print unit.as_dict()
                # this is hacky as all get-out but this IS a WIP... TODO
                try:
                    unit._ttc = int(unit.as_dict().get ('walltime', 1))
                except:
                    pass

      # print "########################################"
      # print "# Pilot information"
      # print "########################################"

        for p_id in overlay.pilots.keys():
          # print "p_id", p_id
            pilot = overlay.pilots[p_id]
          # print pilot
            if pilot.units:
              # print " -------- pilot %s" % p_id
                import pprint
                pprint.pprint (pilot)
                pprint.pprint (pilot.units)
                for u_id in pilot.units.keys():
                  # print "u_id", u_id
                    unit = pilot.units[u_id]
                  # print unit

      # print "#########################################"
      # print "# Beginning Scheduling in Debug Scheduler" 
      # print "#########################################"

        # mark pilots
        for p_id in overlay.pilots:
            if not hasattr(overlay.pilots[p_id], 'est_begin'):
                overlay.pilots[p_id].est_begin=0

        pilot = overlay.pilots[p_id]

        if  not len(overlay.pilots.keys()) :
            raise ValueError ('no pilots on overlay')

        # iterate across all tasks
        for t_id in workload.tasks:

            # print pilot info
            #for p_id in overlay.pilots:
              # print p_id, overlay.pilots[p_id].est_begin

            task = workload.tasks[t_id]
            for u_id in task.units:
                unit = task.units[u_id]

                # find pilot which will be available the soonest
                est_optimal = 999999
                p_optimal = "invalid"
                for p_id in overlay.pilots.keys():
                    if overlay.pilots[p_id].est_begin<est_optimal:
                        p_optimal=p_id
                        est_optimal=overlay.pilots[p_id].est_begin

                # assign task to the soonest available pilot
                unit._bind(p_optimal)
                overlay.pilots[p_optimal].est_begin+=int(unit._ttc)
                radical.owms._logger.debug ("assigning unit %s to pilot %s" % (u_id, p_optimal))

        # # schedule to first 'next' pilot
        # for tid in workload.tasks:
        #     task = workload.tasks[tid]
        #     for unit_id in task.units :
        #         if  _idx >= len(overlay.pilots.keys()) :
        #             _idx  = 0
        #         pilot_id  = overlay.pilots.keys()[_idx]
        #         #_idx     += 1
        #         unit = task.units[unit_id]
        #         unit._bind (pilot_id)

        #         radical.owms._logger.info ("workload schedule : assign unit %-18s to %s" % (unit_id, pilot_id))


# ------------------------------------------------------------------------------

