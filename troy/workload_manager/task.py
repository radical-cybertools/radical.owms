

import copy
import threading

import radical.utils   as ru
import saga.attributes as sa


# ------------------------------------------------------------------------------
#
class Task (sa.Attributes) :
    """
    The `Task` class represents a element of work to be performend on behalf of
    an application, and is part of a workload managed by Troy.

    Task instances are created and owned by the :class:`Workload` class they are
    part of -- only that class should change its composition and state.  Tasks
    are created according to a :class:`TaskDescription`, i.e. a set of key-value
    pairs describing the represented workload element.
    """

    _rlock = threading.RLock ()


    # --------------------------------------------------------------------------
    #
    def __init__ (self, description) :
        """
        Create a new workload element, aka Task, according to the description..

        Each new task is assigned a new ID.

        Later implementations may allow for an additional id parameter, 
        to reconnect to the thus identified task instance.  
        """

        with self._rlock :

            # set attribute interface properties
            self._attributes_extensible  (False)
            self._attributes_camelcasing (True)
    
            # initialize state
            tid   = ru.generate_id ('t.')
            descr = copy.deepcopy  (description)

            if  not 'tag' in descr :
                raise ValueError ("no 'tag' in TaskDescription")

            # register attributes
            self._attributes_register   ('id',          tid,       sa.STRING, sa.SCALAR, sa.READONLY)
            self._attributes_register   ('tag',         descr.tag, sa.STRING, sa.SCALAR, sa.READONLY)
            self._attributes_register   ('description', descr,     sa.ANY,    sa.SCALAR, sa.READONLY)

            # FIXME: complete attribute list, dig attributes from description,
            # perform sanity checks


# ------------------------------------------------------------------------------
#
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

