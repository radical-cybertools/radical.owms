
__author__    = "RADICAL Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


# ------------------------------------------------------------------------------
#
# below are the state enums for the various stateful objects in radical.owms.  State
# diagrams are extremely simple right now -- state progression is only ever
# linear, in the order listed.  The only exception are the final state FAILED
# which can be reached at any time.
#
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
#
# Plugin selection wildcards
#
DEFAULT      = 'default'     # use default plugin as configured by radical.owms

# Why do we need an alias auto for AUTO?! 
# Could we change AUTOMATIC to DEFAULT? Just naming so definitevely a third 
# order concern.

AUTO         = 'auto'        # leave plugin selection to current radical.owms strategy
AUTOMATIC    =  AUTO         # alias


# ------------------------------------------------------------------------------
#
# workload states
#
DESCRIBED    = 'Described'   # tasks known
EXPANDED     = 'Expanded'    # tasks expanded
TRANSLATED   = 'Translated'  # tasks derived
BOUND        = 'Bound'       # tasks bound
DISPATCHED   = 'Dispatched'  # tasks dispatched
DONE         = 'Done'        # tasks completed
FAILED       = 'Failed'      # oops
CANCELED     = 'Canceled'    # tasks canceled
UNKNOWN      = 'Unknown'     # what?


# ------------------------------------------------------------------------------
#
# Task states
#
DESCRIBED    = 'Described'   # i.e. New
TRANSLATED   = 'Translated'  # Units derived
BOUND        = 'Bound'       # Units bound to pilot
DISPATCHED   = 'Dispatched'  # Units dispatched to pilot
DONE         = 'Done'        # Units completed
FAILED       = 'Failed'      # oops
CANCELED     = 'Canceled'    # Units canceled
UNKNOWN      = 'Unknown'     # what?


# ------------------------------------------------------------------------------
#
# Unit states -- we don't have radical.owms.compute_unit -- but we expect all adaptors to
# use that state model
#
DESCRIBED    = 'Described'   # Unit created
BOUND        = 'Bound'       # Unit bound to pilot
DISPATCHED   = 'Dispatched'  # Unit submitted to pilot
PENDING      = 'Pending'     # Unit scheduled on pilot
RUNNING      = 'Running'     # Unit active    on pilot
DONE         = 'Done'        # Unit completed
FAILED       = 'Failed'      # oops
CANCELED     = 'Canceled'    # Unit canceled
UNKNOWN      = 'Unknown'     # what?


# ------------------------------------------------------------------------------
#
# overlay states
#
DESCRIBED    = 'Described'   # requirements known
TRANSLATED   = 'Translated'  # pilots derived
SCHEDULED    = 'Scheduled'   # pilots scheduled
PROVISIONED  = 'Provisioned' # pilots provisioned
COMPLETED    = 'Completed'   # pilots completed 
CANCELED     = 'Canceled'    # pilots canceled
FAILED       = 'Failed'      # oops
UNKNOWN      = 'Unknown'     # what?


# ---------- --------------------------------------------------------------------
#
# pilot states
#
DESCRIBED    = 'Described'   # i.e. New
BOUND        = 'Bound'       # assigned to a resource
PROVISIONED  = 'Provisioned' # submitted to / running on a resource
COMPLETED    = 'Completed'   # finished as planned
CANCELED     = 'Canceled'    # finished as requested
FAILED       = 'Failed'      # oops
UNKNOWN      = 'Unknown'     # what?


# ------------------------------------------------------------------------------
# 
# constants for task description attributes
#
# RELATION_TIME
TAG              = 'Tag'             # non-unique identified
CARDINALITY      = 'Cardinality'     # Cardinality ;)

RELATION_TIME    = 'RelationTime'    # attribute key -- for cardinal subtasks
CONCURRENT       = 'Concurrent'      # subtasks are concurrent
SEQUENTIAL_START = 'SequentialStart' # subtasks start when previous ones started
SEQUENTIAL_END   = 'SequentialEnd'   # subtasks start when previous ones finished

RELATION_SPACE   = 'RelationSpace'   # attribute key -- for cardinal subtasks
COMMUNICATION    = 'Communication'   # subtasks directly exchange messages
SHARED_DATA      = 'SharedData'      # subtasks access the same data sets
SHARED_MEMORY    = 'SharedMemory'    # subtasks access the same data in memory

EXECUTABLE       = 'Executable'
ARGUMENTS        = 'Argument'
ENVIRONMENT      = 'Environment'


# ------------------------------------------------------------------------------
# 
# constants for relation description attributes
#
# RELATION_TIME
HEAD             = 'Head'            # leading  node for relation
TAIL             = 'Tail'            # trailing node for relation

RELATION_TIME    = 'RelationTime'    # attribute key
CONCURRENT       = 'Concurrent'      # start TAIL and  HEAD concurrently
SEQUENTIAL_START = 'SequentialStart' # start TAIL when HEAD is started
SEQUENTIAL_END   = 'SequentialEnd'   # start TAIL when HEAD is finished

RELATION_SPACE   = 'RelationSpace'   # attribute key
COMMUNICATION    = 'Communication'   # TAIL and HEAD directly exchange messages
PIPE             = 'Pipe'            # output stream of HEAD is input for TAIL
INPUT_OUTPUT     = 'InputOutput'     # output files of HEAD are input for TAIL
SHARED_DATA      = 'SharedData'      # HEAD and TAIL access the same data sets
SHARED_MEMORY    = 'SharedMemory'    # HEAD and TAIL access the same data in memory

PORT_NAME        = 'PortName'        # attribute key
PORT_VALUE       = 'PortValue'       # attribute key # FIXME: semantics?
INPUT_PORT       = 'PortValue'       # attribute key # FIXME: semantics?
OUTPUT_PORT      = 'PortValue'       # attribute key # FIXME: semantics?


# ------------------------------------------------------------------------------
# 
# constants for overlay description attributes
#
# RELATION_TIME
CORES            = 'Cores'           # number of required cores
WALL_TIME        = 'WallTime'        # overlay lifetime in minutes


# ------------------------------------------------------------------------------
# 
# constants for pilot description attributes
#
SIZE             = 'Size'            # number of cores


# ------------------------------------------------------------------------------
# 
# constants for object inspection
#
ID               = 'ID'              # object id
TAG              = 'TAG'             # object tag
STATE            = 'State'           # object state
DESCRIPTION      = 'Description'     # object description dict


# ------------------------------------------------------------------------------
# 
# constants for binding mode flags on workload_manager.scheduler_workload() calls
#
EARLY            = 'Early'
LATE             = 'Late'


# ------------------------------------------------------------------------------
#
# constants for guarding mode in the Planner
#
UPPER_LIMIT      = 'Upper'
LOWER_LIMIT      = 'Lower'
UNLIMITED        = 'Unlimited'


# ------------------------------------------------------------------------------

