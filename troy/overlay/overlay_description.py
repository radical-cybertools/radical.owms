

import radical.utils   as ru
import saga.attributes as sa

import troy
from   troy.constants import *


# ------------------------------------------------------------------------------
#
class OverlayDescription (sa.Attributes) :
    """
    The `OverlayDescription` class is a simple container for attributes which
    describe a :class:`Overlay`.  `OverlayDescription`s passed to `Overlay`
    instances on construction, to initialize their configuration.

    FIXME: description of supported attributes goes here
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, dictionary={}) :


        sa.Attributes.__init__ (self, dictionary)

        # set attribute interface properties
        self._attributes_extensible  (True)  # FIXME
        self._attributes_camelcasing (True)

        # register attributes
        self._attributes_register    ('cores',     None, sa.INT, sa.SCALAR, sa.WRITEABLE)
        self._attributes_register    ('wall_time', None, sa.INT, sa.SCALAR, sa.WRITEABLE)


    # --------------------------------------------------------------------------
    #
    def _dump (self) :

        self._attributes_dump ()


# ------------------------------------------------------------------------------

