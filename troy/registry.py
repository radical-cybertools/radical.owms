

import threading
import radical.utils as ru

import troy.workload as twl
import troy.overlay  as tol


# ------------------------------------------------------------------------------
#
class _Registry (object) :
    """
    This registry class is only used internally in Troy -- it serves as
    a central hub for keeping workload and overlay instances around.

    It is in general not a favourable design to have large, all-visible
    registries in a multi-component software stack, as ownership of state
    transitions can easily become blurry, and as a registry can also become
    a performance bottleneck on frequent queries -- so why are we doing this?

    First of all, state transitions in Troy *are* blurry to some extent, as Troy
    aims to support a variety of state diagram transitions, and thus the order
    of transitions is not pre-defined (first derive overlay then schedule CUs,
    or vice versa?).  Also, the ownership of state transitions for a workload is
    not easily scoped (the :class:`Planner` will move a workload from `DESCRIBED` 
    to `PLANNED`, the :class:`WorkloadManager` will move it from `PLANNED` to
    `TRANSLATED`, etc.  And, finally, we want to allow for re-scheduling,
    re-translation, re-planning etc, which would require us to pass control of
    a workload back and forth between different modules.  Finally, this seems to
    be useful for inspection and introspection of Troy activities related to
    specific workload instances.

    In that context, a registry seems the (much) lesser of two devils.

    The registry class will allow to register workload and overlay instances
    (duh), and to acquire/release control over it.  The module which acquires
    control needs to ascertain that the respective workload and overlay
    instances are in a usable state for that module -- the registry is neither
    interpreting nor enforcing any state model on the managed instances.
    Neither will this class perform garbage collection -- active unregistration
    will remove instances from the registry, but not enforce a deletion.

    Workloads and overlays are considered lockable, i.e. we can call
    `entity.lock()` on them to retrieve an rlock.  `acquire` will return
    a locked entity, `release()` will unlock it again.

    This is a singleton class.  We assume that Workload *and* Overlay IDs are
    unique.
    """
    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :
        """
        Create a new Registry instance.  
        """

        # make this instance lockable
        self.lock = threading.RLock ()

        self._registry = dict()
        self._session  = None  # this will be set by Troy.submit_workload()

    # --------------------------------------------------------------------------
    #
    def register (self, entity) :
        """
        register a new workload or overlay.
        """

        if  not isinstance  (entity, twl.Workload) and \
            not isinstance  (entity, tol.Overlay)  :
            raise TypeError ("expected 'Workload' or 'Overlay', not %s"
                          % type(entity))


        # lock manager before checking/manipulating the registry
        with self.lock :

            # lock entity before checking state
            with entity.lock () :

                if  entity.id in self._registry :
                    raise ValueError ("'%s' is already registered" % entity.id)

                if  entity.state != troy.DESCRIBED :
                    raise ValueError ("'%s' not in DESCRIBED state" % entity.id)

                print 'register %s' % entity.id

                self._registry[entity.id] = {}
                self._registry[entity.id]['leased'] = False  # not leased
                self._registry[entity.id]['entity'] = entity


    # --------------------------------------------------------------------------
    #
    def acquire (self, entity_id) :
        """
        temporarily relinquish control over the referenced identity to the
        caller.
        """

        # lock manager before checking/manipulating the registry
        with  self.lock :

            if  not entity_id in self._registry :
              # KeyError ("'%s' is not registered" % entity_id)
                return None 

            if  self._registry[entity_id]['leased'] :
                raise ValueError ("'%s' is currently in use" % entity_id)

            print 'acquire %s' % entity_id

            # acquire entity lock
            self._registry[entity_id]['entity'].lock ().acquire ()
            self._registry[entity_id]['leased'] = True

            # all is well...
            return self._registry[entity_id]['entity']


    # --------------------------------------------------------------------------
    #
    def release (self, entity_id) :
        """
        relinquish the control over the referenced entity
        """

        # lock manager before checking/manipulating the registry
        with  self.lock :

            if  not entity_id in self._registry :
             #  raise KeyError ("'%s' is not registered" % entity_id)
                pass

            if  not self._registry[entity_id]['leased'] :
             #  raise ValueError ("'%s' was not acquired" % entity_id)
                pass

            print 'release %s' % entity_id

            # release entity lock
            self._registry[entity_id]['entity'].lock.release ()
            self._registry[entity_id]['leased'] = False

            # all is well...


    # --------------------------------------------------------------------------
    #
    def unregister (self, entity_id) :
        """
        remove the reference entity from the registry, but do not explicitly
        call the entity's destructor.
        """

        # lock manager before checking/manipulating the registry
        with  self.lock :

            if  not entity_id in self._registry :
                raise KeyError ("'%s' is not registered" % entity_id)

            if  self._registry[entity_id]['leased'] :
                raise ValueError ("'%s' is currently used" % entity_id)

            print 'unregister %s' % entity_id

            # remove entity from registry, w/o a trace...
            del self._registry[entity_id]


# ------------------------------------------------------------------------------
#
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

