
# ------------------------------------------------------------------------------
#
# below are the state enums for the various stateful objects in troy.  State
# diagrams are extremely simple right now -- state progression is only ever
# linear, in the order listed.  The only exception are the final state FAILED
# which can be reached at any time.
#
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
#
# workload states
#
DESCRIBED   = 'Described'   # tasks known
PLANNED     = 'Planned'     # overlay derived
TRANSLATED  = 'Translated'  # tasks derived
SCEDULED    = 'Sceduled'    # tasks bound
DISPATCHED  = 'Dispatched'  # tasks dispatched
COMPLETED   = 'Completed'   # tasks completed
FAILED      = 'Failed'      # oops


# ------------------------------------------------------------------------------
#
# Task states
#
DESCRIBED   = 'Described'   # i.e. New
TRANSLATED  = 'Translated'  # CUs derived
SCEDULED    = 'Sceduled'    # CUs bound to pilot
DISPATCHED  = 'Dispatched'  # CUs dispatched to pilot
COMPLETED   = 'Completed'   # CUs completed
FAILED      = 'Failed'      # oops


# ------------------------------------------------------------------------------
#
# overlay states
#
DESCRIBED   = 'Described'   # requirements known
TRANSLATED  = 'Translated'  # pilots derived
SCHEDULED   = 'Scheduled'   # pilots sceduled
PROVISIONED = 'Provisioned' # pilots provisioned
COMPLETED   = 'Completed'   # pilots completed 
FAILED      = 'Failed'      # oops


# ------------------------------------------------------------------------------
#
# pilot states
#
DESCRIBED   = 'Described'   # i.e. New
SCHEDULED   = 'Scheduled'   # assigned to a resource
PROVISIONED = 'Provisioned' # submitted to / running on a resource
COMPLETED   = 'Completed'   # finished as planned
FAILED      = 'Failed'      # oops


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

