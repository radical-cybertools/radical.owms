
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

    configurable = troy.Configuration ()
    config       = configurable.get_config ('general')
    outdir       = config['output_directory'].get_value ()

    assert (outdir == '/Users/mark/agent'), "%s != DEBUG" % (loglevel)

