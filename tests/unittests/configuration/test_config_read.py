
__author__    = "Mark Santcroos"
__copyright__ = "Copyright 2013, RADICAL @ Rutgers"
__license__   = "MIT"


import pprint
import radical.utils.testing as rut

import troy


# ------------------------------------------------------------------------------
#
def test_config_read():
    """
    test configuration reading
    """

    cf = troy.Configuration()

    general = cf.get_config ('general')
    lucky = general['i_feel_lucky'].get_value ()
    assert lucky == 'yes', 'Dont feeling lucky apparently!'




