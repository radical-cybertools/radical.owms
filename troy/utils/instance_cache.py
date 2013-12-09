
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import troy


# ------------------------------------------------------------------------------
class InstanceCache (object) :
    """
    Proper reconnect to pilots and CUs is out of scope for Troy at the moment --
    so troy simply caches instances by their native and their troy ID, to be
    able to retrieve them as needed.  That obviously won't survive an
    application restart, 
    """

    # --------------------------------------------------------------------------
    def __init__ (self) :

        self.instance_cache = dict () # to cache the instances
        self.nativeid_cache = dict () # to translate native to instance IDs


    # --------------------------------------------------------------------------
    def put (self, instance, instance_id, native_id) :

        self.instance_cache[instance_id] = instance
        self.nativeid_cache[native_id]   = instance_id


    # --------------------------------------------------------------------------
    def get (self, instance_id=None, native_id=None) :

        if  not instance_id and not native_id :
            return None

        if  not instance_id :
            if  not native_id in self.nativeid_cache :
                return None
            instance_id = self.nativeid_cache[native_id]

        if  not instance_id in self.instance_cache :
            return none

        return self.instance_cache[instance_id]


    # --------------------------------------------------------------------------
    def _dump (self) :

        import pprint
        pprint.pprint (self.instance_cache)


# ------------------------------------------------------------------------------

