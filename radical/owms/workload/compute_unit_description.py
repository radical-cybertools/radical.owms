
__author__    = "RADICAL Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


from   radical.owms.constants import *
import radical.owms
from   radical.owms import utils  as tu
import radical.utils              as ru


# ------------------------------------------------------------------------------
#
class ComputeUnitDescription (tu.Properties) :
    """
    The `ComputeUnitDescription` class is a simple container for properties
    which describe a :class:`ComputeUnit`, i.e. a workload element.
    `ComputeUnitDescription`s are submitted to :class:`WorkloadManager`
    instances on `add_task`, and are internally used to create
    :class:`ComputeUnit` instances.

    FIXME: description of supported properties goes here
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, descr={}) :

        tu.Properties.__init__ (self, descr)

        # register properties
        self.register_property ('executable')
        self.register_property ('arguments')
        self.register_property ('working_directory')
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

