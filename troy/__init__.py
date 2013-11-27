
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"

version = 0.1

# ------------------------------------------------------------------------------
#
# provide Troy session and context
#
import saga

class Session (saga.Session) : pass
class Context (saga.Context) : pass


import radical.utils as ru
_logger = ru.logger.getLogger ('troy')

# ------------------------------------------------------------------------------
#
# the Troy API layer
#
from constants  import *


# ------------------------------------------------------------------------------
#
# and the internal Troy classes -- which are also exposed in Troy.v1
#
from config import Configuration

from planner    import Planner

from workload   import ComputeUnitDescription
from workload   import ComputeUnit
from workload   import TaskDescription
from workload   import Task
from workload   import RelationDescription
from workload   import Relation
from workload   import Workload
from workload   import WorkloadManager

from overlay    import Pilot            # should be private
from overlay    import PilotDescription # should be private
from overlay    import Overlay
from overlay    import OverlayDescription
from overlay    import OverlayManager

from bundle_wrapper import BundleManager

# ------------------------------------------------------------------------------

