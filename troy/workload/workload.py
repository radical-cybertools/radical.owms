

import threading

import radical.utils    as ru
import saga.attributes  as sa

import task
import task_description


# ------------------------------------------------------------------------------
#
"""
A workload undergoes a series of transformations before ending up as on
a specific resource (pilot).  Those transformations are orchestrated by the
workload manager.  To support that orchestratrion, a workload will be lockable,
and it will have a state attribute.  The valid states are listed below

FIXME: those states assume that all tansformations are atomic and complete, i.e.
we do not expect a partial translation, followed by a partial schedule, followed
byt another partial translations.  Is that assumption valid?
"""
NEW        = 'New'
TRANSLATED = 'Translated'
SCHEDULED  = 'Scheduled'
DISPATCHED = 'Dispatched'


# ------------------------------------------------------------------------------
#
class Workload (sa.Attributes) :
    """
    The `Workload` class represents a workload which is managed by Troy.  It
    contains a set of Tasks, and a set of relationships between those tasks.

    Workload instances are owned by the :class:`WorkloadManager` class -- only
    that class should change its composition and state.
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :
        """
        Create a new workload instance.

        Each new workload is assigned a new ID.

        Later implementations may allow for an additional id parameter, 
        to reconnect to the thus identified workload instances.  
        """

        # make this instance lockable
        self._rlock = threading.RLock ()

        with self._rlock :

            # initialize state
            self._id        = ru.generate_id ('wl.')
            self._state     = NEW
            self._tasks     = dict ()
            self._relations = list ()


            # set attribute interface properties
            self._attributes_extensible  (False)
            self._attributes_camelcasing (True)
    
            # register attributes
            self._attributes_register   ('id',        self._id,        sa.STRING, sa.SCALAR, sa.READONLY)
            self._attributes_register   ('state',     self._state,     sa.STRING, sa.SCALAR, sa.READONLY)
            self._attributes_register   ('tasks',     self._tasks,     sa.ANY,    sa.VECTOR, sa.READONLY)
            self._attributes_register   ('relations', self._relations, sa.ANY,    sa.VECTOR, sa.READONLY)


    # --------------------------------------------------------------------------
    #
    def lock (self) :
        """
        The workload manager can lock a workload so that no more than one
        workload transformation (translation, scheduling, enactment) is
        happening at any point in time::

            # this is a Workload Manager method stub
            def translate (self, workload_id) :
                if  not workload_id in self._workloads :
                    raise LookupError ("no such workload '%s'" % workload_id)
                with 

        """
        return self._rlock


    # --------------------------------------------------------------------------
    #
    def add_task (self, description) :
        """
        Add a task (or a list of tasks) to the workload.
        
        Tasks are expected of type `TaskDescription`.
        """

        with self._rlock :

            # handle scalar and list uniformly
            if  type(description) != list :
                description = [description]

            # check type and uniqueness for each task
            for d in description :

                if  not isinstance (d, task_description.TaskDescription) :
                    raise TypeError ("expected TaskDescription, got %s" % type(d))

                # FIXME: add sanity checks for task syntax / semantics

                t = task.Task (d)

              # t._attributes_dump ()

                # FIXME: clarify what adding multiple tasks with same tags means
                if t.tag in self._tasks :
                    raise ValueError ("Task with tag '%s' already exists" % t.tag)
                
                self._tasks [d.tag] = t


    # --------------------------------------------------------------------------
    #
    def add_relation (self, relation) :
        """
        Add a relation for a pair of tasks, or a list relations for a set
        task-pairs, to the workload.  
        
        Relations are expected of type `Relation`, and can only be
        added once.  The related tasks must already be in the
        `Workload` -- otherwise a `ValueError` is raised.
        """

        # FIXME: need a relation description

        with self._rlock :

            # handle scalar and list uniformly
            if  type(relation) != list :
                relation = [relation]

            # check type, uniqueness and validity for each relation
            for r in relation :

                if  type(r) != 'Relation' :
                    raise TypeError ("expected Relation, got %s" % type(r))

                if  r in self._relations :
                    raise ValueError ("Relation'%s' cannot be added again" % r.name)

                if  not r.head in self._tasks :
                    raise ValueError ("head '%s' no known" % r.head)

                if  not r.tail in self._tasks :
                    raise ValueError ("tail '%s' no known" % r.tail)

            # all is well
            self._relations.append (relation)


# ------------------------------------------------------------------------------
#
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

