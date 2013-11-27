
import saga

class Properties (saga.Attributes) :
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

        class troy.workload (troy.utils.Properties) :

            self.register_property ('state')
            ...

    From that point on, any plugin, or any thread within Troy, can set the
    workload state property, and any application callback registered for that
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

        class troy.workload (troy.utils.Properties) :

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
                self.set_property ('state', self._backend.get_state (self.id))
                

            # ------------------------------------------------------------------
            #
            def _properties_updater (self) :

                # update all properties by backend polling
                info = self._backend.get_all_info (self.id)
                for key in info :
                    self.set_property (key, info[key])


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

    Also note that the above is very similar to the native Python way to
    provide property getters -- but integrates that mechanism with callback
    management.  For more detailed information, see the implementation and
    documentation of the saga.Attributes interface.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self, inits={}) :
        """
        set up the Troy property interface -- allow normal properties (set as
        extensible), and initialize from a given dictionary (`inits`).  If inits
        is of any other type than dict, we attempt to cast it to a dict.
        """
        
        # make sure we have a dict for initialization
        if  not isinstance (inits, dict) :

            # saga.Attributes have an as_dict method
            if  isinstance (inits, saga.Attributes) :
                inits = inits.as_dict ()

            # otherwise we attempt a cast
            else :
                inits = dict (inits)

        saga.Attributes.__init__ (self, inits) # initialize base class
        self._attributes_extensible  (True)    # allow non-registered properties
        self._attributes_camelcasing (False)   # don't change case on the fly
    

    # --------------------------------------------------------------------------
    #
    def register_property (self, key) :
        """
        Any property registered by this call is eligible for callbacks, and is
        also eligible for in-access updates -- if a respective updater was
        registered with `register_property_updater`.
        """

        # register attribute w/o type checking
        self._attributes_register (key, typ    = saga.attributes.ANY, 
                                        flavor = saga.attributes.ANY)


    # --------------------------------------------------------------------------
    #
    def register_property_updater (self, arg1, arg2=None) :
        """
        For a registered property, register a callable which is invoked whenever
        the property's value is accessed.  That callable can be used to update
        the property value for that access, i.e. on the fly.

        There are two invocation modi for this call:

            self.register_property_updater (key, updater)
            self.register_property_updater (     updater)

        In the first case, the updater will only be called on access of the
        property `key`.  In the second case, the updater will be called on *any*
        access to a registered property on the class.

        Note that frequent property accesses can create a significant number of
        updater invocations -- implementers should be aware of this, and should
        consider to cache values in the updater, at least for short periods of
        time.
        """

        if  arg2 :
            # set getter for one specific property...
            self._attributes_set_getter   (arg1, arg2)
        else :
            # ... or for all properties
            self._attributes_set_global_getter (arg1)


    # --------------------------------------------------------------------------
    #
    def set_property (self, key, val) :
        """
        This is equivalent to::

            self.<key> = val

        but will register the property on the fly, making it eligible for
        callbacks etc.
        """

        # set a property w/o invoking updaters
        self._attributes_i_set (key, val, force=True, flow=self._UP)
        


    # --------------------------------------------------------------------------
    #
    def get_property (self, key) :
        """
        This is equivalent to the access via::

            self.<key>

        but will *not* invoke any registered updater methods.  This is thus safe
        to use within an updater.
        """

        # retrieve a property w/o invoking updaters
        return self._attributes_i_get (key, flow=self._UP)


# ------------------------------------------------------------------------------

