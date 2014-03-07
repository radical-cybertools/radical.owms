
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import copy
import radical.utils as ru

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'expand',
    'name'        : 'cardinal',
    'version'     : '0.1',
    'description' : "This workload expander can multiplies tasks according to "
                    "their 'cardinality' property."
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (troy.PluginBase):
    """
    This plugin expands a workload by inspecting all tasks, and multiplying them
    according to their `cardinality` property.  If that property is not set, no
    additional tasks will be created.  The new tasks will have a new property,
    `cardinal`, which is set to their index respecitive to their sibling tasks.
    That property can also be used for expansion in other task properties.
    workload tasks.
    
    **Configuration Options:** None
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__(self):

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def expand_workload (self, workload):
        """
        Inspect all workload tasks, check if cardinality is set and larger than
        1.  If so, created that many identical tasks, assign them an `cardinal`
        index, and have that set replace the original task.  All new tasks
        will have a cardinality of 1.
        """

        task_descriptions = list()

        task_ids = workload.tasks.keys ()
        for task_id in task_ids :

            task = workload.tasks[task_id]
            task_dict = task.as_dict ()

            # make sure all known config vars are expanded
            ru.dict_stringexpand (task_dict, self.session.cfg)

            if  'cardinality' in task_dict :
                cardinality = int(task_dict['cardinality'])

                # if cardinality is specified, create 'that many -1' new tasks.
                # '-1' because we keep the original task around...
                for c in range(cardinality-1) :

                    new_task_dict = copy.deepcopy(task_dict)
                    new_task_dict['cardinality'] = 1 # avoid repeated expansion
                    new_task_dict['cardinal']    = c
                    task_descriptions.append (troy.TaskDescription (new_task_dict))

                # add the fresh tasks
                workload.add_task (task_descriptions)


        troy._logger.info ("planner  expand wl cardinality: %s" % workload)

        print workload.tasks
        print len(workload.tasks)


# ------------------------------------------------------------------------------

