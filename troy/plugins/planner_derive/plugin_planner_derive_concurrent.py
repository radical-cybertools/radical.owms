

import radical.utils as ru

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'derive',
    'name'        : 'concurrent',
    'version'     : '0.1',
    'description' : 'This plugin derives an overlay for partial concurrent ' \
                    'workload execution'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (troy.PluginBase):
    """
    This plugin splits a workload in a certain number of partitions.  It assumes
    that a certain percentage (see option below) of tasks can run concurrently,
    and that all other tasks need to run sequentially, i.e. in their own
    partition.  Based on the resulting workload, an overlay is derived which has
    the size of the largest workload partition (partition 1).

    NEW: we now also respect task relations, and will make sure that the HEADs
    of those relations will be in earlier partitions than the TAILs.  This is
    not a clever scheme, and will only work for the simplest relation settings.
    We only support 'SEQUENTIAL_END' as relation_time type.

    .. note:: This plugin can restructure the workload while deriving
       the overlay description!
    
    **Configuration Options:**

    * `concurrency`: percentage of concurrent tasks in the workload.  
      Default: `100%`
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__(self):

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def derive_overlay(self, workload):
        """
        Split the overlay into partitions, according to the set concurrency.
        Once done, count the cores needed to run the largest (first) partition,
        and also sum up the walltime of all resulting partitions.
        """

        # partition workload according to given concurrency
        if  len(workload.partitions) > 1 :
            troy._logger.warning ("workload is already partitioned, ignore concurrency setting")

        else :

            # get relation info
            relation_heads  = [r.head  for r in workload.relations]
            relation_tails  = [r.tail  for r in workload.relations]
            relation_times  = [r.time  for r in workload.relations]
            relation_spaces = [r.space for r in workload.relations]

            # make sure we have only SEQUENTIAL_END type relations, and no space
            # relations
            other_times  = [True for r in workload.relations if r.time  != 'SEQUENTIAL_END']
            other_spaces = [True for r in workload.relations if r.space != '']

            if  True in (other_times + other_spaces) :
                raise ValueError ("only support temporal 'SEQUENTIAL_END' relations")

            # now we create an ordered list of task IDs, where we first have all
            # tasks which are an relation HEAD but not a TAIL; the all tasks
            # which are TAILs of those HEADs, then all tasks which are not in
            # any relation.
            # FIXME: this schema is stupid, and will break for all but the
            # simplest of cases.  It will work for Matteo's experiments though
            # - what more could we possibly want right now? ;)

            task_partitions = list()
            seen_tasks      = list()

            for rh in relation_heads :
                this_partition = list()
                for task_id in workload.tasks :
                    if  workload.tasks[task_id].tag == rh :
                        if  task_id not in seen_tasks :
                            this_partition.append (task_id)
                            seen_tasks.append     (task_id)

                if  len(this_partition) :
                    task_partitions.append (this_partition)


            for rt in relation_tails :
                this_partition = list()
                for task_id in workload.tasks :
                    if  workload.tasks[task_id].tag == rt :
                        if  task_id not in seen_tasks :
                            this_partition.append (task_id)
                            seen_tasks.append     (task_id)

                if  len(this_partition) :
                    task_partitions.append (this_partition)


            for task_id in workload.tasks :
                this_partition = list()
                if  task_id not in seen_tasks :
                    this_partition.append (task_id)
                    seen_tasks.append     (task_id)

                if  len(this_partition) :
                    task_partitions.append (this_partition)

            # now create partitions for each of the above task_partition lists.
            # for each, put the first 'concurrency'% number of tasks into one,
            # then add one partition per task

           

            # task concurrency in %
            concurrency  = int(self.cfg.get ('concurrency', 100))
            troy._logger.info ("planner uses concurrency of %d%%" % concurrency)

            # first, remove old partitioning
            workload.partitions = list()

            # determine largest partion for overlay size
            largest_partition_list = list()
            largest_partition_size = 0

            # also keep tolly for overlay lifetime
            overlay_lifetime_estimate = 0

            for partition_list in task_partitions :

                if  not len (partition_list) :
                    next

                # count tasks / concurrent tasks / sequential tasks in workload
                n_tasks      = len(partition_list)
                n_concurrent = int(n_tasks * concurrency / 100)

                if  n_tasks >= 1 and n_concurrent == 0 :
                    n_concurrent = 1

                # this is same as sequential, but avoids empty partitions
                n_sequential = int(n_tasks - n_concurrent)

                # the number of sequential tasks defines the number of partitions as
                # n_partitions = n_sequential+1.
                # The first partition contains n_concurrent tasks, the other
                # partitions contain one task each.

                # then create concurrent partitions
                c_partition = troy.Workload (workload.session)

                for n in range (0, n_concurrent) :
                    c_partition.tasks[partition_list[n]] = workload.tasks[partition_list[n]]
 
                workload.partitions.append (c_partition.id)
                overlay_lifetime_estimate += float(c_partition.get_walltime ())

                # keep info on largest partition, for overlay size
                if  largest_partition_size < n_tasks :
                    largest_partition_size = n_tasks
                    largest_partition_list = partition_list


                # now create the remaining sequential partitions with the remaining
                # tasks
                for n in range (n_concurrent, n_tasks) :
                    s_partition = troy.Workload (workload.session)
                    s_partition.tasks[partition_list[n]] = workload.tasks[partition_list[n]]
                    workload.partitions.append (s_partition.id)
                    overlay_lifetime_estimate += float(s_partition.get_walltime ())


            troy._logger.info ("created %d workload partitions" % len(workload.partitions))


 
        # plan the overlay *large* enough to hold the larges partition.
        cores = 0

        for tid in largest_partition_list :
            cores += workload.tasks[tid].cores

        # have all information needed for the overlay
        ovl_descr = troy.OverlayDescription ({'cores'    : cores, 
                                              'walltime'
                                              : overlay_lifetime_estimate})

        troy._logger.info ("planner  derived overlay: %s" % ovl_descr)

        print "--------------------------------------------------------------"
        for c_partition_id in workload.partitions :
            c_partition = troy.WorkloadManager.get_workload (c_partition_id)
            print '%s : %s' % (c_partition.id, c_partition.tasks.keys())
        print "--------------------------------------------------------------"

        return ovl_descr


# ------------------------------------------------------------------------------

