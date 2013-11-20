

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

        # inspection attributes needed by scheduler
        self._attributes_register   ('ServiceURL',              None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('NumberOfProcesses',       None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('ProcessesPerNode',        None, sa.INT   , sa.SCALAR, sa.READONLY)
        self._attributes_register   ('WorkingDirectory',        None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('Project',                 None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('Queue',                   None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('WallTimeLimit',           None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('AffinityDatacenterLabel', None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('AffinityMachineLabel',    None, sa.STRING, sa.SCALAR, sa.READONLY)
         
        # FIXME: complete attribute list, dig attributes from description,
        # perform sanity checks

        self._resource      = None
        self._provisioner   = None
        self._instance      = None
        self._instance_type = None
        self._pilot_info    = None

        self._attributes_set_global_getter (self.get_attribute)


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
    def _get_attribute (self, key) :
        """
        This method is invoked whenever some attribute is asked for, to give us 
        a chance to update the respective attribute value.
        """
        print "getting attribute %s" % key

        # check if the info were available via the original description
        if  key in self.description :
            return self.description[key]


        # else we need to ask the pilot provisioner plugin -- but that is 
        # only available/usable after dispatching
        if  self.state in [PROVISIONED, COMPLETED, CANCELED, FAILED] :

            if  not self._provisioner :
                raise RuntimeError ("pilot is in inconsistent state (no provisioner known)")

            # if we already got the requested information, return them
            # FIXME: this assumes that data are updated only once, ever...
            if  self._pilot_info  and \
                key in self._pilot_info :
                    return self._pilot_info[key]


            # otherwise simply fetch all info(again?)
            # FIXME: need convention about key names / casing
            self._pilot_info = self._provisioner.get_pilot_info ()

            if  key in self._pilot_info :
                # wohoo!
                return self._pilot_info[key]

            # this is not a key we know about at this stage -- so simply 
            # return the currently set value.  Use UP-flow so that the 
            # attrib interface is not calling getters (duh!).
            return self._attributes_i_get (key, flow='UP')



    # --------------------------------------------------------------------------
    #
    def __str__ (self) :

        return str(self.description)


    # --------------------------------------------------------------------------
    #
    def _dump (self) :

        self._attributes_dump ()



