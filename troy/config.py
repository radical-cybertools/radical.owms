
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import pprint

import radical.utils.config    as ruc
import radical.utils.singleton as rus


# ------------------------------------------------------------------------------
#
# Takes a configuration file in the following format:
#
# [general]
# output_directory=/Users/mark/proj/troy/output
# log_level=42
# i_feel_lucky=yes
#
# [bundle]
# mode=local
# finished_job_trace=/Users/mark/bla
#
# [compute:india]
# endpoint=india.futuregrid.org
# type=moab
# port=22
# username=marksant
# ssh_key=/Users/mark/.ssh/id_rsa
# h_flag=True
#
# [compute:sierra]
# endpoint=sierra.futuregrid.org
# type=moab
# port=22
# username=marksant
# ssh_key=/Users/mark/.ssh/id_rsa
# h_flag=True
#

class Configuration (ruc.Configurable):

    __metaclass__ = rus.Singleton    

    def __init__(self):

        # set the configuration options for this object
        ruc.Configurable.__init__(self, 'troy')

        #ruc.Configurable.config_options (self, 'troy.bundles',  _bundle_section)
        #self._cfg = self.get_config('troy.engine')

        _general_section = [
        {
            # output_directory
            'category'      : 'general',
            'name'          : 'output_directory',
            'type'          : str,
            'default'       : '', # $HOME/troy
            'valid_options' : '',
            'documentation' : 'Troy working directory',
            'env_variable'  : ''
        }, {
            # log_level
            'category'      : 'general',
            'name'          : 'log_level',
            'type'          : str,
            'default'       : '0',
            'valid_options' : ['0', '1', '2', '3'],
            'documentation' : 'Verbosity mode',
            'env_variable'  : ''
        }]

        ruc.Configurable.config_options (self, 'general', _general_section)
        #general_config = ruc.Configurable.get_config(self, 'general')

        _bundle_section = [
        {
            # mode
            'category'      : 'bundle',
            'name'          : 'mode',
            'type'          : str,
            'default'       : 'local',
            'valid_options' : ['local', 'remote'],
            'documentation' : 'Mode of operation for bundles.',
            'env_variable'  : ''
        }, {
            # finished_job_trace
            'category'      : 'bundle',
            'name'          : 'finished_job_trace',
            'type'          : str,
            'default'       : '',
            'valid_options' : '',
            'documentation' : 'Storage of finished job traces for bundles',
            'env_variable'  : ''
        }]

        ruc.Configurable.config_options (self, 'bundle', _bundle_section)
        #bundle_config = ruc.Configurable.get_config(self, 'bundle')

        # Get all sections that begin with "compute:" and consider them endpoints
        cd = self.get_config_as_dict()
        all_sections = cd.keys()
        self.compute_sections = filter(lambda x: x.startswith('compute:'), all_sections)

        for section_name in self.compute_sections:

            _compute_section_template = [
            {
                # endpoint
                'category'      : section_name,
                'name'          : 'endpoint',
                'type'          : str,
                'default'       : '',
                'valid_options' : '',
                'documentation' : 'This option specifies the endpoint address of the '
                                  'resource',
                'env_variable'  : ''
            }, {
                # type
                'category'      : section_name,
                'name'          : 'type',
                'type'          : str,
                'default'       : 'moab',
                'valid_options' : ['moab', 'pbs'],
                'documentation' : 'This option specifies the type endpoint address of the resource',
                'env_variable'  : ''
            }, {
                # port
                'category'      : section_name,
                'name'          : 'port',
                'type'          : str,
                'default'       : '22',
                'valid_options' : '',
                'documentation' : 'Port to use at endpoint address of the resource',
                'env_variable'  : ''
            }, {
                # username
                'category'      : section_name,
                'name'          : 'username',
                'type'          : str,
                'default'       : '', # get_id()?
                'valid_options' : '',
                'documentation' : 'This option specifies the endpoint address of the resource',
                'env_variable'  : ''
            }, {
                # ssh_key
                'category'      : section_name,
                'name'          : 'ssh_key',
                'type'          : str,
                'default'       : '', # $HOME/.ssh/id_rsa ?
                'valid_options' : '',
                'documentation' : 'This option specifies the ssh key to use with the resource',
                'env_variable'  : ''
            }, {
                # password
                'category'      : section_name,
                'name'          : 'password',
                'type'          : str,
                'default'       : '',
                'valid_options' : '',
                'documentation' : 'Specifies the password to use with the resource',
                'env_variable'  : ''
            }, {
                # h_flag?
                'category'      : section_name,
                'name'          : 'h_flag',
                'type'          : bool,
                'default'       : True,
                'valid_options' : '',
                'documentation' : 'Heterogenerous resource type',
                'env_variable'  : ''
            }]

            ruc.Configurable.config_options (self, section_name,
                                             _compute_section_template)
            c = ruc.Configurable.get_config(self,section_name)

            endpoint = c['endpoint'].get_value ()

          # pprint.pprint(c)
          # import troy
          # troy._logger.debug ('endpoint: %s' % endpoint)


