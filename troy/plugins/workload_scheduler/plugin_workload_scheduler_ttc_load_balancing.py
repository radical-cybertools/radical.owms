

import radical.utils as ru

from   troy.constants import *
import troy


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
class PLUGIN_CLASS (troy.PluginBase):

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def schedule (self, workload, overlay) :
        print "########################################"
        print "# Unit information"
        print "########################################"
        
        for t_id in workload.tasks.keys():
            print "t_id", t_id
            task = workload.tasks[t_id]
            for u_id in task.units.keys():
                print "u_id", u_id
                unit = task.units[u_id]
                print unit.description
                # this is hacky as all get-out but this IS a WIP... TODO
                try:
                    unit.description._ttc = int(unit.description.walltime)
                except:
                    pass

        print "########################################"
        print "# Pilot information"
        print "########################################"

        for p_id in overlay.pilots.keys():
            print "p_id", p_id
            pilot = overlay.pilots[p_id]
            print pilot
            if pilot.units:
                print " -------- pilot %s" % p_id
                import pprint
                pprint.pprint (pilot)
                pprint.pprint (pilot.units)
                for u_id in pilot.units.keys():
                    print "u_id", u_id
                    unit = pilot.units[u_id]
                    print unit

        print "#########################################"
        print "# Beginning Scheduling in Debug Scheduler" 
        print "#########################################"

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
            for p_id in overlay.pilots:
                print p_id, overlay.pilots[p_id].est_begin

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
                overlay.pilots[p_optimal].est_begin+=int(unit.description._ttc)
                print "assigning task to pilot:", p_optimal

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

        #         troy._logger.info ("workload schedule : assign unit %-18s to %s" % (unit_id, pilot_id))


# ------------------------------------------------------------------------------

