

import radical.utils   as ru
import saga.attributes as sa


# ------------------------------------------------------------------------------
#
class Overlay (sa.Attributes) :
    """
    The `Overlay` class represents a resource overlay which is managed by Troy.
    It contains a set of Pilots, and a set of relationships between those
    pilots.

    Overlay instances are owned by the :class:`OverlayManager` class -- only
    that class should change its composition and state.
    """

    self._rlock = threading.RLock ()


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :
        """
        Create a new overlay instance.

        Each new overlay is assigned a new ID.

        Later implementations may allow for an additional id parameter, to
        reconnect to the thus identified overlay instances.
        """

        with self._rlock :

            # call base constructor
            self._super = super  (Overlay, self)
            self._super.__init__ (self)

            # initialize state
            self._id        = ru.generate_id ('wl.')
            self._pilots    = dict ()
            self._relations = dict ()


            # set attribute interface properties
            self._attributes_extensible  (False)
            self._attributes_camelcasing (True)
    
            # register attributes
            self._attributes_register   ('id',        self._id,        sa.STRING, sa.SCALAR, sa.READONLY)
            self._attributes_register   ('pilots',    self._pilots,    sa.ANY,    sa.VECTOR, sa.READONLY)
            self._attributes_register   ('relations', self._relations, sa.ANY,    sa.VECTOR, sa.READONLY)

            # register getter calls
            self._attributes_set_getter ('id',        self.get_id)
            self._attributes_set_getter ('pilots',    self.get_pilots)
            self._attributes_set_getter ('relations', self.get_relations)


    # --------------------------------------------------------------------------
    #
    def add_pilot (self, pilot) :
        """
        Add a pilot (or a list of pilots) to the overlay.
        
        pilots are expected of type `pilot`, and can only be added
        once.
        """

        with self._rlock :

            # handle scalar and list uniformly
            if  type(pilot) != list :
                pilot = [pilot]

            # check type and uniqueness for each pilot
            for t in pilot :

                if  type(t) != 'Pilot' :
                    raise TypeError ("expected Pilot, got %s" % type(t))

                if t in self._pilots :
                    raise ValueError ("Pilot '%s' cannot be added again" % t.name)

            # all is well
            self._pilots.append (pilot)


    # --------------------------------------------------------------------------
    #
    def add_relation (self, relation) :
        """
        Add a relation for a pair of pilots, or a list relations for a set
        pilot-pairs, to the overlay.  
        
        Relations are expected of type `Relation`, and can only be
        added once.  The related pilots must already be in the
        `Overlay` -- otherwise a `ValueError` is raised.
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

                if  not relation.pilot_1 in self._pilots :
                    raise ValueError ("pilot_1 '%s' no known" % r.pilot_1)

                if  not relation.pilot_2 in self._pilots :
                    raise ValueError ("pilot_2 '%s' no known" % r.pilot_2)

            # all is well
            self._relations.append (relation)


    # --------------------------------------------------------------------------
    #
    def get_id (self) :
        """
        Return a copy of the overlay id, which uniquely (*) identifies 
        this Overlay instance.

        (*) within the scope of one Troy instance.

        """
        return str(self._id) # return a copy to safeguard against changes


    # --------------------------------------------------------------------------
    #
    def get_pilots (self) :
        """
        Return the list of pilots known by this overlay manager.  

        Note that the return list is a reference to the actual list of
        pilots, and thus SHOULD NOT be altered.
        """
        return self._pilots


    # --------------------------------------------------------------------------
    #
    def get_relations (self) :
        """
        Return the list of relations known by this overlay manager.  

        Note that the return list is a reference to the actual list of
        pilots, and thus SHOULD NOT be altered.
        """
        return self._relations


# ------------------------------------------------------------------------------
#
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

