
__author__ = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__ = "MIT"


import radical.utils      as ru
import troy.utils         as tu
from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
class OverlayDescription (tu.Properties) :
    """
    The `OverlayDescription` class is a simple container for properties which
    describe a :class:`Overlay`.  `OverlayDescription`s passed to `Overlay`
    instances on construction, to initialize their configuration.

    FIXME: description of supported properties goes here
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, descr=None) :

        if  not descr :
            descr = dict()

        tu.Properties.__init__ (self, descr)

        # register properties
        self.register_property ('workload_id')  # descr was derived from this
        self.register_property ('cores')
        self.register_property ('wall_time')


    # --------------------------------------------------------------------------
    #
    def __str__ (self) :

        return str(self.as_dict ())


# ------------------------------------------------------------------------------

