
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import os
import radical.utils      as ru
import troy.utils         as tu
from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
class PilotDescription (tu.Properties) :
    """
    The `PilotDescription` class is a simple container for properties which
    describe a :class:`Pilot`, i.e. a overlay element.  `PilotDescription`s are
    submitted to :class:`OverlayManager` instances on `add_pilot`, and are
    internally used to create :class:`Pilot` instances.

    FIXME: description of supported properties goes here
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, descr={}) :

        # initialize properties
        tu.Properties.__init__ (self, descr)

        # property defaults
        self.size              = 1

        # properties as set
        for key in descr :
            self.set_attribute (key, descr[key])


    # --------------------------------------------------------------------------
    #
    def __str__ (self) :

        return str(self.as_dict ())


# ------------------------------------------------------------------------------

