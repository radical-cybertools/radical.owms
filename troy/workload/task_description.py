

import radical.utils   as ru
import saga.attributes as sa

import troy
from   troy.constants import *


# ------------------------------------------------------------------------------
#
class TaskDescription (sa.Attributes) :
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

        # set attribute interface properties
        self._attributes_extensible  (False)
        self._attributes_camelcasing (True)

        # register attributes
        self._attributes_register    (TAG,        None, sa.STRING, sa.SCALAR, sa.WRITEABLE)
        self._attributes_register    (EXECUTABLE, None, sa.STRING, sa.SCALAR, sa.WRITEABLE)
        self._attributes_register    (ARGUMENTS,  None, sa.STRING, sa.VECTOR, sa.WRITEABLE)

        sa.Attributes.__init__ (self, descr)

    # --------------------------------------------------------------------------
    #
    def __str__ (self) :

        return str(self.as_dict ())


    # --------------------------------------------------------------------------
    #
    def __repr__ (self) :

        return self.description


    # --------------------------------------------------------------------------
    #
    def _dump (self) :

        self._attributes_dump ()


# ------------------------------------------------------------------------------

