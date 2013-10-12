

import radical.utils   as ru
import saga.attributes as sa


# ------------------------------------------------------------------------------
#
class Workload (sa.Attributes) :
    """
    The `Workload` class represents a workload which is managed by Troy.  It
    contains a set of Tasks, and a set of relationships between those tasks.

    Workload instances are owned by the :class:`WorkloadManager` class -- only
    that class should change its composition and state.
    """

    self._rlock = threading.RLock ()


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :
        """
        Create a new workload instance.

        Each new workload is assigned a new ID.

        Later implementations may allow for an additional id parameter, 
        to reconnect to the thus identified workload instances.  
        """

        with self._rlock :

            # call base constructor
            self._super = super  (Workload, self)
            self._super.__init__ (self)

            # initialize state
            self._id        = ru.generate_id ('wl.')
            self._tasks     = dict ()
            self._relations = dict ()


            # set attribute interface properties
            self._attributes_extensible  (False)
            self._attributes_camelcasing (True)
    
            # register attributes
            self._attributes_register   ('id',        self._id,        sa.STRING, sa.SCALAR, sa.READONLY)
            self._attributes_register   ('tasks',     self._tasks,     sa.ANY,    sa.VECTOR, sa.READONLY)
            self._attributes_register   ('relations', self._relations, sa.ANY,    sa.VECTOR, sa.READONLY)

            # register getter calls
            self._attributes_set_getter ('id',        self.get_id)
            self._attributes_set_getter ('tasks',     self.get_tasks)
            self._attributes_set_getter ('relations', self.get_relations)


    # --------------------------------------------------------------------------
    #
    def add_task (self, task) :
        """
        Add a task (or a list of tasks) to the workload.
        
        Tasks are expected of type `Task`, and can only be added
        once.
        """

        with self._rlock :

            # handle scalar and list uniformly
            if  type(task) != list :
                task = [task]

            # check type and uniqueness for each task
            for t in task :

                if  type(t) != 'Task' :
                    raise TypeError ("expected Task, got %s" % type(t))

                if t in self._tasks :
                    raise ValueError ("Task '%s' cannot be added again" % t.name)

            # all is well
            self._tasks.append (task)


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

                if  not relation.task_1 in self._tasks :
                    raise ValueError ("task_1 '%s' no known" % r.task_1)

                if  not relation.task_2 in self._tasks :
                    raise ValueError ("task_2 '%s' no known" % r.task_2)

            # all is well
            self._relations.append (relation)


    # --------------------------------------------------------------------------
    #
    def get_id (self) :
        """
        Return a copy of the workload id, which uniquely (*) identifies 
        this Workload instance.

        (*) within the scope of one Troy instance.

        """
        return str(self._id) # return a copy to safeguard against changes


    # --------------------------------------------------------------------------
    #
    def get_tasks (self) :
        """
        Return the list of tasks known by this workload manager.  

        Note that the return list is a reference to the actual list of
        tasks, and thus SHOULD NOT be altered.
        """
        return self._tasks


    # --------------------------------------------------------------------------
    #
    def get_relations (self) :
        """
        Return the list of relations known by this workload manager.  

        Note that the return list is a reference to the actual list of
        tasks, and thus SHOULD NOT be altered.
        """
        return self._relations


# ------------------------------------------------------------------------------
#
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

