


class Attributes (saga.Attributes) :
    """

    Several Troy classes benefit from somewhat richer than default python
    properties -- in particular, we want to get notification callbacks on state
    changes, and want to be able to refresh properties on the fly, i.e. when
    they are needed.

    Notifications:
    --------------

    Assume we want to get a callback involved when a task's state changes::

        def my_cb (task, key, val) :
            print 'state of task %s changed to %s' % (task.id, val)

        task = workload.tasks[3]
        task.add_callback ('state', my_cb)


    For that to work, we need to declare which properties are eligible for
    callbacks::

        class troy.workload (troy.utils.Attributes) :

            self.register_property ('state')
            ...

    From that point on, any plugin, or any thread within troy, can set the
    workload state attribute, and any registered user callback will get invoked.


    Refresh:
    --------

    It is costly for troy to frequently update all possible information from
    remote information sources -- without actually knowing what is needed.  It
    would be more efficient to pull information only when they are actually
    accessed.  For that, we would need again to declare those properties which
    are eligible for on-demand (or rather: on-access) refreshs, and we need to
    declare what method refreshes (i.e. updates) all properties, or a single
    property::

        class troy.workload (troy.utils.Attributes) :

            def __init__ (...) :
                self.register_property ('state')
                self.register_property ('runtime')

                # set a property updater for 'state'
                self.register_property_update ('state', self._update_state)

                # set a property updater for all registered properties
                self.register_property_update (self._update_properties)


            def _update_state (self) :
                # update 'state' property by backend polling
                self.state = self._backend.get_state (self.id)
                

            def _update_properties (self, key) :
                # update other properties by backend polling
                info = self._backend.get_all_info (self.id)
                if  key not in info :
                    print "we have no information about '%s'" % key
                else :
                    self.__setattr__ (key, info[key])


    Note: the `_update_properties` method can be made even more efficient by
    caching the resulting info dict - but that optimization is out of scope for
    this part of the documentation.

    Also note that the the above is very similar to the native Python way to
    provide property getters -- but integrates that mechanism with callback
    management.
    """

    def register_property (self, key) :
        # register atribute w/o type checking
        self._attributes_register (key)

    def update_property (self, key, val) :
        # force updated, also triggers attached callbacks
        self._attributes_i_set (key, val, force=True, flow=self._UP)

    def register_property_update (self, key=None, update=None) :
        # set getters for a key, or for all keys
        if  not key :
            self._attributes_set_global_getter (update)
        else :
            self._attributes_set_getter (key, update)


