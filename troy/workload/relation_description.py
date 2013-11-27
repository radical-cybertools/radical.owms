
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils      as ru
import troy.utils         as tu
from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
class RelationDescription (tu.Properties) :
    """
    The `RelationDescription` class is a simple container for properties which
    describe a :class:`Relation`, i.e. a workload element.  `RelationDescription`s are
    submitted to :class:`WorkloadManager` instances on `add_relation`, and are
    internally used to create :class:`Relation` instances.

    FIXME: description of supported properties goes here
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, descr={}) :


        # register properties
        # FIXME

        tu.Properties.__init__ (self, descr)


# ------------------------------------------------------------------------------

