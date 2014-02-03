
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils as ru
import os
import pprint
import saga
import troy
import logging
import radical.utils.logger as rul


# ------------------------------------------------------------------------------
#
def _format_log_level (log_level) :

    return {
            'debug'    : logging.DEBUG,
            'info'     : logging.INFO,
            'warning'  : logging.WARNING,
            'error'    : logging.ERROR,
            'critical' : logging.CRITICAL
            } [log_leverl.lower()]

    raise ValueError ('%s is not a valid value for log_level.' \
                   % (log_level, log_level))


# ------------------------------------------------------------------------------
#

# This dict defines the troy configuration hierarchy -- sections contained in
# here are viable config sections.  For each entry, an arbitrary sub-hierarchy
# is supported.
#
# For example, the structure below defines an entry for
# 'workload_manager:dispatcher', but any sub-dict beneath that entry would be
# permitted, such as for the dispatcher plugins.

_troy_config_skeleton = {
        'log_level'           : int( 0),
        'resource_config'     : None,
        'planner'             : {
            'planner'         : dict(),
        },
        'overlay_manager'     : {
            'dispatcher'      : dict(),
            'provisioner'     : dict(),
            'scheduler'       : dict(),
            'transformer'     : dict(),
            'translator'      : dict(),
        },
        'workload_manager'    : {
            'dispatcher'      : dict(),
            'inspector'       : dict(),
            'scheduler'       : dict(),
            'transformer'     : dict(),
            'translator'      : dict(),
        },
        'resources'           : dict(),
        'application'         : dict(),
    }


_resource_config_skeleton = {
        'type'                : list(),
        'home'                : None,
        'queue'               : None,
        'walltime'            : int(0)
    }


# ------------------------------------------------------------------------------
#
class Session (saga.Session) : 

    def __init__ (self, user_cfg={}, default=True) :

        # FIXME: the whole config setup should be moved to troy/config.py, once
        # we converged on a format on radical level... 

        # set saga apitype for clean inheritance (cpi to api mapping relies on
        # _apitype)
        self._apitype = 'saga.Session'

        # read the ~/.troy.cfg, which uses ini format
        print 'read  troy cfg'
        self.cfg = ru.read_json_str ("%s/.troy.json" % os.environ['HOME'])
        self._check_config ()

        # the user config is passed as python dict, and merged into the config.
        print 'merge user cfg'
        print user_cfg
        ru.dict_merge (self.cfg, user_cfg, merge_policy='overwrite')
        self._check_config ()


        # read the json formatted resource config
        print 'read  rsrc cfg'
        resource_cfg_file = "%s/resource.json" % os.path.dirname (troy.__file__)
        resource_cfg      = ru.read_json_str (resource_cfg_file)

        self.cfg['resources'] = resource_cfg
        self._check_config ()

        # if the troy.cfg also has a user specified resource config, read that
        # and merge it in
        if  'resource_config' in self.cfg and \
            self.cfg['resource_config']   :

            print 'merge ursc cfg'
            resource_user_cfg_file = self.cfg['resource_config']
            print 'merge ursc cfg %s' % resource_user_cfg_file
            resource_user_cfg      = ru.read_json_str (resource_user_cfg_file)
            ru.dict_merge (self.cfg['resources'], resource_user_cfg, 
                           merge_policy='overwrite')
            self._check_config ()


        # but we set the log level as indicated in the troy config or user
        # config
        if  'troy' in self.cfg :
            if 'log_level' in cfg['troy'] :
                log_level  =  cfg['troy']['log_level']
                troy._logger.setLevel (log_level)

        saga.Session.__init__ (self, default)

    # --------------------------------------------------------------------------
    #
    def get_config (self, path='troy') :

        if  isinstance (path, basestring) :
            path = path.split (':')

        if  path[0] == 'troy' :
            path = path[1:]

        current_cfg  = self.cfg
        current_path = 'troy'

        for elem in path :
            if  not elem in current_cfg :
                raise RuntimeError ('no config "%s" beneath %s' \
                        % (':'.join (path), current_path))

            if  not istinstance (current_cfg[elem], dict) :
                raise TypeError ('no config dict "%s" beneath %s' \
                        % (':'.join (path), current_path))

            current_config = current_config[elem]

        return current_config


    # --------------------------------------------------------------------------
    #
    def _check_config (self) :

        if  not self.cfg :
            raise RuntimeError ('Troy found no configuration')

        # merge with the skeleton to make sure all keys exist and are set to
        # defaults
        ru.dict_merge (self.cfg, _troy_config_skeleton)

        # we know know we have a resource dict -- handle all resource configs
        # simmilarly: merge with skeleton to ensure completeness...
        for res_name in self.cfg['resources'] :
            ru.dict_merge (self.cfg['resources'][res_name], 
                           _resource_config_skeleton)

        print "-----------------------------"
        pprint.pprint (self.cfg)


# ------------------------------------------------------------------------------
#
class Context (saga.Context) : 

    def __init__ (self, ctype) :

        self._apitype = 'saga.Context'

        saga.Context.__init__ (self, ctype)
    

# ------------------------------------------------------------------------------

