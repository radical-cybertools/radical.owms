
__author__    = "RADICAL Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


from   radical.owms.constants import *
import radical.owms
from   radical.owms import utils  as tu
import radical.utils              as ru


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
        self.register_property ('cores')
        self.register_property ('walltime')


    # --------------------------------------------------------------------------
    #
    def __str__ (self) :

        return str(self.as_dict ())


# ------------------------------------------------------------------------------

