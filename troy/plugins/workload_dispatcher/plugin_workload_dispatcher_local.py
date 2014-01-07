

import os
import saga

import radical.utils as ru

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_dispatcher', 
    'name'        : 'local', 
    'version'     : '0.1',
    'description' : 'this is a simple dispatcher which forks CUs locally.'
  }


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
    def dispatch (self, workload, overlay) :

      # # stage-in for workload
      # workload.manager._stager.stage_in_workload (workload)

        for tid in workload.tasks.keys () :

            task = workload.tasks[tid]

          # # stage-in for task
          # workload.manager._stager.stage_in_task (task)

            for unit_id in task['units'] :
                unit     = task['units'][unit_id]

              # # stage-in for unit
              # workload.manager._stager.stage_in_unit (unit)

                if  not unit.staged_in and task.description.inputs :
                    raise RuntimeError ("cannot dispatch %s - stage-in not done" % unit.id)

                unit_descr     = unit.description
                pid            = unit.pilot_id
                pilot          = troy.Pilot (pid)
                pilot_instance = pilot._get_instance ('default')
                unit_instance  = pilot_instance.submit_unit (unit_descr)
                troy._logger.info ('workload dispatch : dispatch %-23s to %s' % (unit_id, pid))

                unit._set_instance ('default', self, unit_instance, unit_instance.id)


    # --------------------------------------------------------------------------
    #
    def unit_get_info (self, unit) :

        # find out what we can about the pilot...
        u = unit._get_instance ('default')

        info = dict()

        # hahaha python switch statement hahahahaha
        info['state'] =  {"New"      : DISPATCHED, 
                          "Running"  : RUNNING, 
                          "Failed"   : FAILED, 
                          "Done"     : DONE, 
                          "Canceled" : CANCELED}.get (u.state, UNKNOWN)

        info['slots']            = 1
        info['start_time']       = u.start
        info['agent_start_time'] = -1
        info['job_id']           = u.id 
        info['end_queue_time']   = -1 

        return info


    # --------------------------------------------------------------------------
    #
    def unit_cancel (self, unit) :

        u = unit._get_instance ('default')
        u.cancel ()


    # --------------------------------------------------------------------------
    #
    def stage_file_in (self, src, resource, tgt) :
        """
        src file element can contain wildcards.  
        tgt can not contain wildcards -- but must be a directory URL.
        """

        # make sure we stay on localhost
        resource_url = saga.Url (resource)
        if  resource_url.host != 'localhost' :
            raise ValueError ("can only stage files on local resource, not %s" % resource_url.host)

        # make sure the src path is absolute
        if  src[0] != '/' :
            src = "%s/%s" % (os.getcwd(), src)

        print 'copy %s -> %s' % (src, tgt)

        os.popen ("mkdir -p %s" % (os.path.dirname (tgt)))
        os.popen ("cp %s %s" % (src, tgt))


    # --------------------------------------------------------------------------
    #
    def stage_file_out (self, resource, src_dir, src) :
        """
        src file element can contain wildcards.  
        tgt can not contain wildcards, but must be a directory.
        """

        # make sure we stay on localhost
        resource_url = saga.Url (resource)
        if  resource_url.host != 'localhost' :
            raise ValueError ("can only stage files on local resource, not %s" % resource_url.host)

        # make sure the src path is absolute
        if  src_dir[0] != '/' :
            src_dir = "%s/%s" % (os.getcwd(), src_dir)

        tgt = os.getcwd()

        print 'copy %s / %s -> %s' % (src_dir, src, tgt)

        os.popen ("cp %s/%s %s" % (src_dir, src, tgt))




# ------------------------------------------------------------------------------

