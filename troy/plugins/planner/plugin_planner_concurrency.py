

import radical.utils as ru

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'planner',
    'name'        : 'concurrency',
    'version'     : '0.1',
    'description' : 'This is the concurrency planner, plans the overlay ' \
                    'for concurrent workload partitions'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (troy.PluginBase):

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__(self):

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def expand_workload(self, workload):

        # Do nothing for now
        
        troy._logger.info ("planner  expand wl: expand workload : %s" % workload)


    # --------------------------------------------------------------------------
    #
    def derive_overlay(self, workload):

        # partition workload according to given concurrency
        if  len(workload.partitions) > 1 :
            troy._logger.warning ("workload is already partitioned, ignore concurrency setting")

        elif len(workload.relations) > 0 :
            troy._logger.warning ("Cannot partition workloads with task relations")

        else :

            # task concurrency in %
            concurrency  = int(self.cfg.get ('concurrency', 100))

            # count tasks / concurrent tasks / sequential tasks in workload
            n_tasks      = len(workload.tasks)
            n_concurrent = int(n_tasks * concurrency / 100)
            n_sequential = int(n_tasks - n_concurrent)

            # the number of sequential tasks defines the number of partitions as
            # n_partitions = n_sequential+1.
            # The first partition contains n_concurrent tasks, the other
            # partitions contain one task each.
            
            # first, remove old partitioning
            workload.partitions = list()


            # then create concurrent partitions
            task_ids = workload.tasks.keys ()
            c_partition = troy.Workload ()

            for n in range (0, n_concurrent) :
                c_partition.tasks[task_ids[n]] = workload.tasks[task_ids[n]]

            workload.partitions.append (c_partition.id)


            # now create the remaining sequential partitions with the remaining
            # tasks
            for n in range (n_concurrent, n_tasks) :
                s_partition = troy.Workload ()
                s_partition.tasks[task_ids[n]] = workload.tasks[task_ids[n]]
                workload.partitions.append (s_partition.id)


            troy._logger.info ("created %d workload partitions" % len(workload.partitions))


        # plan the overlay large enough to hold the first, concurrent partition.
        cores          = 0
        c_partition_id = workload.partitions[0] # max 1
        c_partition    = troy.WorkloadManager.get_workload (c_partition_id)

        for tid in c_partition.tasks :
            cores += c_partition.tasks[tid].cores

        ovl_descr = troy.OverlayDescription ({'cores'     : cores, 
                                              'wall_time' : 1}) # FIXME: use task description

        troy._logger.info ("planner  derive ol: derive overlay for workload: %s" % ovl_descr)

        return ovl_descr


# ------------------------------------------------------------------------------

