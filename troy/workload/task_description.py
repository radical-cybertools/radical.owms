


import radical.utils      as ru
import troy.utils         as tu
import troy
from   troy.constants import *


# ------------------------------------------------------------------------------
#
class TaskDescription (tu.Attributes) :
    """
    The `TaskDescription` class is a simple container for attributes which
    describe a :class:`Task`, i.e. a workload element.  `TaskDescription`s are
    submitted to :class:`WorkloadManager` instances on `add_task`, and are
    internally used to create :class:`Task` instances.

    FIXME: description of supported attributes goes here
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, descr={}) :

        # register attributes
        self.register_property ('tag')
        self.register_property ('executable')
        self.register_property ('arguments')

        tu.Attributes.__init__ (self, descr)

    # --------------------------------------------------------------------------
    #
    def __str__ (self) :

        return str(self.as_dict ())


    # --------------------------------------------------------------------------
    #
    def __repr__ (self) :

        return self.description


# ------------------------------------------------------------------------------

