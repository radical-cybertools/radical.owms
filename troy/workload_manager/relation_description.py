

import radical.utils   as ru
import saga.attributes as sa


# ------------------------------------------------------------------------------
#
class RelationDescription (sa.Attributes) :
    """
    The `RelationDescription` class is a simple container for attributes which
    describe a :class:`Relation`, i.e. a workload element.  `RelationDescription`s are
    submitted to :class:`WorkloadManager` instances on `add_relation`, and ar
    internally used to create :class:`Relation` instances.

    FIXME: description of supported attributes goes here
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, dictionary={}) :


        # set attribute interface properties
        self._attributes_extensible  (True)  # FIXME
        self._attributes_camelcasing (True)
    
        # register attributes
        # FIXME

        self.update (dictionary)


# ------------------------------------------------------------------------------
#
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

