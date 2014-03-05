
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils      as ru
import troy.utils         as tu
from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
class Task (tu.Properties, tu.Timed) :
    """
    The `Task` class represents a element of work to be performed on behalf of
    an application, and is part of a workload managed by Troy.

    Task instances are created and owned by the :class:`Workload` class they are
    part of -- only that class should change its composition and state.  Tasks
    are created according to a :class:`TaskDescription`, i.e. a set of key-value
    pairs describing the represented workload element.

    As tasks are components of a :class:`Workload`, they are subject to the
    transformations the workload undergoes (see :class:`Workload` documentation
    for details).  During that process, tasks are enriched with additional
    information, which are kept as additional member properties::

    FIXME: do we need states for tasks?  Like: DESCRIBED, TRANSLATED, BOUND,
    DISPATCHED, DONE?  Sounds useful on a first glance, but on re-bind etc
    (see comments in workload manager), the states quickly become meaningless...
    But related to that will be the workload state inspection from the upper
    layers, and from the overlay manager (which better not plan pilots for
    completed tasks :P).
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, session, descr, _workload=None) :
        """
        Create a new workload element, aka Task, according to the description..

        Each new task is assigned a new ID.

        Later implementations may allow for an additional id parameter, 
        to reconnect to the thus identified task instance.  
        """


        self.session  = session

        tu.Properties.__init__ (self, descr)

        # register properties
        self.register_property ('id')
        self.register_property ('state')
        self.register_property ('tag')
        self.register_property ('cardinality')
        self.register_property ('units')
        self.register_property ('workload')
        self.register_property ('description')


        # initialize essential properties
        self.state       = DESCRIBED
        self.tag         = descr.get ('tag', None)
        self.units       = dict()
        self.workload    = _workload
        self.description = descr

        # FIXME: complete attribute list, dig properties from description,
        # perform sanity checks

        # initialize state
        self.id   = ru.generate_id ('t.')

        tu.Timed.__init__            (self, 'troy.Task', self.id)
        self.session.timed_component (self, 'troy.Task', self.id)

        if  self.workload :
            self.workload.timed_component (self, 'troy.Task', self.id)


        self.register_property_updater ('state', self.get_state)


    # --------------------------------------------------------------------------
    #
    def __del__ (self) :
        """
        Destructor -- cancels the task
        """

        self.cancel ()


    # --------------------------------------------------------------------------
    #
    def cancel (self) :
        """
        cancel all units
        """

        if  self.state in [DISPATCHED] :

            troy._logger.info ('cancel task     %s' % self.id)

            for uid in self.units.keys () :

                unit = self.units[uid]
                unit.cancel ()
                self.state = CANCELED


    # --------------------------------------------------------------------------
    #
    def _add_unit (self, cu_descr) :
        """
        Add a unit to the task
        """

        if  self.state != DESCRIBED :
            raise RuntimeError ("task is not in DESCRIBED state -- cannot add units (%s)" % self.state)

        # handle scalar and list uniformly
        # check type, content and uniqueness for each task
        if  not isinstance (cu_descr, troy.ComputeUnitDescription) :
            raise TypeError ("expected ComputeUnitDescription, got %s" % type(cu_descr))

        unit = troy.ComputeUnit (self.session, cu_descr, _task=self)

        self.units[unit.id] = unit
        self.timed_component (unit, 'troy.Unit', unit.id)

        return unit.id


    # --------------------------------------------------------------------------
    #
    def get_walltime (self) :
        """
        This method will return a walltime estimate for the task.  If walltime
        was given for the task description, we use it.  If it was not, or is
        zero, then we sum up the max walltime of all CUs currently defined (i.e.
        we assume CUs in one task to always (be able to) run concurrently.
        """

        if  'walltime' in self.description and \
            self.description['walltime'] :

            return self.description['walltime']

        else :
            walltime = 0.0
            for unit in self.units :
                print unit
                walltime = max (walltime, unit.walltime)

            return walltime


    # --------------------------------------------------------------------------
    #
    def get_state (self) :
        """
        The task state is a wonderous thing -- it is sometimes atomic, and
        sometimes it isn't...  It is derived as follows:

        The initial stages of Troy cause atomic state transitions for the
        tasks -- they are created as `DESCRIBED`, 
        `workload_manager.translate_workload()` moves them to `TRANSLATED`,
        `workload_manager.bind_workload()`      moves them to `BOUND`,       and
        `workload_manager.dispatch_workload()`  moves them to `DISPATCHED`.

        Up to then, all state transitions are under full control of Troy, so we
        can make sure that the task states make sense -- if any of
        the transitions cannot be performed for a task, we can raise an
        exception and not advance the state, or revert everything and move into
        FAILED state.

        After dispatch, however, the units which make up the tasks have states
        which are managed by some backend, and have individual and uncorrelated
        state transitions.  At that point, we make the task state dependent on the
        tasks states, and define::

                 if any unit  is  FAILED     : task.state = FAILED
            else if any unit  is  CANCELED   : task.state = CANCELED
            else if any unit  is  DISPATCHED : task.state = DISPATCHED
            else if any unit  is  DISPATCHED : task.state = RUNNING
            else if any unit  is  RUNNING    : task.state = RUNNING
            else if all units are DONE       : task.state = DONE
            else                             : task.state = UNKNOWN

        """

        # final states are never left
        if  self.state in [DONE, FAILED, CANCELED] :
            return self.state

        # if there are no units, then there was no further state transition
        if  not len(self.units) :
            return self.state
        
        # only DISPATCHED and RUNNING are left -- state depends on unit states
        unit_states = []
        for tid in self.units.keys () :
            unit       = self.units[tid]
            unit_states.append (unit.state)

        if  UNKNOWN in unit_states :
            self.state = UNKNOWN

        elif FAILED in unit_states :
            self.state = FAILED

        elif CANCELED in unit_states :
            self.state = CANCELED

        elif DESCRIBED in unit_states :
            self.state = TRANSLATED

        elif BOUND in unit_states :
            self.state = BOUND

        elif DISPATCHED in unit_states or \
             PENDING    in unit_states or \
             RUNNING    in unit_states :
            self.state = DISPATCHED

        else :
            self.state = DONE
            for s in unit_states :
                if s != DONE :
                    self.state = UNKNOWN

        troy._logger.debug ('task state %-6s : %-10s %s' % (self.id, self.state, str(unit_states)))

        return self.state



# ------------------------------------------------------------------------------

