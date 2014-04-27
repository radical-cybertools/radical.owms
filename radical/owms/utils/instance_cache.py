
__author__    = "RADICAL Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.owms


# ------------------------------------------------------------------------------
class InstanceCache (object) :
    """
    Proper reconnect to pilots and CUs is out of scope for radical.owms at the moment --
    so radical.owms simply caches instances by their native and their
    radical.owms ID, to be
    able to retrieve them as needed.  That obviously won't survive an
    application restart, 
    """

    # --------------------------------------------------------------------------
    def __init__ (self) :

        self.instance_cache = dict () # to cache the instances
        self.nativeid_cache = dict () # to translate native to instance IDs


    # --------------------------------------------------------------------------
    def put (self, instance, instance_id, native_id) :

        self.instance_cache[str(instance_id)] = instance
        self.nativeid_cache[str(native_id)]   = instance_id


    # --------------------------------------------------------------------------
    def get (self, instance_id=None, native_id=None) :

        if  not instance_id and not native_id :
            return None

        if  not instance_id :
            if  not str(native_id) in self.nativeid_cache :
                return None
            instance_id = self.nativeid_cache[str(native_id)]

        if  not str(instance_id) in self.instance_cache :
            return None

        return self.instance_cache[str(instance_id)]


    # --------------------------------------------------------------------------
    def _dump (self) :

        import pprint
        pprint.pprint (self.instance_cache)


# ------------------------------------------------------------------------------

