
__author__    = "Mark Santcroos"
__copyright__ = "Copyright 2013, RADICAL @ Rutgers"
__license__   = "MIT"


import os
import radical.utils.testing as rut

import radical.owms


# ------------------------------------------------------------------------------
#
def test_config_read():
    """
    test configuration reading
    """

    os.environ ['RADICAL_OWMS_CONFIG'] = "%s/radical_owms.cfg" % os.path.dirname (__file__)

    configurable = radical.owms.Configuration ()
    config       = configurable.get_config ('general')
    outdir       = config['output_directory'].get_value ()

    assert (outdir == '/Users/mark/agent'), "%s != DEBUG" % (loglevel)

