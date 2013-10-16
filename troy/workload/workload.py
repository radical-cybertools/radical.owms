

import threading

import radical.utils    as ru
import saga.attributes  as sa

import task
import task_description

from   troy.constants import *


# ------------------------------------------------------------------------------
#
class Workload (sa.Attributes) :
    """
    The `Workload` class represents a workload which is managed by Troy.  It
    contains a set of :class:`Tasks`, and a set of :class:`Relation`s between
    those tasks.

    Workload instances are owned by the :class:`WorkloadManager` class -- only
    that class should change its composition and state.

    Internally, a workload is represented in two parts: a dictionary of tasks
    (:class:`Task` instances mapped to their task id), and a list of
    :class:`Relation` instances.  As the workload undergoes transformations, it
    is enriched by additional information, although those are kept solely within
    the :class:`Task` instances -- see there for more details.
    
    A workload undergoes a series of transformations before ending up as on
    a specific resource (pilot).  Those transformations are orchestrated by the
    workload manager.  To support that orchestration, a workload will be
    lockable, and it will have a state attribute.  The valid states are listed
    below

    FIXME: those states assume that all transformations are atomic and complete,
    i.e.  we do not expect a partial translation, followed by a partial
    schedule, followed by another partial translations.  Is that assumption
    valid?  
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
        self.lock = threading.RLock ()

        wl_id = ru.generate_id ('wl.')

        # set attribute interface properties
        self._attributes_extensible  (False)
        self._attributes_camelcasing (True)
    
        # register attributes, initialize state
        self._attributes_register   ('id',        wl_id,     sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('state',     DESCRIBED, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('error',     None,      sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('tasks',     dict(),    sa.ANY,    sa.VECTOR, sa.READONLY)
        self._attributes_register   ('relations', list(),    sa.ANY,    sa.VECTOR, sa.READONLY)


    # --------------------------------------------------------------------------
    #
    def add_task (self, description) :
        """
        Add a task (or a list of tasks) to the workload.
        
        Tasks are expected of type `TaskDescription`.
        """

        with self.lock :

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
                if t.tag in self.tasks :
                    raise ValueError ("Task with tag '%s' already exists" % t.tag)
                
                self.tasks [d.tag] = t


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

        with self.lock :

            # handle scalar and list uniformly
            if  type(relation) != list :
                relation = [relation]

            # check type, uniqueness and validity for each relation
            for r in relation :

                if  type(r) != 'Relation' :
                    raise TypeError ("expected Relation, got %s" % type(r))

                if  r in self.relations :
                    raise ValueError ("Relation'%s' cannot be added again" % r.name)

                if  not r.head in self.tasks :
                    raise ValueError ("head '%s' no known" % r.head)

                if  not r.tail in self.tasks :
                    raise ValueError ("tail '%s' no known" % r.tail)

            # all is well
            self.relations.append (relation)


# ------------------------------------------------------------------------------
#
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

