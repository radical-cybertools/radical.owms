
__author__    = "RADICAL Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


from   radical.owms.constants import *
import radical.owms
from   radical.owms import utils  as tu
import radical.utils              as ru


"""
Represent a pilot-based overlay that is managed by radical.owms.
"""

# -----------------------------------------------------------------------------
#
@ru.Lockable  # needed locks for the ru.Registry
class Overlay (tu.Properties, tu.Timed) :
    """
    The `Overlay` class represents a resource overlay which is managed by
    radical.owms,
    i.e. in application and user space.  It contains a set of :class:`Pilots`, 
    which represent the resource capabilities of the overlay.

    Overlay instances are owned by the :class:`OverlayManager` class -- only
    that class should change its composition and state (but Overlay may get
    created by the :class:`radical.owms.Planner`).

    An overlay undergoes a series of transformations before being able to run
    workloads.  Those transformations are orchestrated by the overlay manager.
    To support that orchestration, an overlay will be lockable, and it will have
    a state attribute.  The valid states are listed below.

    Internally, a overlay is represented by a set of :class:`radical.owms.Pilot`
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
    considered out-of-scope for radical.owms at this point, so that state transitions
    are considered irreversible.  
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self, session, descr=None) :
        """
        Create a new overlay instance, based on the given overlay description

        Each new overlay is assigned a new ID.

        Later (service oriented) radical.owms implementations may allow for an
        additional id parameter, to reconnect to the thus identified overlay
        instance.
        """

        if  session : self.session = session
        else:         self.session = radical.owms.Session ()

        if  not descr :
            descr = radical.owms.OverlayDescription ()

        if  isinstance (descr, dict) :
            descr = radical.owms.OverlayDescription (descr)
        
        self.id = ru.generate_id ('ol.')

        tu.Timed.__init__            (self, 'radical.owms.Overlay', self.id)
        self.session.timed_component (self, 'radical.owms.Overlay', self.id)

        tu.Properties.__init__ (self, descr)

        # register properties, initialize state
        self.register_property ('id')
        self.register_property ('state')
        self.register_property ('description')
        self.register_property ('pilots')
        self.register_property ('manager')

        # initialize essential properties
        self.description = descr
        self.pilots      = dict()
        self.state       = None
        self._set_state (DESCRIBED)

        # register this instance, so that overlay can be passed around by id.
        radical.owms.OverlayManager.register_overlay (self)


    # --------------------------------------------------------------------------
    #
    def __del__ (self) :
        """
        Destructor -- cancels the overlay
        """

        self.cancel ()


    # --------------------------------------------------------------------------
    #
    def _set_state (self, new_state) :
        """
        Private method which updates the object state, and logs the event time
        """

        if  self.state != new_state :
            self.state  = new_state
            self.timed_event ('state', new_state)


    # --------------------------------------------------------------------------
    #
    def cancel (self) :
        """
        cancel all pilots
        """

        for pid in self.pilots.keys () :
            pilot = self.pilots[pid]
            pilot.cancel ()

        self._set_state (CANCELED)


    # --------------------------------------------------------------------------
    #
    def _add_pilot (self, p_descr) :
        """
        Add a pilot to the overlay
        """

        if  self.state != DESCRIBED :
            raise RuntimeError ("overlay is not in DESCRIBED state -- cannot add pilots")

        # handle scalar and list uniformly
        # check type, content and uniqueness for each task
        if  not isinstance (p_descr, radical.owms.PilotDescription) :
            raise TypeError ("expected PilotDescription, got %s" % type(p_descr))

        p = radical.owms.Pilot (self.session, p_descr, _overlay=self)

        self.pilots[p.id] = p

        return p.id


# ------------------------------------------------------------------------------

