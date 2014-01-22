
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils      as ru
import troy.utils         as tu
from   troy.constants import *
import troy


"""
Represent a pilot, as element of a troy.Overlay.
"""

# ------------------------------------------------------------------------------
#
class Pilot (tu.Properties) :
    """
    """

    _instance_cache = tu.InstanceCache ()

    # --------------------------------------------------------------------------
    #
    def __init__ (self, param, _overlay=None, _instance_type=None) :
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


        tu.Properties.__init__ (self, descr)

        # register properties
        self.register_property ('id')
        self.register_property ('state')
        self.register_property ('description')
        self.register_property ('overlay')

        # inspection properties needed by scheduler
        self.register_property ('size')
        self.register_property ('resource')
        self.register_property ('units')
        self.register_property ('native_id')

        # info from backend
        self.register_property ('native_description')
        self.register_property ('start_time')
        self.register_property ('last_contact')
        self.register_property ('end_queue_time')
        self.register_property ('processes_per_node')
        self.register_property ('slots')
        self.register_property ('working_directory')
        self.register_property ('service_url')


        # info from backend - wishes
        self.register_property ('project')
        self.register_property ('queue')
        self.register_property ('wall_time_limit')
        self.register_property ('affinity_datacenter_label')
        self.register_property ('affinity_machine_label')
         
        # initialize essential properties
        self.id             = pid
        self.state          = DESCRIBED
        self.description    = descr
        self.overlay        = _overlay
        self.resource       = None

        # FIXME: complete attribute list, dig properties from description,
        # perform sanity checks

        self._provisioner   = None
        self._instance      = None
        self._instance_type = None
        self._pilot_info    = None

        self.register_property_updater (self._update_properties)


        if  reconnect :

            self.id,             self.native_id, \
            self._provisioner,   self._instance, \
            self._instance_type, self._state,    \
            self.resource = self._instance_cache.get (instance_id = self.id, 
                                                      native_id   = self.native_id)

            if  not self._instance :
                raise ValueError ("Could not reconnect to unit %s (%s)" % (self.id, self.native_id))

            # refresh pilot information and state from the backend
            self._update_properties ()


        # register in cache for later reconnect
        else :
            self._instance_cache.put (instance_id = self.id, 
                                      native_id   = self.native_id,
                                      instance    = [self.id, 
                                                     self.native_id, 
                                                     self._provisioner,    
                                                     self._instance, 
                                                     self._instance_type, 
                                                     self.state, 
                                                     self.resource])


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

            troy._logger.info ('cancel pilot    %s' % self.id)

            if  self._provisioner :
                self._provisioner.pilot_cancel (self)

            self.state = CANCELED


    # --------------------------------------------------------------------------
    #
    def _bind (self, resource) :

        if  self.state not in [DESCRIBED] :
            raise RuntimeError ("Can only bind pilots in DESCRIBED state (%s)" % self.state)

      # print " ------------ binding pilot: %s" % resource
            
        self.resource = resource
        self.state    = BOUND

        # update cache
        self._instance_cache.put (instance_id = self.id, 
                                  native_id   = self.native_id,
                                  instance    = [self.id, 
                                                 self.native_id, 
                                                 self._provisioner,    
                                                 self._instance, 
                                                 self._instance_type, 
                                                 self.state, 
                                                 self.resource])

    # --------------------------------------------------------------------------
    #
    def _set_instance (self, instance_type, provisioner, instance, native_id) :

        if  self.state not in [BOUND] :
            raise RuntimeError ("Can only provision pilots in BOUND state (%s)" % self.state)

        self._provisioner   = provisioner
        self._instance_type = instance_type
        self._instance      = instance

        self.native_id      = native_id
        self.state          = PROVISIONED

        troy.OverlayManager.pilot_id_to_native_id (self.id, native_id)

        # update cache
        self._instance_cache.put (instance_id = self.id, 
                                  native_id   = self.native_id,
                                  instance    = [self.id, 
                                                 self.native_id, 
                                                 self._provisioner,    
                                                 self._instance, 
                                                 self._instance_type, 
                                                 self.state, 
                                                 self.resource])


    # --------------------------------------------------------------------------
    #
    def _get_instance (self, instance_type) :

        if  instance_type != self._instance_type :
            raise RuntimeError ("pilot instance type is '%s', not '%s'" \
                             % (self._instance_type, instance_type))

        return self._instance


    # --------------------------------------------------------------------------
    #
    def _update_properties (self, key=None) :
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
            self._update_pilot_info ()

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
            return self.get_property (key)

        if  key == 'resource' : return self.resource
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
                self._update_pilot_info ()

                if  key in self._pilot_info :
                    # wohoo!
                    return self._pilot_info[key]


        # we don't have the requested backend info -- fall back to attribs
        return self.get_property (key)


    # --------------------------------------------------------------------------
    #
    def _update_pilot_info (self) :

        # FIXME: this code should actually live within the bigjob plugin, as
        # only it should know about the mapping below

        keymap = {'description'          : 'native_description', 
                  'bigjob_id'            : 'native_id', 
                  'start_time'           : 'start_time',
                  'last_contact'         : 'last_contact',
                  'stopped'              : 'stopped',
                  'end_queue_time'       : 'end_queue_time',
                  'processes_per_node'   : 'processes_per_node',
                  'number_of_processes'  : 'slots',
                  'working_directory'    : 'working_directory',
                  'service_url'          : 'service_url',
                }


        # now that we have fresh info, lets update all pilot properties
        for info_key in self._pilot_info :

            if  info_key in keymap : new_key = keymap[info_key]
            else                   : new_key =        info_key

            # this will trigger registered callbacks
            self.set_property (new_key, self._pilot_info[info_key])


        # also, flatten the description into the pilot properties
        if  'description' in self._pilot_info :

            description = self._pilot_info['description']

            for descr_key in description : 

                if  descr_key in keymap : new_key = keymap[descr_key]
                else                    : new_key =        descr_key

                # this will trigger registered callbacks
                self.set_property (new_key, description[descr_key])


    # --------------------------------------------------------------------------
    #
    def __str__ (self) :

        return str(self.description)


    # --------------------------------------------------------------------------
    #
    def __repr__ (self) :

        return str(self.description)


# ------------------------------------------------------------------------------

