

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
        self._attributes_register   (TAG,               descr.tag, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   (DESCRIPTION,       descr,     sa.ANY,    sa.SCALAR, sa.READONLY)
        self._attributes_register   ('cus',             dict(),    sa.ANY,    sa.VECTOR, sa.WRITEABLE)
         
        # FIXME: complete attribute list, dig attributes from description,
        # perform sanity checks


    # --------------------------------------------------------------------------
    #
    def __str__ (self) :

        return str(self.description)


    # --------------------------------------------------------------------------
    #
    def _dump (self) :

        self._attributes_dump ()


# ------------------------------------------------------------------------------

