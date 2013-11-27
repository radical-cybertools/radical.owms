
__author__ = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__ = "MIT"


import radical.utils      as ru
import troy.utils         as tu
from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
class OverlayDescription (tu.Attributes) :
    """
    The `OverlayDescription` class is a simple container for attributes which
    describe a :class:`Overlay`.  `OverlayDescription`s passed to `Overlay`
    instances on construction, to initialize their configuration.

    FIXME: description of supported attributes goes here
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, descr={}) :


        tu.Attributes.__init__ (self, descr)

        # register attributes
        self.register_property ('cores')
        self.register_property ('wall_time')


    # --------------------------------------------------------------------------
    #
    def __str__ (self) :

        return str(self.as_dict ())


# ------------------------------------------------------------------------------

