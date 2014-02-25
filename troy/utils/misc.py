
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import os
import sys
import glob

import radical.utils as ru
import troy


# ------------------------------------------------------------------------------
#
def get_config (params) :
    """
    This method attempts to obtain configuration settings from a variety of
    sources, depending on the parameter. it can point to an env var, or to
    a directory containing configuration files, or to a single configuration
    file, or to a list of any above, or it is a config dict already, or a list
    of such dicts.  In all cases, the config is obtained from the respective
    source (which is assumed json formatted in the case of config files), and
    a single merged and expanded dict is returned.
    """


    ret = dict()

    # always make params list for simpler code below
    if  not isinstance(params, list) :
        params = [params]


    for param in params :

        if  not param or None == param : 

            # we silently accept None's, to save some 
            # repetetetetive checks on the calling side
            continue


        elif isinstance (param, dict) :

            # simply merge it into the result
            ru.dict_merge (ret, param, policy='overwrite')


        elif isinstance (param, basestring) :
        
            # check if the string points to an env variable
            if  param in os.environ :
                # assume that the value of the env var is what we really want
                param = os.environ[param]

            # is string, is not env, must be a dir or a file
            if  os.path.isdir (param) :
                # config dir
                cfg_files = glob.glob ("%s/*" % param)
              # print 'is dir %s/*' % param
              # print cfg_files

            elif os.path.isfile (param) :
                # single config file
                cfg_files = [param]

            else :
                troy._logger.warning ("cannot handle config location %s" % param)
                cfg_files = list()

            print 'files: %s' % cfg_files
            # read and merge all config files
            for cfg_file in cfg_files :
                cfg_dict = dict()
                try :
                    cfg_dict = ru.read_json (cfg_file)
                    troy._logger.info ("reading  config in %s" % cfg_file)
                except Exception as e :
                    troy._logger.warning ("skipping config in %s (%s)" % (cfg_file, e))

              # import pprint
              # print '================'
              # print cfg_file
              # pprint.pprint (cfg_dict)
              # print '================'

                ru.dict_merge (ret, cfg_dict, policy='overwrite')



        else :
            raise TypeError ("get_config parameter must be (list of) dict or "
                             "string, not %s" % type(param))

  # print '================================'
  # pprint.pprint (ret)
  # print '================================'

    # expand config(s) before returning
    ru.dict_stringexpand (ret)

    return ret


# ------------------------------------------------------------------------------

