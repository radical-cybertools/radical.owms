

__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils as ru
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_parser',
    'name'        : 'default',
    'version'     : '0.1',
    'description' : 'This is the default workload parser'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (troy.PluginBase):
    """
    This pugin consumes a json file, and creates a troy workload from the task
    and relation descriptions therein.  The structure of the json file should
    be::
       
       {
           "tasks"     : [ {<task_description>    , ... ],
           "relations" : [ {<relation_description>, ... ]
       }

    where `<task_description>` and `<relation_description>` are dict
    representatios of the normal :class:`troy.TaskDescription` and
    :class:`troy.RelationDescription` classes.

    **Configuration Options:** None
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__(self):

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def parse (self, workload_description):
        """
        Parse the given json into  task and relation descriptions, and create
        a workload out of them.
        """

        troy._logger.info ("parsing workload")

        tasks     = None
        relations = None

        workload_dict = ru.parse_json (workload_description)

        if 'tasks'     in workload_dict : 
            tasks      =  workload_dict['tasks']
        if 'relations' in workload_dict : 
            relations  =  workload_dict['relations']

        if  not tasks and not relations :
            raise ValueError ("Cannot handle workload description")

        task_descriptions     = list()
        relation_descriptions = list()

        if tasks :
            for task_descr in tasks :
                # make sure we use all current information
                ru.dict_stringexpand (task_descr, self.session.cfg)
                task_descriptions.append (troy.TaskDescription (task_descr))

        if relations :
            for relation_descr in relations :
                # make sure we use all current information
                ru.dict_stringexpand (relation_descr, self.session.cfg)
                relation_descriptions.append (troy.RelationDescription (relation_descr))

        return task_descriptions, relation_descriptions




# ------------------------------------------------------------------------------

