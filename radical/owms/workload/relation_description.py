
__author__    = "RADICAL Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


from   radical.owms.constants import *
import radical.owms
from   radical.owms import utils  as tu
import radical.utils              as ru


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

