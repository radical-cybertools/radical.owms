

import threading
import radical.utils   as ru


# ------------------------------------------------------------------------------
#
class WorkloadManager (object) :
    """
    The `WorkloadManager` class, as its name suggests, manages :class:`Workload`
    instances, i.e. schedules and enacts those instances.
    """

    _rlock = threading.RLock ()


    # --------------------------------------------------------------------------
    #
    def __init__ (self, scheduler=None, dispatcher=None) :
        """
        Create a new workload manager instance.
        """

        with self._rlock :


            if  not scheduler  : scheduler  = 'default'
            if  not dispatcher : dispatcher = 'default'

            # initialize state
            plugin_mgr       = ru.PluginManager ('troy')
            self._scheduler  = plugin_mgr.load  ('workload_scheduler',  scheduler)
            self._dispatcher = plugin_mgr.load  ('workload_dispatcher', dispatcher)




# ------------------------------------------------------------------------------
#
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

