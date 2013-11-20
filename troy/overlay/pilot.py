

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
        self._provisioner   = None
        self._instance      = None
        self._instance_type = None


    # --------------------------------------------------------------------------
    #
    def __del__ (self) :
        """
        Destructor -- cancels the pilot
        """

        self.cancel ()


    # --------------------------------------------------------------------------
    #
    def cancel (self) :
        """
        cancel the pilot
        """

        if  self.state in [COMPLETED, FAILED, CANCELED] :
            return

        if  self.state not in [PROVISIONED] :
            raise RuntimeError ("Cannot cancel pilot in '%s' state" % self.state)

        self._provisioner.pilot_cancel (self)
        self.state = CANCELED


    # --------------------------------------------------------------------------
    #
    def _bind (self, resource) :

        if  self.state not in [DESCRIBED] :
            raise RuntimeError ("Can only bind pilots in DESCRIBED state (%s)" % self.state)
            
        self._resource = resource
        self.state     = BOUND


    # --------------------------------------------------------------------------
    #
    def _set_instance (self, instance_type, provisioner, instance) :

        if  self.state not in [BOUND] :
            raise RuntimeError ("Can only provision pilots in BOUND state (%s)" % self.state)

        self._provisioner   = provisioner
        self._instance_type = instance_type
        self._instance      = instance

        self.state          = PROVISIONED


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



