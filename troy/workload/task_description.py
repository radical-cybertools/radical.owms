
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import os
import radical.utils      as ru
import troy.utils         as tu
from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
class TaskDescription (tu.Properties) :
    """
    The `TaskDescription` class is a simple container for properties which
    describe a :class:`Task`, i.e. a workload element.  `TaskDescription`s are
    submitted to :class:`WorkloadManager` instances on `add_task`, and are
    internally used to create :class:`Task` instances.

    FIXME: description of supported properties goes here
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, descr={}) :

        # set property defaults
        self.tag               = None
        self.executable        = None
        self.arguments         = list()
      # self.working_directory = '/tmp/troy.%s/' % os.getuid ()
        self.stdin             = None
        self.stdout            = None

        self.cores             = 1

        self.inputs            = list()
        self.outputs           = list()

        tu.Properties.__init__ (self, descr)

    # --------------------------------------------------------------------------
    #
    def __str__ (self) :

        return str(self.as_dict ())


    # --------------------------------------------------------------------------
    #
    def __repr__ (self) :

        return self.description


# ------------------------------------------------------------------------------

