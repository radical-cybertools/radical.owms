import radical.utils.config as ruc


# ------------------------------------------------------------------------------
#
# a set of pre-defined options
#

class TroyConfiguration(ruc.Configurable):

    _bundle_options = [
        {
            'category'      : 'bundle',
            'name'          : 'casing',
            'type'          : str,
            'default'       : 'default',
            'valid_options' : ['default', 'lower', 'upper'],
            'documentation' : "This option determines the casing of example's output",
            'env_variable'  : 'EXAMPLE_CONFIG_CASING'
        },
        {
            'category'      : 'config',
            'name'          : 'excluded',
            'type'          : list,
            'default'       : '',
            'valid_options' : [],
            'documentation' : "This option determines set of excluded components",
            'env_variable'  : ''
        }
    ]

    def __init__(self):

        # set the configuration options for this object
        ruc.Configurable.__init__       (self, 'troy')
        ruc.Configurable.config_options (self, 'troy.bundles', _config_options)
        self._cfg = self.get_config('troy.engine')
