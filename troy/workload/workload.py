

import threading
import weakref

import radical.utils        as ru
import saga.attributes      as sa

import task                 as tt
import task_description     as ttd

import relation             as tr
import relation_description as trd

from   troy.constants       import *
import troy


# ------------------------------------------------------------------------------
#
@ru.Lockable
class Workload (sa.Attributes) :
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
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :
        """
        Create a new workload instance.

        Each new workload is assigned a new ID.

        Later (service oriented) Troy implementations may allow for an
        additional id parameter, to reconnect to the thus identified workload
        instances.  
        """
        
        wl_id = ru.generate_id ('wl.')

        # set attribute interface properties
        self._attributes_extensible  (False)
        self._attributes_camelcasing (True)
    
        # register attributes, initialize state
        self._attributes_register   (ID,          wl_id,     sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   (STATE,       DESCRIBED, sa.STRING, sa.SCALAR, sa.WRITEABLE) # FIXME
        self._attributes_register   ('tasks',     dict(),    sa.ANY,    sa.VECTOR, sa.READONLY)
        self._attributes_register   ('relations', list(),    sa.ANY,    sa.VECTOR, sa.READONLY)

        self._attributes_set_getter (STATE, self.get_state)


    # --------------------------------------------------------------------------
    #
    def __del__ (self) :
        """
        Destructor -- cancels the workload
        """

        self.cancel ()


    # --------------------------------------------------------------------------
    #
    def cancel (self) :
        """
        cancel all tasks
        """

        # don't touch final states
        if  self.state in [CANCELED, DONE, FAILED] :
            return

        # non-final -- cancel all tasks
        for tid in self.tasks.keys () :
            task = self.tasks[tid]
            task.cancel ()

        # and update state
        self.state = CANCELED


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
        bulk = False
        if  type(descr) != list :
            bulk  = True
            descr = [descr]

        ret = []

        # check type, content and uniqueness for each task
        for d in descr :

            if  not isinstance (d, ttd.TaskDescription) :
                raise TypeError ("expected TaskDescription, got %s" % type(d))

            # FIXME: add sanity checks for task syntax / semantics
            task = tt.Task (d, _manager=self)

            if task.tag in self.tasks :
                raise ValueError ("Task with tag '%s' already exists" % task.tag)
            
            self.tasks [d.tag] = task
            ret.append (task.id)


        if  bulk :
            return ret
        else :
            return ret[0]


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
        bulk = False
        if  type(descr) != list :
            bulk  = True
            descr = [descr]

        # check type, uniqueness and validity for each relation
        ret = []
        for d in descr :

            if  not isinstance (d, trd.RelationDescription) :
                raise TypeError ("expected RelationDescription, got %s" % type(d))

            if  d in self.relations :
                raise ValueError ("Relation '%s' cannot be added again" % d.name)

            if  not d.head in self.tasks :
                raise ValueError ("relation head '%s' no known" % d.head)

            if  not d.tail in self.tasks :
                raise ValueError ("relation tail '%s' no known" % d.tail)

            r = tr.Relation (d)

            self.relations.append (r)

            ret.append (r.id)


        if  bulk :
            return ret
        else :
            return ret[0]


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
        if  self.state in [DESCRIBED, PLANNED, TRANSLATED, BOUND] :
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
          # print 'ts: %s' % task.state

        if UNKNOWN in task_states :
            self.state = UNKNOWN

        elif FAILED in task_states :
            self.state = FAILED

        elif CANCELED in task_states :
            self.state = CANCELED

        elif DISPATCHED in task_states :
            self.state = DISPATCHED

        else :
            self.state = DONE
            for s in task_states :
                if s != DONE :
                    self.state = UNKNOWN

        troy._logger.debug ('wl   state %-6s: %-10s %s' % (self.id, self.state, str(task_states)))
        return self.state


    # --------------------------------------------------------------------------
    #
    def __str__ (self) :

        import pprint
        return "%-7s : %s" % (self.id, str(pprint.pformat ([self.tasks, self.relations])))


    # --------------------------------------------------------------------------
    #
    def __repr__ (self) :

        return str(self)


    # --------------------------------------------------------------------------
    #
    def _dump (self) :

        self._attributes_dump ()


# ------------------------------------------------------------------------------

