
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import saga.attributes      as sa
import radical.utils        as ru

from   troy.constants   import *

"""
Represent a pilot-based overlay that is managed by TROY.
"""

# -----------------------------------------------------------------------------
#
@ru.Lockable
class Overlay (sa.Attributes) :
    """
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :
        """
        Create a new overlay instance.

        Each new overlay is assigned a new ID.

        Later (service oriented) Troy implementations may allow for an
        additional id parameter, to reconnect to the thus identified overlay
        instances.  
        """
        
        ol_id = ru.generate_id ('ol.')

        # set attribute interface properties
        self._attributes_extensible  (False)
        self._attributes_camelcasing (True)
    
        # register attributes, initialize state
        self._attributes_register   ('id',        ol_id,     sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('state',     DESCRIBED, sa.STRING, sa.SCALAR, sa.WRITEABLE) # FIXME
        self._attributes_register   ('error',     None,      sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('pilots',    dict(),    sa.ANY,    sa.VECTOR, sa.READONLY)


