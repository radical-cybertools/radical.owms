
import saga

class Attributes (saga.Attributes) :
    """
    Several Troy classes benefit from somewhat richer than default python
    properties -- in particular, we want to get notification callbacks on state
    changes (and similar), and want to be able to refresh properties on the fly,
    i.e. when they are needed.


    Notifications:
    --------------

    Assume we want to allow users to register callback for a task's state
    change, which is getting invoked whenever the task's `state` property
    changes::

        def my_cb (obj, key, val) :
            print 'state of task %s changed to %s' % (obj.id, val)

        task = workload.tasks[3]
        task.add_callback ('state', my_cb)


    For that to work, Troy needs to declare which properties are eligible for
    those callbacks::

        class troy.workload (troy.utils.Attributes) :

            self.register_property ('state')
            ...

    From that point on, any plugin, or any thread within Troy, can set the
    workload state attribute, and any application callback registered for that
    property will get invoked.  For example, a bigjob dispatcher plugin could
    use::

        tasks[i].state = troy.FAILED

    that would immediately call the application callback (in the same thread
    context).


    Refresh:
    --------

    It is costly for Troy to frequently update all possible information from
    remote information sources -- without actually knowing what is needed.  It
    would be more efficient to pull information only when they are actually
    accessed.  For that, Troy needs again to explicitly register properties
    which are eligible for on-demand (or rather: on-access) updates, and also
    what method updates the property/properties::

        class troy.workload (troy.utils.Attributes) :

            # ------------------------------------------------------------------
            #
            def __init__ (...) :

                # register properties for callback
                self.register_property ('state')
                self.register_property ('runtime')

                # set a property updater for the 'state' property
                self.register_property_updater ('state', self._state_updater)

                # set a property updater for all registered properties
                self.register_property_updater (self._properties_updater)


            # ------------------------------------------------------------------
            #
            def _state_updater (self) :

                # update 'state' property by backend polling
                self.state = self._backend.get_state (self.id)

                # this is equivalent to:
                self.update_property ('state', self._backend.get_state (self.id))
                

            # ------------------------------------------------------------------
            #
            def _properties_updater (self) :

                # update all properties by backend polling
                info = self._backend.get_all_info (self.id)
                for key in info :
                    self.update_property (key, info[key])


    Note: the `_update_properties` method can be made even more efficient by
    caching the resulting info dict - but that optimization is out of scope for
    this part of the documentation.

            # ------------------------------------------------------------------
            #
            def _properties_updater (self) :
                # update all properties by backend polling
                if  (time.now() - self._info_age > self._cache_ttl) :

                    # info cache timed out - -refetch properties
                    info = self._backend.get_all_info (self.id)
                    self._info_age = time.now()
                    for key in info :
                        self.__setattr__ (key, info[key])

    Also note that the the above is very similar to the native Python way to
    provide property getters -- but integrates that mechanism with callback
    management.  For more detailed information, see the implementation and
    documentation of the saga.Attributes interface.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self, inits={}) :

        # set up attribute interface -- allow normal properties (extensible),
        # and initialize from a given dictionary

        saga.Attributes.__init__ (self, inits)
        self._attributes_extensible  (True)
        self._attributes_camelcasing (False)  # don't change property cases on the fly
    

    # --------------------------------------------------------------------------
    #
    def register_property (self, key) :

        # register attribute w/o type checking
        self._attributes_register (key)


    # --------------------------------------------------------------------------
    #
    def update_property (self, key, val) :

        # force attribute updated, also triggers attached callbacks
        self._attributes_i_set (key, val, force=True, flow=self._UP)


    # --------------------------------------------------------------------------
    #
    def register_property_updater (self, key=None, update=None) :

        if  key :
            # set getter for one specific attribute...
            self._attributes_set_getter   (key, update)
        else :
            # ... or for all attributes
            self._attributes_set_global_getter (update)


# ------------------------------------------------------------------------------

