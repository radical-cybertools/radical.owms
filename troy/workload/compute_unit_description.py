

import troy.utils            as tu
from   troy.constants    import *
import troy


# ------------------------------------------------------------------------------
#
class ComputeUnitDescription (tu.Attributes) :
    """
    The `ComputeUnitDescription` class is a simple container for attributes
    which describe a :class:`ComputeUnit`, i.e. a workload element.
    `ComputeUnitDescription`s are submitted to :class:`WorkloadManager`
    instances on `add_task`, and are internally used to create
    :class:`ComputeUnit` instances.

    FIXME: description of supported attributes goes here
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, descr={}) :

        tu.Attributes.__init__ (self, descr)

        # register attributes
        self.register_property ('executable')
        self.register_property ('arguments')
        # FIXME: complete...



    # --------------------------------------------------------------------------
    #
    def __str__ (self) :

        return str(self.as_dict ())


    # --------------------------------------------------------------------------
    #
    def __repr__ (self) :

        return (self.as_dict ())


# ------------------------------------------------------------------------------

