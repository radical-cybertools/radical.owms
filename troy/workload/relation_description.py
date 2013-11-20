

import radical.utils   as ru
import saga.attributes as sa

import troy
from   troy.constants import *


# ------------------------------------------------------------------------------
#
class RelationDescription (sa.Attributes) :
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


        # set attribute interface properties
        self._attributes_extensible  (True)  # FIXME
        self._attributes_camelcasing (True)
    
        # register attributes
        # FIXME

        sa.Attributes.__init__ (self, descr)


    # --------------------------------------------------------------------------
    #
    def _dump (self) :

        self._attributes_dump ()


# ------------------------------------------------------------------------------

