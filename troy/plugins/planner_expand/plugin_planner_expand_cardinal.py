
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


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

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__(self):

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def expand_workload (self, workload):

        task_descriptions = list()

        for task_id in workload.tasks :

            task = workload.tasks[task_id]
            task_dict = task.as_dict ()

            # make sure all known config vars are expanded
            ru.dict_stringexpand (task_dict, self.session.cfg)

            if  'cardinality' in task_dict :
                cardinality = int(task_dict['cardinality'])

                new_task_dict = task.as_dict ()
                new_task_dict['cardinality'] = 1 # avoid repeated expansion

                for c in range(cardinality) :

                    new_task_dict['cardinal'] = c
                    task_descriptions.append (troy.TaskDescription (new_task_dict))

            else :
                task_descriptions.append (task.as_dict ())

        # remove old tasks
        workload.tasks = dict()

        # and add fresh ones
        workload.add_task (task_descriptions)

        troy._logger.info ("planner  expand wl cardinality: %s" % workload)


# ------------------------------------------------------------------------------

