
__author__    = "Mark Santcroos"
__copyright__ = "Copyright 2013, RADICAL @ Rutgers"
__license__   = "MIT"


import os
import radical.utils.testing as rut

import troy


# ------------------------------------------------------------------------------
#
def test_config_read():
    """
    test configuration reading
    """

    os.environ ['TROY_CONFIG'] = "%s/troy.cfg" % os.path.dirname (__file__)

    configurable  =  troy.Configuration ()
    config        =  configurable.get_config ('general')
    loglever      =  config['log_level'].get_value ()

    assert (loglevel == '42'), "%s != 42" % (loglevel)

