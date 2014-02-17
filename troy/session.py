
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils as ru
import os
import re
import fnmatch
import pprint
import saga
import troy
import logging
import radical.utils as ru
import troy.utils    as tu



# ------------------------------------------------------------------------------
#
def _format_log_level (log_level) :

    return {
            'debug'    : logging.DEBUG,
            'info'     : logging.INFO,
            'warning'  : logging.WARNING,
            'error'    : logging.ERROR,
            'critical' : logging.CRITICAL
            } [log_level.lower()]

    raise ValueError ('%s is not a valid value for log_level.' % log_level)


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
        'log_level'                : int( 0),
        'resource_config'          : None,
        'resources'                : dict(),
        'planner'                : {
            'expand'               : dict(),
            'derive'               : dict(),
        },
        'overlay_manager'        : {
            'overlay_translator'   : dict(),
            'overlay_transformer'  : dict(),
            'overlay_scheduler'    : dict(),
            'overlay_provisioner'  : dict(),
        },
        'workload_manager'       : {
            'workload_parser'      : dict(),
            'workload_translator'  : dict(),
            'workload_transformer' : dict(),
            'workload_scheduler'   : dict(),
            'workload_dispatcher'  : dict(),
        },
        'strategy'               : {
            'strategy'             : dict(),
        },
    }


_resource_config_skeleton = {
        'type'      : list(),
        'username'  : None,
        'home'      : None,
        'queue'     : None,
        'walltime'  : int(60*24) # default: 1 day
    }


# ------------------------------------------------------------------------------
#
class Session (saga.Session, tu.Timed) : 

    # --------------------------------------------------------------------------
    #
    def __init__ (self, user_cfg=None, default=True) :

        if  user_cfg :
            if  isinstance (user_cfg, basestring) :
                user_cfg  = ru.read_json (user_cfg)
            elif isinstance (user_cfg, dict) :
                # just use it
                pass
            else :
                raise TypeError ("user_cfg must be filename or dict")

        # FIXME: the whole config setup should be moved to troy/config.py, once
        # we converged on a format on radical level... 

        # set saga apitype for clean inheritance (cpi to api mapping relies on
        # _apitype)
        self._apitype = 'saga.Session'
        self.user_cfg = user_cfg

        # read the ~/.troy.cfg, which uses ini format
        self.cfg = ru.read_json_str ("%s/.troy.json" % os.environ['HOME'])
        self._check_config ()

        # read the json formatted resource config
        resource_cfg_file = "%s/resource.json" % os.path.dirname (troy.__file__)
        resource_cfg      = ru.read_json_str (resource_cfg_file)

        if  not 'resources' in self.cfg :
            self.cfg['resources'] = dict()

        # overwrite whatever existed in troy.conf.
        ru.dict_merge (self.cfg['resources'], resource_cfg, policy='overwrite')
        self._check_config ()


        # if the troy.cfg also has a user specified resource config, read that
        # and merge it in
        if  'resource_config' in self.cfg and self.cfg['resource_config'] :

            resource_user_cfg_file = self.cfg['resource_config']
            resource_user_cfg      = ru.read_json_str (resource_user_cfg_file)
            ru.dict_merge (self.cfg['resources'], resource_user_cfg, 
                           policy='overwrite')
            self._check_config ()


        # the user config is passed as python dict, and merged into the config.
        ru.dict_merge (self.cfg, user_cfg, policy='overwrite')
        self._check_config ()

        # we set the log level as indicated in the troy config or user
        # config
        if 'log_level' in self.cfg :
            log_level  =  self.cfg['log_level']
            troy._logger.setLevel (log_level)

        # now that config parsing is done, we can create the session ID
        session_id_stub = "session."
        if 'session_id' in self.cfg :
            session_id_stub =  self.cfg['session_id']

        self.id = ru.generate_id (session_id_stub, mode=ru.ID_UNIQUE)
        troy._logger.info ("session id: %s" % self.id)
        
        tu.Timed.__init__ (self, 'troy.Session', self.id)
        self.timed_method ('saga.Session', ['init'],  
                           saga.Session.__init__, [self, default])



    # --------------------------------------------------------------------------
    #
    def get_config (self, path='troy') :

        if  isinstance (path, basestring) :
            path = path.split (':')

        if  path[0] == 'troy' :
            path = path[1:]

        current_cfg  = self.cfg
        current_path = 'troy'

        for idx, elem in enumerate(path) :

            if  not elem in current_cfg :
                # if this is the last path element, return an empty dict
                if  idx == len(path)-1 :
                    return dict()

                raise RuntimeError ('no config "%s" beneath %s' \
                        % (':'.join (path), current_path))

            if  not isinstance (current_cfg[elem], dict) :
                raise TypeError ('no config dict "%s" beneath %s' \
                        % (':'.join (path), current_path))

            current_cfg = current_cfg[elem]
            current_path = '%s:%s' % (current_path, elem)

        return current_cfg


    # --------------------------------------------------------------------------
    #
    def get_resource_config (self, resource) :

        # resources may be in fact URLs -- but resource configs use host
        # names as keys.  So we check if the URL is well formed and attempt
        # to extract the host
        # FIXME: cache results, URL parsing is expensive
        try :
            resource_url = saga.Url (resource)

            # the url string 'india.futuregrid.org' is parsed as url path
            # element, not as URL host name.
            if  resource_url.host :
                resource = resource_url.host

        except saga.SagaException as e :
            pass # probably not a URL :P


        resource_cfg = self.get_config ('resources')

        # default to a copy of the resource config skeleton
        troy._logger.debug ('create resource config for %s' % resource)
        ret = dict (_resource_config_skeleton)

        # check if have a match with one of the wildcards.
        for resource_key in resource_cfg.keys () :
            if  '*' in resource_key :
                resource_pattern = re.compile (fnmatch.translate (resource_key))
                if  resource_pattern.match (resource):
                    troy._logger.debug ('merge resource pattern %s for %s' \
                                     % (resource_key, resource))
                    ru.dict_merge (ret, resource_cfg[resource_key], policy='overwrite')

        # check if we have an exact match for the resource name.  This upersedes
        # the wildcard entries
        if  resource in resource_cfg :
            troy._logger.debug ('merge resource config for %s' % resource)
            ru.dict_merge (ret, resource_cfg[resource], policy='overwrite')

        # make sure the hostname is in the config
        ret['hostname'] = resource

        return ret


    # --------------------------------------------------------------------------
    #
    def _check_config (self) :

        if  not self.cfg :
            raise RuntimeError ('Troy found no configuration')

        # expand config with itself, to satisfy parameteter replacements where
        # possible
        ru.dict_stringexpand (self.cfg)

        # merge with the skeleton to make sure all keys exist and are set to
        # defaults
        ru.dict_merge (self.cfg, _troy_config_skeleton)

        # we now know we have a resource dict -- handle all resource configs
        # simmilarly: merge conservatively with skeleton to ensure completeness...
        for res_name in self.cfg['resources'] :
            ru.dict_merge (self.cfg['resources'][res_name], 
                           _resource_config_skeleton, 
                           policy='preserve')

        print "-----------------------------"
        pprint.pprint (self.cfg)


# ------------------------------------------------------------------------------
#
class Context (saga.Context) : 

    # --------------------------------------------------------------------------
    #
    def __init__ (self, ctype) :

        self._apitype = 'saga.Context'

        saga.Context.__init__ (self, ctype)
    

# ------------------------------------------------------------------------------

