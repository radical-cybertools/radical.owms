

import troy.utils         as tu
from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
class RelationDescription (tu.Attributes) :
    """
    The `RelationDescription` class is a simple container for attributes which
    describe a :class:`Relation`, i.e. a workload element.  `RelationDescription`s are
    submitted to :class:`WorkloadManager` instances on `add_relation`, and are
    internally used to create :class:`Relation` instances.

    FIXME: description of supported attributes goes here
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, descr={}) :


        # register attributes
        # FIXME

        tu.Attributes.__init__ (self, descr)


# ------------------------------------------------------------------------------

