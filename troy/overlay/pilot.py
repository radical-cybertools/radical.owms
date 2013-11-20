

__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils   as ru
import saga.attributes as sa

from troy.constants import *


"""
Represent a pilot, as element of a troy.Overlay.
"""

# -----------------------------------------------------------------------------
#
class Pilot (sa.Attributes) :
    """
    """

    def __init__ (self, descr) :
        """
        Create a new pilot

        Each new pilot is assigned a new ID.

        Later implementations may allow for an additional id parameter, 
        to reconnect to the thus identified pilot instance.  
        """

        # initialize state
        pid = ru.generate_id ('p.')

        # set attribute interface properties
        self._attributes_extensible  (False)
        self._attributes_camelcasing (True)

        # register attributes
        self._attributes_register   (ID,           pid,             sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   (STATE,        DESCRIBED,       sa.STRING, sa.SCALAR, sa.WRITEABLE)  # FIXME
        self._attributes_register   (DESCRIPTION,  descr,           sa.ANY,    sa.SCALAR, sa.READONLY)
         
        # FIXME: complete attribute list, dig attributes from description,
        # perform sanity checks

        self._resource      = None
        self._instance      = None
        self._instance_type = None


    # --------------------------------------------------------------------------
    #
    def _bind (self, resource) :

        self._resource = resource


    # --------------------------------------------------------------------------
    #
    def _set_instance (self, instance_type, instance) :

        if  self._instance_type :
            raise RuntimeError ("cannot set instance for pilot (is %s)" % self.instance_type)

        self._instance_type = instance_type
        self._instance      = instance


    # --------------------------------------------------------------------------
    #
    def _get_instance (self, instance_type) :

        if  instance_type != self._instance_type :
            raise RuntimeError ("pilot instance type is '%s', not '%s'" \
                             % (self._instance_type, instance_type))

        return self._instance


    # --------------------------------------------------------------------------
    #
    def __str__ (self) :

        return str(self.description)


    # --------------------------------------------------------------------------
    #
    def _dump (self) :

        self._attributes_dump ()



