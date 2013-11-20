

import copy
import threading

import radical.utils   as ru
import saga.attributes as sa

from   troy.constants import *

# ------------------------------------------------------------------------------
#
class Relation (sa.Attributes) :
    """
    The `Relation` class represents a logical, temporal or spacial dependency
    between two :class:`Task`s, and is part of a workload managed by Troy.

    Relation instances are created and owned by the :class:`Workload` class they
    are part of -- only that class should change its composition and state.
    Relations are created according to a :class:`RelationDescription`, i.e.
    a set of key-value pairs describing the represented task dependency.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self, descr) :
        """
        Create a new workload dependency element, aka Relation, according to 
        the description..

        Each new relation is assigned a new ID.

        Later implementations may allow for an additional id parameter, to
        reconnect to the thus identified relation instance.  
        """

        # set attribute interface properties
        self._attributes_extensible  (False)
        self._attributes_camelcasing (True)
    
        # initialize state
        tid   = ru.generate_id ('r.')

        if  not 'head' in descr :
            raise ValueError ("no 'head' in RelationDescription")
        if  not 'tail' in descr :
            raise ValueError ("no 'tail' in RelationDescription")

        # register attributes
        self._attributes_register   (ID,          tid,        sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   (HEAD,        descr.head, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   (TAIL,        descr.tail, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   (DESCRIPTION, descr,      sa.ANY,    sa.SCALAR, sa.READONLY)

        # FIXME: complete attribute list, dig attributes from description,
        # perform sanity checks


    # --------------------------------------------------------------------------
    #
    def _dump (self) :

        self._attributes_dump ()


# ------------------------------------------------------------------------------

