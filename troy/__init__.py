
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"

# ------------------------------------------------------------------------------
#
# the Troy API layer
#
from constants  import *
from config     import Configuration
from session    import Session
from session    import Context

from planner    import Planner

from workload   import ComputeUnitDescription
from workload   import ComputeUnit
from workload   import TaskDescription
from workload   import Task
from workload   import RelationDescription
from workload   import Relation
from workload   import Workload
from workload   import WorkloadManager
from workload   import DataStager

from overlay    import Pilot            # should be private
from overlay    import PilotDescription # should be private
from overlay    import Overlay
from overlay    import OverlayDescription
from overlay    import OverlayManager

from strategy   import manage_workload, execute_workload

# internal helper classes, exposed for plugin developers
from bundle_wrapper import BundleManager
from plugin_base    import PluginBase

# ------------------------------------------------------------------------------

import os
import radical.utils.logger as rul

version = open (os.path.dirname (os.path.abspath (__file__)) + "/VERSION", 'r').read().strip()
"""
Please always note the Troy version when opening tickets or asking for support
on the Troy mailing lists!
"""

# FIXME: the logger init will require a 'classical' troy config, which is
# different from the json based config we use now.   May need updating once the
# radical configuration system has changed to json
_logger = rul.logger.getLogger  ('troy')
_logger.info ('troy            version: %s' % version)


# ------------------------------------------------------------------------------

