

import radical.utils as ru

from   radical.owms.constants import *
import radical.owms


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_transformer', 
    'name'        : 'synapse', 
    'version'     : '0.1',
    'description' : 'transforms a workload for profiling or emulation.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (radical.owms.PluginBase):
    """
    This plugin is not documented.  Go figure.
    """

    __metaclass__ = ru.Singleton
    
    
    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        radical.owms.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def translate (self, workload, overlay=None) :
        """
        This method does not exist in radical.owms.  Officially.
        """

        for tid in workload.tasks.keys () :

            task = workload.tasks[tid]

            # we simply and stupidly translate one task into one unit description
            cu_descr = radical.owms.ComputeUnitDescription (task.description.as_dict ())

            # this translator adds a TTC estimate -- for now, it assumes
            # something stupid, like the number of characters in the arguments
            # representing estimated TTC in seconds...
            cu_descr._ttc = int(len(str(cu_descr.arguments)))

            cu_id    = task._add_unit (cu_descr)
            radical.owms._logger.info ('workload translate: derive unit %-18s for %s' % (cu_id, task.id))



# ------------------------------------------------------------------------------

