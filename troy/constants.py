
# ------------------------------------------------------------------------------
#
# Workload and Overlay states
#
DESCRIBED  = 'Described'  # i.e. New
PLANNED    = 'Planned'
TRANSLATED = 'Translated'
SCHEDULED  = 'Scheduled'
DISPATCHED = 'Dispatched'
COMPLETED  = 'Completed'
FAILED     = 'Failed'     # ABORT! ABORT! ABORT!


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
# constants for binding mode flags on workload_manager.scheduler_workload() calls
#
EARLY            = 'Early'
LATE             = 'Late'


# ------------------------------------------------------------------------------

