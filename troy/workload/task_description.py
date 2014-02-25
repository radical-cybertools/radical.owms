
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils  as ru
import troy.utils     as tu


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
        self.cardinality       = 1
        self.executable        = None
        self.arguments         = list()
        self.stdin             = None
        self.stdout            = None

        self.cores             = 1

        self.inputs            = list()
        self.outputs           = list()

        tu.Properties.__init__ (self, descr)


    def expand_description (self, session) :

        # This will apply any application configuration wildcards we find in the
        # session config.
        
        td_dict = self.as_dict()
        print td_dict
        ru.dict_stringexpand (td_dict, session.cfg)
        print td_dict

        # we need to re-initialize our properties with the expanded dict values
        tu.Properties.__init__ (self, td_dict)


# ------------------------------------------------------------------------------

