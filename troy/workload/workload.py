
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import time

import radical.utils      as ru
import troy.utils         as tu
from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
@ru.Lockable  # needed locks for the ru.Registry
class Workload (tu.Properties, tu.Timed) :
    """
    The `Workload` class represents a workload which is managed by Troy.  It
    contains a set of :class:`Tasks`, and a set of :class:`Relation`s between
    those tasks.

    Workload instances are owned by the :class:`WorkloadManager` class -- only
    that class should change its composition and state.

    A workload undergoes a series of transformations before ending up as on
    a specific resource (pilot).  Those transformations are orchestrated by the
    workload manager.  To support that orchestration, a workload will be
    lockable, and it will have a state attribute.  The valid states are listed
    below.

    Internally, a workload is represented in two parts: a dictionary of tasks
    (:class:`Task` instances mapped to their task id), and a list of
    :class:`Relation` instances.  As the workload undergoes transformations, it
    is enriched by additional information, although those are kept solely within
    the :class:`Task` instances -- see there for more details.

    The workload transformations are:

    * *Planning:* A workload is inspected and its cardinal parameters are
      expanded, based on the overlay if it exists.

    * *Translation:* A workload is inspected, and its tasks are translated into 
      compute units.  A single task may result in one or more compute units.
      Multiple tasks may be combined into one compute unit.

    * *Scheduling:* A translated workload is mapped onto an resource overlay.
      More specifically, the compute units of an translated workload are
      scheduled on the compute pilots of a given overlay.  

    * *Dispatching:* A scheduled workload is dispatched to the active entities
      (pilots) of an overlay.


    Workload States
    ---------------

    A workload can be in different states, depending on the transformations
    performed on it.  Specifically, it can be in `DESCRIBED`, `PLANNED`,
    `TRANSLATED`, `SCHEDULED`, `DISPATCHED`, `DONE` or `FAILED`.
    A workload enters the workload manager in `DESCRIBED` or `PLANNED` state,
    and all follow-up state transitions are kept within the workload manager.

    Those states are ill defined in case of partial transformations -- if, for
    example, a translation step only derives compute units for some of the
    tasks, but not for others.  As a general rule, a workload will remain in
    a state until the transformation has been performed on all applicable
    workload components (tasks and relations).

    Even on fully transformed workloads, the actual workload state may not be
    trivial to determine -- for example, a specific compute unit configuration
    derived in a translation step may show to be impossible to dispatch later
    on, and may require a re-translation into a different configuration; or if
    a newly `DESCRIBED` task is added to a `SCHEDULED` workload.   Those
    feedback loops are considered out-of-scope for Troy at this point, so that
    state transitions are considered irreversible.  

    Workload Partitions
    -------------------

    A Troy Planner (or in fact any other algorithm in Troy) can partition
    a workload.  Workload Partitions are sub-workloads which have to run
    sequentially -- i.e. partition[0] has to be completed before partition[1]
    can start.  Task dependencies provide boundaries to the possible
    partitioning schemes, but partitions can also be defined in the absence of
    task dependencies, for example to ensure efficient usage of certain overlay
    structures.

    A troy workload maintains a set of partitions, and any algorithm, in
    particular the troy.strategy and the workload.dispatcher plugins, may or may
    not honor the defined partitions -- the plugin documentation should document
    if partitions are honored or not.

    Partitions are provided as `workload.partitions`, which is a list of
    partition IDs, which can be translated to `troy.Workload` instances via
    `troy.WorkloadManager.get_workload (workload.partitions[0])` etc.  That list
    will contain at least one partition, the original workload itself --
    algorithms can thus transparently operate over partitioned and unpartitioned
    workloads.  It is guaranteed that the union of all partitions is equivalent
    to the complete original workload, i.e. that it contains all tasks of the
    workload.  The partitions and the original workload share their tasks, i.e.
    when a task is run and enters `DONE` state in a partition, it is also in
    `DONE` state in the original workload, and vice versa.  Partition states
    follow the rules for workload states above.  The overall workload state is
    not affected by the partitioning of the workload.

    Note that partitions may create garbage collection cycles -- this will be
    changed in future versions of Troy.
    """

    # FIXME: if the original workload gets, for example, BOUND, then all
    # partitions should be marked as BOUND.


    # --------------------------------------------------------------------------
    #
    def __init__ (self, session, task_descriptions=None, relation_descriptions=None) :
        """
        Create a new workload instance.

        Each new workload is assigned a new ID.

        Later (service oriented) Troy implementations may allow for an
        additional id parameter, to reconnect to the thus identified workload
        instances.  
        """

        self.session = session

        self.id = ru.generate_id ('wl.')

        tu.Timed.__init__            (self, 'troy.Workload', self.id)
        self.session.timed_component (self, 'troy.Workload', self.id)

        tu.Properties.__init__ (self)


        # register properties, initialize state
        self.register_property ('id')
        self.register_property ('state')
        self.register_property ('tasks')
        self.register_property ('relations')
        self.register_property ('partitions')
        self.register_property ('manager')

        # initialize essential properties
        self.state = UNKNOWN
        self._set_state (DESCRIBED)

        self.tasks      = dict()
        self.relations  = list()
        self.partitions = list()


        # initialize partitions
        self.partitions = [self.id]

        self.register_property_updater ('state', self.get_state)

        # initialize private properties
        self.parametrized = False

        # register this instance, so that workload can be passed around by id.
        troy.WorkloadManager.register_workload (self)

        # fill the workload with given task and relation descriptions
        if  task_descriptions :
            self.add_task (task_descriptions)

        if  relation_descriptions :
            self.add_relation (relation_descriptions)

        


    # --------------------------------------------------------------------------
    #
    def __del__ (self) :
        """
        Destructor -- cancels the workload
        """

        # AM: is this really wanted?  Will break on long-running workloads.
        # OTOH, of course, we have no means to reconnect...

        self.cancel ()


    # --------------------------------------------------------------------------
    #
    def cancel (self) :
        """
        cancel all tasks
        """

        # don't touch final states
        if  self.state in [DISPATCHED] :

            troy._logger.info ('cancel workload %s' % self.id)

            # non-final -- cancel all tasks
            for tid in self.tasks.keys () :
                task = self.tasks[tid]
                task.cancel ()

            # and update state
            self._set_state (CANCELED)


    # --------------------------------------------------------------------------
    #
    def add_task (self, descr) :
        """
        Add a task (or a list of tasks) to the workload.
        
        Tasks are expected of type `TaskDescription`.
        """

        if  self.state != DESCRIBED :
            raise RuntimeError ("workload is not in DESCRIBED state (%s) -- cannot add tasks" % self.state) 

        # handle scalar and list uniformly
        bulk = True
        if  not isinstance (descr, list) :
            bulk  = False
            descr = [descr]

        ret = []

        # check type, content and uniqueness for each task
        for d in descr :

            if  isinstance (d, dict) :
                d = troy.TaskDescription (d)

            if  not isinstance (d, troy.TaskDescription) :
                raise TypeError ("expected TaskDescription, got %s" % type(d))


            # now that we have a task description, we want to expand it with the
            # session information
            d.expand_description (self.session)


            # FIXME: add sanity checks for task syntax / semantics
            task = troy.Task (self.session, descr=d, _workload=self)
        
            self.timed_component (task, 'troy.Task', task.id)

            self.tasks [task.id] = task
            ret.append (task.id)


        if  bulk : return ret
        else     : return ret[0]


    # --------------------------------------------------------------------------
    #
    def add_relation (self, descr) :
        """
        Add a relation for a pair of tasks, or a list relations for a set
        task-pairs, to the workload.  
        
        Relations are expected of type `Relation`, and can only be
        added once.  The related tasks must already be in the
        `Workload` -- otherwise a `ValueError` is raised.
        """

        if  self.state != DESCRIBED :
            raise RuntimeError ("workload is not in DESCRIBED state -- cannot add relation")

        # handle scalar and list uniformly
        bulk = True
        if  not isinstance (descr, list) :
            bulk  = False
            descr = [descr]

        # check type, uniqueness and validity for each relation
        ret = []

        for d in descr :

            if  not isinstance (d, troy.RelationDescription) :
                raise TypeError ("expected RelationDescription, got %s" % type(d))

            if  d in self.relations :
                raise ValueError ("Relation '%s' cannot be added again" % d.name)

            if  not d.head in self.tasks :
                raise ValueError ("relation head '%s' no known" % d.head)

            if  not d.tail in self.tasks :
                raise ValueError ("relation tail '%s' no known" % d.tail)

            r = troy.Relation (d)

            self.relations.append (r)

            ret.append (r.id)

        if  bulk : return ret
        else     : return ret[0]


    # --------------------------------------------------------------------------
    #
    def _set_state (self, new_state) :
        """
        Private method which updates the workload state, and logs the event time
        """

        if  self.state != new_state :
            self.state  = new_state
            self.timed_event ('state', [new_state])


    # --------------------------------------------------------------------------
    #
    def get_state (self) :
        """
        The workload state is a wonderous thing -- it is sometimes atomic, and
        sometimes it isn't...  It is derived as follows:

        The initial stages of Troy cause atomic state transitions for the
        workload -- it is created as `DESCRIBED`, 
        `planner.plan()`                        moves it to `PLANNED`, 
        `workload_manager.translate_workload()` moves it to `TRANSLATED`,
        `workload_manager.bind_workload()`      moves it to `BOUND`,       and
        `workload_manager.dispatch_workload()`  moves it to `DISPATCHED`.

        Up to then, all state transitions are under full control of Troy, so we
        can make sure that the global workload state makes sense -- if any of
        the transitions cannot be performed for a task, we can raise an
        exception and not advance the state, or revert everything and move into
        FAILED state.

        After dispatch, however, the tasks (and more precisely the units which
        make up the tasks) have a state which is managed by some backend, and
        have individual and uncorrelated state transitions.  At that point, we
        make the workload state dependent on the tasks states, and define::

                 if any task  is  FAILED     :  workload.state = FAILED
            else if any task  is  CANCELED   :  workload.state = CANCELED
            else if any task  is  DISPATCHED :  workload.state = DISPATCHED
            else if all tasks are DONE       :  workload.state = DONE
            else                             :  workload.state = UNKNOWN

        """

        # atomic states are set elsewhere
        if  self.state in [DESCRIBED, PLANNED] :
            return self.state

        # final states are never left
        if  self.state in [DONE, FAILED, CANCELED] :
            return self.state
        
        # if there are no tasks, then there was no further state transition
        if  not len(self.tasks) :
            return self.state
        
        # state depends on task states
        task_states = []
        for tid in self.tasks.keys () :
            task = self.tasks[tid]
            task_states.append (task.state)

        if UNKNOWN in task_states :
            self._set_state (UNKNOWN)

        elif FAILED in task_states :
            self._set_state (FAILED)

        elif CANCELED in task_states :
            self._set_state (CANCELED)

        elif DESCRIBED in task_states :
            self._set_state (TRANSLATED)

        elif TRANSLATED in task_states :
            self._set_state (TRANSLATED)

        elif BOUND in task_states :
            self._set_state (BOUND)

        elif DISPATCHED in task_states :
            self._set_state (DISPATCHED)

        else :
            self._set_state (DONE)
            for s in task_states :
                if s != DONE :
                    self._set_state (UNKNOWN)

        troy._logger.debug ('wl   state %-6s: %-10s %s' % (self.id, self.state, str(task_states)))
        return self.state


    # --------------------------------------------------------------------------
    #
    def wait (self) :

        while self.state not in [troy.DONE, troy.FAILED, troy.CANCELED]:
            troy._logger.info ("waiting for workload (state: %s)" % self.state)
            time.sleep(1)


# ------------------------------------------------------------------------------

