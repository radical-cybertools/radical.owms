
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils        as ru
import saga.attributes      as sa

import pilot                as tp

from   troy.constants   import *
import troy

"""
Represent a pilot-based overlay that is managed by TROY.
"""

# -----------------------------------------------------------------------------
#
@ru.Lockable
class Overlay (sa.Attributes) :
    """
    The `Overlay` class represents a resource overlay which is managed by Troy,
    i.e. in application and user space.  It contains a set of :class:`Pilots`, 
    which represent the resource capabilities of the overlay.

    Overlay instances are owned by the :class:`OverlayManager` class -- only
    that class should change its composition and state (but Overlay may get
    created by the :class:`troy.Planner`).

    An overlay undergoes a series of transformations before being able to run
    workloads.  Those transformations are orchestrated by the overlay manager.
    To support that orchestration, an overlay will be lockable, and it will have
    a state attribute.  The valid states are listed below.

    Internally, a overlay is represented by a set of :class:`troy.Pilot`
    instances.  As the overlay undergoes transformations, it is enriched by
    additional information, although those are kept solely within the
    :class:`Pilot` instances -- see there for more details.

    The overlay transformations are:

    * *Scheduling:* A overlay is mapped onto resourced.

    * *Dispatching:* A scheduled overlay is provisioned to the respective
      resources.


    Overlay States
    ---------------

    An overlay can be in different states, depending on the transformations
    performed on it.  Specifically, it can be in `DESCRIBED`,
    `TRANSLATED`, `SCHEDULED`, `PROVISIONED`, `COMPLETED` or `FAILED`.

    A overlay enters the overlay manager in `DESCRIBED` state, and all follow-up
    state transitions are kept within the overlay manager.

    Those states are ill defined in case of partial transformations -- if, for
    example, a scheduling step may only schedule some of the pilots, but not
    others.  As a general rule, a overlay will remain in a state until the
    transformation has been performed on all applicable overlay components
    (pilots).

    Even on fully transformed overlay, the actual overlay state may not be
    trivial to determine -- for example, a specific pilot may have failed, and
    my turn out to be impossible to re-run on its target resource, so it needs
    to be rescheduled to a different resource.  Those feedback loops are
    considered out-of-scope for Troy at this point, so that state transitions
    are considered irreversible.  
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self, descr={}) :
        """
        Create a new overlay instance, based on the given overlay description

        Each new overlay is assigned a new ID.

        Later (service oriented) Troy implementations may allow for an
        additional id parameter, to reconnect to the thus identified overlay
        instance.
        """

        if  isinstance (descr, dict) :
            descr = troy.OverlayDescription (descr)
        
        ol_id = ru.generate_id ('ol.')

        # set attribute interface properties
        self._attributes_extensible  (False)
        self._attributes_camelcasing (True)
    
        # register attributes, initialize state
        self._attributes_register    (ID,          ol_id,     sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register    (STATE,       DESCRIBED, sa.STRING, sa.SCALAR, sa.WRITEABLE) # FIXME
        self._attributes_register    ('error',     None,      sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register    (DESCRIPTION, descr,     sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register    ('pilots',    dict(),    sa.ANY,    sa.ANY,    sa.READONLY)


    # --------------------------------------------------------------------------
    #
    def __del__ (self) :
        """
        Destructor -- cancels the overlay
        """

        self.cancel ()


    # --------------------------------------------------------------------------
    #
    def cancel (self) :
        """
        cancel all pilots
        """

        for pid in self.pilots.keys () :
            pilot = self.pilots[pid]
            pilot.cancel ()


    # --------------------------------------------------------------------------
    #
    def _add_pilot (self, p) :
        """
        Add a pilot to the overlay
        """

        if  self.state != DESCRIBED :
            raise RuntimeError ("overlay is not in DESCRIBED state -- cannot add pilots")

        # handle scalar and list uniformly
        # check type, content and uniqueness for each task
        if  not isinstance (p, tp.Pilot) :
            raise TypeError ("expected Pilot, got %s" % type(p))

        self.pilots[p.id] = p

        return p.id


    # --------------------------------------------------------------------------
    #
    def __str__ (self) :

        return str(self.description)


    # --------------------------------------------------------------------------
    #
    def _dump (self) :

        self._attributes_dump ()

# ------------------------------------------------------------------------------
