

import copy
import threading

import radical.utils   as ru
import saga.attributes as sa

from   troy.constants import *

# ------------------------------------------------------------------------------
#
class Task (sa.Attributes) :
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
    information, which are kept as additional member attributes::

    FIXME: do we need states for tasks?  Like: DESCRIBED, TRANSLATED, BOUND,
    DISPATCHED, DONE?  Sounds useful on a first glance, but on re-bind etc
    (see comments in workload manager), the states quickly become meaningless...
    But related to that will be the workload state inspection from the upper
    layers, and from the overlay manager (which better not plan pilots for
    completed tasks :P).
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, descr) :
        """
        Create a new workload element, aka Task, according to the description..

        Each new task is assigned a new ID.

        Later implementations may allow for an additional id parameter, 
        to reconnect to the thus identified task instance.  
        """

        # initialize state
        tid   = ru.generate_id ('t.')

        if  not 'tag' in descr :
            raise ValueError ("no 'tag' in TaskDescription")

        # set attribute interface properties
        self._attributes_extensible  (False)
        self._attributes_camelcasing (True)

        # register attributes
        self._attributes_register   (ID,                tid,       sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   (STATE,             UNKNOWN,   sa.STRING, sa.SCALAR, sa.WRITEABLE) # FIXME
        self._attributes_register   (TAG,               descr.tag, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   (DESCRIPTION,       descr,     sa.ANY,    sa.SCALAR, sa.READONLY)
        self._attributes_register   ('units',           dict(),    sa.ANY,    sa.VECTOR, sa.WRITEABLE)
         
        # FIXME: complete attribute list, dig attributes from description,
        # perform sanity checks


        self._attributes_set_getter (STATE, self.get_state)

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

                 if any unit  is  FAILED   : task.state = FAILED
            else if any unit  is  CANCELED : task.state = CANCELED
            else if any unit  is  PENDING  : task.state = RUNNING
            else if any unit  is  RUNNING  : task.state = RUNNING
            else if all units are DONE     : task.state = DONE
            else                           : task.state = UNKNOWN

        """

        # atomic states are set elsewhere
        if  self.state in [DESCRIBED, TRANSLATED, BOUND] :
            return self.state

        # final states are never left
        if  self.state in [DONE, FAILED, CANCELED] :
            return self.state
        
        # only DISPATCHED and RUNNING are left -- state depends on unit states
        unit_states = []
        for tid in self.units.keys () :
            unit       = self.units[tid]
            unit_state = unit['dispatcher'].get_unit_state (unit['instance'])
            unit_states.append (unit_state)
          # print 'us: %s' % unit_state

        if FAILED in unit_states :
            self.state = FAILED

        elif CANCELED in unit_states :
            self.state = CANCELED

        elif PENDING in unit_states or \
             RUNNING in unit_states :
            self.state = RUNNING

        else :
            self.state = DONE
            for s in unit_states :
                if s != DONE :
                    self.state = UNKNOWN


        return self.state


    # --------------------------------------------------------------------------
    #
    def __str__ (self) :

        return str(self.description)


    # --------------------------------------------------------------------------
    #
    def _dump (self) :

        self._attributes_dump ()


# ------------------------------------------------------------------------------

