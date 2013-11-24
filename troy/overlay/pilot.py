

__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils   as ru
import saga.attributes as sa

from   troy.constants import *
import troy


"""
Represent a pilot, as element of a troy.Overlay.
"""

# ------------------------------------------------------------------------------
#
class Pilot (sa.Attributes) :
    """
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, param) :
        """
        Create a new pilot according to a description, or reconnect to with an ID.

        Each new pilot is assigned a new ID.
        """

        if isinstance (param, basestring) :
            pid       = param
            descr     = troy.PilotDescription ()
            reconnect = True

        elif isinstance (param, troy.PilotDescription) :
            pid       = ru.generate_id ('p.')
            descr     = param
            reconnect = False

        else :
            raise TypeError ("Pilot constructor accepts either a pid (string) or a "
                             "description (troy.PilotDescription), not '%s'" \
                          % type(param))


        # set attribute interface properties
        self._attributes_extensible  (False)
        self._attributes_camelcasing (True)

        # register attributes
        self._attributes_register     (ID,           pid,               sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register     (STATE,        DESCRIBED,         sa.STRING, sa.SCALAR, sa.WRITEABLE)  # FIXME
        self._attributes_register     (DESCRIPTION,  descr,             sa.ANY,    sa.SCALAR, sa.READONLY)

        # inspection attributes needed by scheduler
        self._attributes_register     ('NativeID',                None, sa.STRING, sa.SCALAR, sa.WRITEABLE)  # FIXME
        self._attributes_register     ('Size',                    None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register     ('Resource',                None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register     ('Units',                   None, sa.STRING, sa.VECTOR, sa.READONLY)

        self._attributes_register     ('ProcessesPerNode',        None, sa.INT   , sa.SCALAR, sa.READONLY)
        self._attributes_register     ('WorkingDirectory',        None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register     ('Project',                 None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register     ('Queue',                   None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register     ('WallTimeLimit',           None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register     ('AffinityDatacenterLabel', None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register     ('AffinityMachineLabel',    None, sa.STRING, sa.SCALAR, sa.READONLY)
         
        # FIXME: complete attribute list, dig attributes from description,
        # perform sanity checks

        self._resource      = None
        self._provisioner   = None
        self._instance      = None
        self._instance_type = None
        self._pilot_info    = None

        self._attributes_set_global_getter (self._get_attribute, flow=self._DOWN)


        if  reconnect :
            # we need to get instance and instance type -- but for that we 
            # need to find the provisioner.  So we cycle through all overlay 
            # provision plugins, and ask them if they know about our ID.
            plugin_mgr = ru.PluginManager ('troy')

            # FIXME: error handling
            candidates = plugin_mgr.list ('overlay_provisioner')

            native_id = troy.OverlayManager.pilot_id_to_native_id (pid)
            for candidate in candidates :
                provisioner = plugin_mgr.load ('overlay_provisioner', candidate)

                try :
                    self._instance      = provisioner.pilot_reconnect (native_id)
                    self._instance_type = candidate
                    self._provisioner   = provisioner
                except :
                    pass

            if  not self._instance :
                raise ValueError ("Could not reconnect to pilot %s" % pid)

            self.native_id = native_id

            # refresh pilot information and state from the backend
            self._get_attribute ()


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

        if  self.state in [PROVISIONED] :
            troy._logger.warning ('cancel pilot %s' % self.id)

            if self._provisioner :
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
    def _set_instance (self, instance_type, provisioner, instance, native_id) :

        if  self.state not in [BOUND] :
            raise RuntimeError ("Can only provision pilots in BOUND state (%s)" % self.state)

        self._provisioner   = provisioner
        self._instance_type = instance_type
        self._instance      = instance

        self.state          = PROVISIONED

        troy.OverlayManager.pilot_id_to_native_id (self.id, native_id)


    # --------------------------------------------------------------------------
    #
    def _get_instance (self, instance_type) :

        if  instance_type != self._instance_type :
            raise RuntimeError ("pilot instance type is '%s', not '%s'" \
                             % (self._instance_type, instance_type))

        return self._instance


    # --------------------------------------------------------------------------
    #
    def _get_attribute (self, key=None) :
        """
        This method is invoked whenever some attribute is asked for, to give us 
        a chance to update the respective attribute value.
        """

        # if key is not given, we simply fetch new information
        if  not key :
            if  not self._provisioner :
                raise RuntimeError ("pilot is in inconsistent state (no provisioner known)")

            # otherwise simply fetch all info(again?)
            # FIXME: need convention about key names / casing
            self._pilot_info = self._provisioner.pilot_get_info (self)
            return

        # else we attempt to dig through the pilot info
        if not key in ['state', 
                       'resource',              
                       'size',       
                       'units',       
                       'processes_per_node',        
                       'working_directory',        
                       'project',                 
                       'queue',                   
                       'wall_time_limit',           
                       'affinity_datacenter_label', 
                       'affinity_machine_label'   ] :

            # this is not a key we know about at this stage -- so simply 
            # return the currently set value.  Use UP-flow so that the 
            # attrib interface is not calling getters (duh!).
            return self._attributes_i_get (key, flow='UP')

        if  key == 'resource' : return self._resource
        if  key == 'instance' : return self._instance

        # check if the info were available via the original description
        if  self.description and \
            key in self.description :
            return self.description[key]


        # else we need to ask the pilot provisioner plugin -- but that is 
        # only available/usable after dispatching
        if  self._provisioner :
            if  self.state not in [COMPLETED, CANCELED, FAILED] :

                # if we already got the requested information, return them
                # FIXME: this assumes that data are updated only once, ever...
                # So, ignore for state!
                if  key not in ['state'] :
                    if  self._pilot_info  and \
                        key in self._pilot_info :
                            return self._pilot_info[key]


                # otherwise simply fetch all info(again?)
                # FIXME: need convention about key names / casing
                self._pilot_info = self._provisioner.pilot_get_info (self)

                if  key in self._pilot_info :
                    # wohoo!
                    return self._pilot_info[key]


        # we don't have the requested backend info -- fall back to attribs
        return self._attributes_i_get (key, flow='UP')


    # --------------------------------------------------------------------------
    #
    def __str__ (self) :

        return str(self.description)


    # --------------------------------------------------------------------------
    #
    def __repr__ (self) :

        return str(self.description)


    # --------------------------------------------------------------------------
    #
    def _dump (self) :

        self._attributes_dump ()


# ------------------------------------------------------------------------------

