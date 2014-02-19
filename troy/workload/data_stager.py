
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import os
import saga
import radical.utils      as ru

import troy.utils         as tu
from   troy.constants import *
import troy


"""
Stage_in  for a given unit, once the unit is in BOUND state.
Stage_out for a given unit, once the unit is in final state.
"""


# ------------------------------------------------------------------------------
#
class DataStager (object) :
    """
    staging directives

       [local_path] [operator] [remote_path]

    local path: 
        * interpreted as relative to the application's working directory
        * must point to local storage (localhost)
    
    remote path
        * interpreted as relative to the task's working directory

    operator :
        * >  : stage to remote target, overwrite if exists
        * >> : stage to remote target, append    if exists
        * <  : stage to local  target, overwrite if exists
        * << : stage to local  target, append    if exists

    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self, session) : 
        """
        FIXME
        """

        self.session = session

        # cache saga dirs for file staging
        self._dir_cache = dict()



    # --------------------------------------------------------------------------
    #
    def _parse_staging_directive (self, txt) :
        """
        returns [src, tgt, op] as relative or absolute paths or URLs.  This
        parsing is backward compatible with the simple staging directives used
        in troy previously -- any strings which do not contain staging operators
        will be interpreted as simple paths (identical for src and tgt,
        operation set to '=', which is interpreted as ).

        Supported directives:

           src >  tgt -- stage  task input ./src to remote remote.host as ./tgt
           src >> tgt -- append task input ./src to remote remote.host    ./tgt
           tgt <  src -- stage  task output from remote host ./src to     ./tgt
           tgt << src -- append task output from remote host ./src to     ./tgt
        """

        rs = ru.ReString (txt)

        if  rs // '^(?P<one>.+?)\s*(?P<op><|<<|>|>>)\s*(?P<two>.+)$' :
            res = rs.get ()
            return (res['one'], res['two'], res['op'])

        else :
            return (txt, txt, '=')


    # --------------------------------------------------------------------------
    #
    def stage_in_workload (self, workload) :

        for task_id in workload.tasks :
            self._stage_in_task (workload.tasks[task_id])


    # -------------------------------
    def _stage_in_task (self, task) :

        for unit_id in task.units :
            self._stage_in_unit (task.units[unit_id])


    # -------------------------------
    def _stage_in_unit (self, unit) :

        # stage in only once
        if  unit.staged_in :
            return

        # do nothing if nothing to do
        if  not len(unit.inputs) :
            return

        pilot    = troy.Pilot (unit.session, unit.pilot_id)
        resource = pilot.resource

        # fix the resource placeholders in the unit descriptions.  Get the troy
        # resource config, merge it conservatively into the pilot config, and
        # expand values with resource config settings
        resource_cfg = unit.session.get_resource_config (resource)
        unit.merge_description (resource_cfg)
        workdir = unit.working_directory

        # sanity checks
        if  not workdir :
            raise RuntimeError ("no working directory defined for %s - cannot stage-in" % unit.id)

        if  not pilot :
            raise RuntimeError ("unit %s not bound  - cannot stage-in" % unit.id)

        if  not resource :
            raise RuntimeError ("pilot not bound %s - cannot stage-in" % unit.id)

        for fin in unit.inputs :

            if  not isinstance (fin, basestring) :
                raise TypeError ("Input specs need to be strings, not %s" % type(fin))

            one, two, op = self._parse_staging_directive (fin)

            if  op in ['>>'] :
                raise ValueError ("op '>>' not yet supported for input staging")

            if  op not in ['>', '='] :
                raise ValueError ("'%s' not supported for input staging" % op)

            troy._logger.info ("staging_in %s < %s / %s / %s" \
                                         %  (one, pilot.resource, workdir, two))

            self._stage_in_file (one, pilot.resource, workdir, two)

        unit.staged_in = True


    # --------------------------------------------------------------------------
    #
    def _stage_in_file (self, src, resource, workdir, tgt) :
        """
        src file element can contain wildcards.  
        tgt can not contain wildcards -- but must be a directory URL.
        """

        # make sure we have an absolute target working dir
        if  workdir[0] != '/' : 
            raise ValueError ("target directory must have absolute path, not %s"
                    % workdir)

        # make sure tgt path is absolute -- if not, its relative to workdir
        if  tgt[0] != '/' :
            tgt = os.path.normpath ("%s/%s" % (workdir, tgt))

        # make sure src path is absolute -- if not, its relative to pwd
        if  src[0] != '/' :
            src = os.path.normpath ("%s/%s" % (os.getcwd(), src))

        # if src is not a fully qualified URL, interpret it as local path
        src_url = saga.Url (src)
        if  not src_url.host and not src_url.schema :
            src_url = saga.Url ("file://localhost%s" % src)

        # find a file transfer schema which matches the resource access
        resource_url = saga.Url (resource)
        if  resource_url.schema.endswith ('ssh+') :
            resource_url.schema = 'ssh'
        if  resource_url.schema.endswith ('+ssh') :
            resource_url.schema = 'ssh'
        if  resource_url.schema.endswith ('fork') :
            resource_url.schema = 'file'

        troy._logger.debug ('copy %s -> %s / %s' % (src_url, resource_url, tgt))

        # if needed, create a dir handle to the target resource and cache it
        if  not str(resource) in self._dir_cache :
            self._dir_cache[str(resource)] = \
                 saga.filesystem.Directory (resource_url, session=self.session)

        # use cached dir handle, point it to the target dir (create as needed), 
        # and copy the file
        tgt_dir = self._dir_cache[str(resource)]
        tgt_dir.change_dir (os.path.dirname (tgt), saga.filesystem.CREATE_PARENTS)
        tgt_dir.copy       (src_url, tgt)


    # --------------------------------------------------------------------------
    #
    def stage_out_workload (self, workload) :

        for task_id in workload.tasks :
            self._stage_out_task (workload.tasks[task_id])
        return

    # -------------------------------
    def _stage_out_task (self, task) :

        for unit_id in task.units :
            self._stage_out_unit (task.units[unit_id])
        return

    # -------------------------------
    def _stage_out_unit (self, unit) :

        # stage in only once
        if  unit.staged_out :
            return

        # do nothing if nothing to do
        if  not len(unit.outputs) :
            return

        pilot    = troy.Pilot (unit.session, unit.pilot_id)
        resource = pilot.resource
        workdir  = unit.working_directory

        # sanity checks
        if  not workdir :
            raise RuntimeError ("no working directory defined for %s - cannot stage-out" % unit.id)

        if  not pilot :
            raise RuntimeError ("unit %s not bound  - cannot stage-out" % unit.id)

        if  not resource :
            raise RuntimeError ("pilot not bound %s - cannot stage-out" % unit.id)

        for fout in unit.outputs :

            if  not isinstance (fout, basestring) :
                raise TypeError ("Input specs need to be strings, not %s" % type(fout))

            one, two, op = self._parse_staging_directive (fout)

            if  op in ['<<'] :
                raise ValueError ("'<<' not yet supported for output staging")

            if  op not in ['<', '='] :
                raise ValueError ("'%s' not supported for output staging" % op)

            troy._logger.info ("staging_out %s < %s / %s / %s" \
                                         %  (one, pilot.resource, workdir, two))
            self._stage_out_file (one, pilot.resource, workdir, two)

        unit.staged_out = True

    # --------------------------------------------------------------------------
    #
    def _stage_out_file (self, tgt, resource, srcdir, src) :
        """
        src file element can contain wildcards.  
        tgt can not contain wildcards -- but it can be a directory URL (and, in
        fact, is interpreted as such if src contains wildcard chars).
        """

        if  tgt[0] != '/' :
            tgt = "%s/%s" % (os.getcwd(), tgt)

        # HACK -- URL parsers are picky about paths starting with '//': those
        # are (correctly) interpreted as empty '//hostname/path', which is not
        # what we want.  So we normalize paths at least at the boundaries.
        while srcdir   [ 0] == '/' : srcdir   = srcdir   [1:  ]
        while srcdir   [-1] == '/' : srcdir   = srcdir   [0:-1]
        while resource [-1] == '/' : resource = resource [0:-1]


        src_url          = saga.Url ("/%s/%s" % (srcdir, src))
        tgt_url          = saga.Url ("file://localhost%s" % tgt)
        src_dir_url      = saga.Url (src_url) # deep copy
        src_dir_url.path = os.path.dirname (src_url.path)

        # find a file transfer schema which matches the resource access
        resource_url = saga.Url (resource)
        if  resource_url.schema.endswith ('ssh+') :
            resource_url.schema = 'ssh'
        if  resource_url.schema.endswith ('+ssh') :
            resource_url.schema = 'ssh'
        if  resource_url.schema.endswith ('fork') :
            resource_url.schema = 'file'

        troy._logger.debug ('copy %s <- %s' % (tgt_url, src_url))

        # if needed, create a dir handle to the target resource and cache it
        if  not str(resource) in self._dir_cache :
            self._dir_cache[str(resource)] = \
                 saga.filesystem.Directory (resource_url, session=self.session)

        # use cached dir handle, point it to the target dir (create as needed), 
        # and copy the file
        src_dir = self._dir_cache[str(resource)]
        src_dir.change_dir (src_dir_url.path)
        src_dir.copy       (src_url, tgt_url)


# ------------------------------------------------------------------------------

