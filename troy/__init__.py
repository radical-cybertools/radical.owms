
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


# ------------------------------------------------------------------------------

