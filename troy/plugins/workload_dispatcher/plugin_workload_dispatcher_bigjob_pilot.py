

import os
import saga
import pilot         as pilot_module

import radical.utils as ru
from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_dispatcher', 
    'name'        : 'bigjob_pilot', 
    'version'     : '0.1',
    'description' : 'this is a dispatcher which submits to bigjob pilots.'
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
        """
        Dispatch a given workload: examine all tasks in the WL to find the
        defined CUs, and dispatch them to the pilot system.  
        """

        for tid in workload.tasks.keys () :

            task = workload.tasks[tid]

            for uid in task.units.keys () :

                unit = task.units[uid]

              # # stage-in for unit.  For that to work, we have to make sure to
              # # set the working_directory for the unit (if that was not set
              # # explicitly before)
              # workload.manager._stager.stage_in_unit (unit)

                # sanity check for CU state -- only in BOUND state we can 
                # rely on a pilot being assigned to the CU.
                if  unit.state not in [BOUND] :
                    raise RuntimeError ("Can only dispatch units in BOUND state (%s)" % unit.state)


                # get the unit description, and the target pilot ID
                unit_descr = unit.description
                pilot_id   = unit['pilot_id']

                # reconnect to the given pilot -- this is likely to pull the
                # instance from a cache, so should not cost too much.
                pilot      = troy.Pilot (pilot_id, _instance_type='bigjob_pilot')
                troy._logger.info ('workload dispatch : dispatch %-18s to %s' \
                                % (uid, pilot._get_instance('bigjob_pilot')))
                
                # translate our information into bigjob speak, and dispatch
                # a subjob for the CU
                bj_cu_descr = pilot_module.ComputeUnitDescription ()
                for key in unit_descr :

                    # ignore Troy level keys
                    if  key in ['tag'] :
                        continue

                    bj_cu_descr[key] = unit_descr[key]

                # FIXME: sanity check for pilot type
                bj_pilot  = pilot._get_instance ('bigjob_pilot')
                bj_cu     = bj_pilot.submit_compute_unit (bj_cu_descr)
                bj_cu_url = bj_cu.get_url ()

                # attach the backend instance to the unit, for later state
                # checks etc. We leave it up to the unit to decide if it wants
                # to cache the instance, or just the ID and then later
                # reconnect.
                unit._set_instance ('bigjob_pilot', self, bj_cu, bj_cu_url)


    # --------------------------------------------------------------------------
    #
    def unit_reconnect (self, native_id) :
        """
        the unit lost the instance, and needs to reconnect...
        This is what is getting called on troy.Unit._get_instance, if that
        troy.Unit doesn't have that instance anymore...
        """

        troy._logger.debug ("reconnect to bigjob_pilot subjob %s" % native_id)
        bj_cu = pilot_module.ComputeUnit (cu_url=native_id)

        return bj_cu


    # --------------------------------------------------------------------------
    #
    def unit_get_info (self, unit) :
        """
        unit inspection: get all possible information for the unit, and return
        in a dict.  This dict SHOULD contain 'state' at the very least -- but
        check the pilot_inspection unit test for more recommended attributes.
        """

        # find out what we can about the pilot...
        bj_cu = unit._get_instance ('bigjob_pilot')

        info = bj_cu.get_details ()

        # translate bj state to troy state
        if  'state' in info :
            # hahaha python switch statement hahahahaha
            info['state'] =  {"New"     : DISPATCHED, 
                              "Running" : RUNNING, 
                              "Staging" : RUNNING, 
                              "Failed"  : FAILED, 
                              "Done"    : DONE, 
                              "Unknown" : UNKNOWN}.get (info['state'], UNKNOWN)

      # print 'unit_get_info: %s' % info

        return info


    # --------------------------------------------------------------------------
    #
    def unit_cancel (self, unit) :
        """
        bye bye bye Junimond, es ist vorbei, bye bye...
        """

        sj = unit._get_instance ('bigjob_pilot')
        sj.cancel ()


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
        if  resource_url.schema.endswith ('+ssh') :
            resource_url.schema = 'ssh'

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

        resource_url = saga.Url (resource)
        if  resource_url.schema.endswith ('+ssh') :
            resource_url.schema = 'ssh'

        if  not str(resource) in self._dir_cache :
            self._dir_cache[str(resource)] = saga.filesystem.Directory (resource_url)
      #     troy._logger.warning ('new cache for %s (%s)' % (resource, resource_url))

      # troy._logger.warning ('use cache for %s (%s)' % (resource, resource_url))
        src_dir = self._dir_cache[str(resource)]

        src_dir.change_dir (src_dir_url.path)
        src_dir.copy       (src_url, tgt_url)



# ------------------------------------------------------------------------------

