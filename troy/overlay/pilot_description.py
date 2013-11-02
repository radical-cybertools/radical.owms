

import radical.utils   as ru
import saga.attributes as sa

import troy
from   troy.constants import *


# ------------------------------------------------------------------------------
#
class PilotDescription (sa.Attributes) :
    """
    The `PilotDescription` class is a simple container for attributes which
    describe a :class:`Pilot`, i.e. a overlay element.  `PilotDescription`s are
    submitted to :class:`OverlayManager` instances on `add_pilot`, and are
    internally used to create :class:`Pilot` instances.

    FIXME: description of supported attributes goes here
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, dictionary={}) :


        sa.Attributes.__init__ (self, dictionary)

        # set attribute interface properties
        self._attributes_extensible  (True)  # FIXME
        self._attributes_camelcasing (True)

        pd_id = ru.generate_id ('pd.')

        # register attributes
        self._attributes_register   ('id',        pd_id,     sa.STRING,
                                     sa.SCALAR, sa.READONLY)

        # FIXME


    # --------------------------------------------------------------------------
    #
    def _dump (self) :

        self._attributes_dump ()


# ------------------------------------------------------------------------------

