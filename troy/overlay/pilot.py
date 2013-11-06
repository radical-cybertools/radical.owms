

__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils   as ru
import saga.attributes as sa

from troy.constants import *


"""
Represent a pilot, as element of a troy.Overlay.
"""

# -----------------------------------------------------------------------------
#
class Pilot (sa.Attributes) :
    """
    """

    def __init__ (self, descr, overlay_manager) :
        """
        Create a new pilot

        Each new pilot is assigned a new ID.

        Later implementations may allow for an additional id parameter, 
        to reconnect to the thus identified pilot instance.  
        """

        # initialize state
        pid   = ru.generate_id ('p.')

        if  not 'tag' in descr :
            raise ValueError ("no 'tag' in PilotDescription")

        # set attribute interface properties
        self._attributes_extensible  (False)
        self._attributes_camelcasing (True)

        # register attributes
        self._attributes_register   (ID,          pid,             sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   (STATE,       DESCRIBED,       sa.STRING, sa.SCALAR, sa.READWRITE)  # FIXME
        self._attributes_register   (TAG,         descr.tag,       sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   (DESCRIPTION, descr,           sa.ANY,    sa.SCALAR, sa.READONLY)
        self._attributes_register   ('manager',   overlay_manager, sa.ANY,    sa.SCALAR, sa.READONLY)
        self._attributes_register   ('resource',  None,            sa.STRING, sa.SCALAR, sa.READWRITE)  # FIXME
         
        # FIXME: complete attribute list, dig attributes from description,
        # perform sanity checks


    # --------------------------------------------------------------------------
    #
    def _bind (self, resource) :

        self.resource = resource


    # --------------------------------------------------------------------------
    #
    def _dump (self) :

        self._attributes_dump ()



