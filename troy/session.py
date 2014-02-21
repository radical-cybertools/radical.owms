
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils as ru
import os
import re
import fnmatch
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

_config_skeleton = {
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

        # accept any number of user configs
        if  not isinstance (user_cfg, list) :
            user_cfg = [user_cfg]


        # set saga apitype for clean inheritance (cpi to api mapping relies on
        # _apitype)
        self._apitype = 'saga.Session'

        resource_cfg = "%s/resources.json" % os.path.dirname (troy.__file__)
        config_dir   = "%s/.troy"          % os.environ.get  ('HOME', '/etc/')
        config_env   = "%s"                % os.environ.get  ('TROY_CONFIG', None)

        # we read our base config from $HOME/troy/* by default, but also accept
        # other locations if $TROY_CONFIG is set.  Items later in the list below
        # overwrite earlier ones.
        self.cfg = tu.get_config ([_config_skeleton,
                                   resource_cfg    , 
                                   config_dir      ,
                                   config_env      ] + user_cfg)

        # make sure that the resource sections in the config have the minimal
        # set of entries
        for res_name in self.cfg['resources'] :
            ru.dict_merge (self.cfg['resources'][res_name], 
                           _resource_config_skeleton, 
                           policy='preserve')


        # we set the log level as indicated in the troy config or user
        # config, fallback being log level ERROR
        log_level = 'ERROR'
        log_level = self.cfg.get   ('log_level',    log_level)
        log_level = os.environ.get ('TROY_VERBOSE', log_level)
        troy._logger.setLevel (log_level)


        # now that config parsing is done, we can create the session ID
        session_id_stub = self.cfg.get ("session_id", "session.")
        self.id         = ru.generate_id (session_id_stub, mode=ru.ID_UNIQUE)
        troy._logger.info ("session id: %s" % self.id)
        
        # and initialize the inherited saga session
        tu.Timed.__init__ (self, 'troy.Session', self.id)
        self.timed_method ('saga.Session', ['init'],  
                           saga.Session.__init__, [self, default])

        print '--------------------------------'
        self._dump()
        print '--------------------------------'
      # sys.exit()


    # --------------------------------------------------------------------------
    #
    def __deepcopy__ (self, other) :
        # FIXME

        return self

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
    def _dump (self) :

        print ' -------------------------------------'
        import pprint 
        pprint.pprint (self.cfg)
        print ' -------------------------------------'


# ------------------------------------------------------------------------------
#
class Context (saga.Context) : 

    # --------------------------------------------------------------------------
    #
    def __init__ (self, ctype) :

        self._apitype = 'saga.Context'

        saga.Context.__init__ (self, ctype)
    

# ------------------------------------------------------------------------------

