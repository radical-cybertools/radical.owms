

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
        """
        invoked when plugin is loaded. Only do sanity checks, no other
        initialization
        """

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)

        # cache saga dirs for file staging
        self._dir_cache = dict()


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
    def stage_file_in (self, src, resource, workdir, tgt) :
        """
        src file element can contain wildcards.  
        tgt can not contain wildcards -- but must be a directory URL.
        """

        if  workdir[0] != '/' : 
            raise ValueError ("target directory must have absolute path, not %s"
                    % workdir)


        # make sure src path is absolute -- if not, its relative to pwd
        if  src[0] != '/' :
            src = os.path.normpath ("%s/%s" % (os.getcwd(), src))

        # make sure tgt parg is absolute -- if not, its relative to workdir
        if  tgt[0] != '/' :
            tgt = os.path.normpath ("%s/%s" % (workdir, tgt))

        # if src is not a fully qualified URL, interpret it as local path
        src_url = saga.Url (src)
        if  not src_url.host and not src_url.schema :
            src_url = saga.Url ("file://localhost%s" % src)

        resource_url = saga.Url (resource)
        if  resource_url.schema.endswith ('fork') :
            resource_url.schema = 'file'

        troy._logger.debug ('copy %s -> %s / %s' % (src_url, resource_url, tgt))

        # if neded, create a dir handle to the target resource and cache it
        if  not str(resource) in self._dir_cache :
            self._dir_cache[str(resource)] = saga.filesystem.Directory (resource_url)

        # use cached dir handle, point it to the target dir (to create it if
        # needed), and copy the file
        tgt_dir = self._dir_cache[str(resource)]
        tgt_dir.change_dir (os.path.dirname (tgt), saga.filesystem.CREATE_PARENTS)
        tgt_dir.copy       (src_url, tgt)


    # --------------------------------------------------------------------------
    #
    def stage_file_out (self, tgt, resource, srcdir, src) :
        """
        src file element can contain wildcards.  
        tgt can not contain wildcards -- but it can be a directory URL (and, in
        fact, is interpreted as such if src contains wildcard chars).
        """

        if  tgt[0] != '/' :
            tgt = "%s/%s" % (os.getcwd(), tgt)

        # HACK
        while resource [-1] == '/' : resource = resource [0:-1]
        while srcdir   [-1] == '/' : srcdir   = srcdir   [0:-1]
        while srcdir   [ 0] == '/' : srcdir   = srcdir   [1:  ]


        src_url          = saga.Url ("/%s/%s" % (srcdir, src))
        tgt_url          = saga.Url ("file://localhost%s" % tgt)
        src_dir_url      = saga.Url (src_url) # deep copy
        src_dir_url.path = os.path.dirname (src_url.path)

        troy._logger.debug ('copy %s <- %s' % (tgt_url, src_url))

        if  not str(resource) in self._dir_cache :
            self._dir_cache[str(resource)] = saga.filesystem.Directory \
                    (src_dir_url, saga.filesystem.CREATE_PARENTS)
            troy._logger.warning ('new cache for %s (%s)' % (resource, src_dir_url))

        troy._logger.warning ('use cache for %s (%s)' % (resource, src_dir_url))
        src_dir = self._dir_cache[str(resource)]

        src_dir.change_dir (src_dir_url.path)
        src_dir.copy       (src_url, tgt_url)



# ------------------------------------------------------------------------------

