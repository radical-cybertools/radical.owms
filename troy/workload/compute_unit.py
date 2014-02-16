
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils      as ru
import troy.utils         as tu
from   troy.constants import *
import troy


"""
Represent a compute unit, as element of a troy.Task in a troy.Workload.
"""


# ------------------------------------------------------------------------------
#
class ComputeUnit (tu.Properties, tu.Timed) :
    """
    The `ComputeUnit` class represents the smallest element of work to be
    performed on behalf of an application, and is part of a workload managed by
    Troy.  More specifically, `Task`s are decomposed into `ComputeUnit`s

    ComputeUnits are created according to a :class:`ComputeUnitDescription`,
    i.e. a set of key-value pairs describing the represented workload element.
    """

    _instance_cache = tu.InstanceCache ()

    # --------------------------------------------------------------------------
    #
    def __init__ (self, session, param=None, _native_id=None, _task=None, _pilot_id=None) :
        """
        Create a new ComputeUnit, according to the description, or reconnect to with an ID

        Each new CU is assigned a new ID.
        """

        self.session = session


        if  _native_id :
            native_id  = _native_id
            self.id    = None
            descr      = troy.ComputeUnitDescription ()
            reconnect  = True

        elif isinstance (param, basestring) :
            _native_id = None
            self.id    = param
            descr      = troy.ComputeUnitDescription ()
            reconnect  = True

        elif isinstance (param, troy.ComputeUnitDescription) :
            native_id  = None
            self.id    = ru.generate_id ('cu.')
            descr      = param
            reconnect  = False

        else :
            raise TypeError ("ComputeUnit constructor accepts either an uid (string) or a "
                             "description (troy.ComputeUnitDescription), not '%s'" \
                          % type(param))

        tu.Timed.__init__            (self, 'troy.Unit', self.id)
        self.session.timed_component (self, 'troy.Unit', self.id)

        # set properties which are known from the description
        tu.Properties.__init__ (self, descr)

        # register properties
        self.register_property ('id')
        self.register_property ('state')
        self.register_property ('description')
        self.register_property ('pilot_id')
        self.register_property ('task')
        self.register_property ('native_id')

        # info from backend
        self.register_property ('job_id')
        self.register_property ('tag')
        self.register_property ('executable')
        self.register_property ('arguments')
        self.register_property ('slots')
        self.register_property ('start_time')
        self.register_property ('agent_start_time')
        self.register_property ('end_queue_time')

        # info from backend - wishes
        self.register_property ('size')
        self.register_property ('resource')
        self.register_property ('processes_per_node')
        self.register_property ('working_directory')
        self.register_property ('project')
        self.register_property ('queue')
        self.register_property ('wall_time_limit')
        self.register_property ('affinity_datacenter_label')
        self.register_property ('affinity_machine_label')

        # initialized essential properties
        self.native_id         = native_id
        self.state             = DESCRIBED
        self.description       = descr
        self.pilot_id          = _pilot_id
        self.task              = _task

         
        # FIXME: complete attribute list, dig properties from description,
        # perform sanity checks

        self._dispatcher    = None
        self._instance      = None
        self._instance_type = None
        self._unit_info     = None

        # flag success of stage-in / stage-out
        self.staged_in      = False
        self.staged_out     = False


        self.register_property_updater (self._update_properties)


        # check in cache for reconnect
        if  reconnect :
            # we need to get instance and instance type -- but for that we 
            # need to find the provisioner.  So we cycle through all overlay 
            # provision plugins, and ask them if they know about our ID.

            self.id,             self.native_id, \
            self._dispatcher,    self._instance, \
            self._instance_type, self._state =   \
                    self._instance_cache.get (instance_id = self.id, 
                                              native_id   = self.native_id)

            if  not self._instance :
                raise ValueError ("Could not reconnect to unit %s" % self.id)

            # refresh unit information and state from the backend
            self._update_properties ()


        # register in cache for later reconnect
        else :
            self._instance_cache.put (instance_id = self.id, 
                                      native_id   = self.native_id,
                                      instance    = [self.id, 
                                                     self.native_id, 
                                                     self._dispatcher,    
                                                     self._instance, 
                                                     self._instance_type, 
                                                     self.state])


    # --------------------------------------------------------------------------
    #
    def __del__ (self) :
        """
        Destructor -- cancels the CU
        """

        self.cancel ()


    # --------------------------------------------------------------------------
    #
    def cancel (self) :
        """
        cancel the CU
        """

        if  self.state in [PENDING, RUNNING] :

            troy._logger.info ('cancel unit     %s' % self.id)

            if  self._dispatcher :
                self._dispatcher.unit_cancel (self)

            self.state = CANCELED


    # --------------------------------------------------------------------------
    #
    def _bind (self, pilot_id) :

        if  self.state not in [DESCRIBED] :
            raise RuntimeError ("Can only bind pilots in DESCRIBED state (%s)" % self.state)
            
        self.pilot_id  = pilot_id
        self.state     = BOUND


    # --------------------------------------------------------------------------
    #
    def _set_instance (self, instance_type, dispatcher, instance, native_id) :

        if  self.state not in [BOUND] :
            raise RuntimeError ("Can only dispatch units in BOUND state (%s)" % self.state)

        self._dispatcher    = dispatcher
        self._instance_type = instance_type
        self._instance      = instance
        self.native_id      = native_id

        self.state          = DISPATCHED

        troy.WorkloadManager.unit_id_to_native_id (self.id, native_id)

        # update cache
        self._instance_cache.put (instance_id = self.id, 
                                  native_id   = self.native_id,
                                  instance    = [self.id, 
                                                 self.native_id, 
                                                 self._dispatcher,    
                                                 self._instance, 
                                                 self._instance_type, 
                                                 self.state])


    # ----------------------------------------------------------------------
    #
    def _get_instance (self, instance_type) :

        if  instance_type != self._instance_type :
            raise RuntimeError ("unit instance type is '%s', not '%s'" \
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
            if  not self._dispatcher :
                raise RuntimeError ("unit is in inconsistent state (no dispatcher known)")

            # otherwise simply fetch all info(again?)
            # FIXME: need convention about key names / casing
            self._unit_info = self._dispatcher.unit_get_info (self)
            self._update_unit_info ()
            return

        # else we attempt to dig through the unit info
        if not key in ['state', 
                       'resource',              
                       'size',       
                       'working_directory',        
                       'affinity_datacenter_label', 
                       'affinity_machine_label'   ] :

            # this is not a key we know about at this stage -- so simply 
            # return the currently set value.  Use get_property as to
            # not calling the updater again (duh!).
            return self.get_property (key)


        if  key == 'instance' : return self._instance

        # check if the info were available via the original description
        if  self.description and \
            key in self.description :
            return self.description[key]


        # else we need to ask the unit dispatcher plugin -- but that is 
        # only available/usable after dispatching
        if  self._dispatcher :
            if  self.state not in [COMPLETED, CANCELED, FAILED] :

                # if we already got the requested information, return them
                # FIXME: this assumes that data are updated only once, ever...  
                # So, ignore for state!
                if  key not in ['state'] :
                    if  self._unit_info  and \
                        key in self._unit_info :
                            return self._unit_info[key]


                # otherwise simply fetch all info(again?)
                # FIXME: need convention about key names / casing
                self._unit_info = self._dispatcher.unit_get_info (self)
                self._update_unit_info ()

                if  key in self._unit_info :
                    # wohoo!
                    return self._unit_info[key]

        # we don't have the requested backend info -- fall back to attribs. 
        # Use get_property as to not calling the updater again (duh!).
        return self.get_property (key)


    # --------------------------------------------------------------------------
    #
    def _update_unit_info (self) :

        # FIXME: this code should actually live within the bigjob plugin, as
        # only it should know about the mapping below

        keymap = {'native_id'         : 'native_id'        ,
                  'job-id'            : 'job_id'           ,
                  'tag'               : 'tag'              ,
                  'Executable'        : 'executable'       ,
                  'Arguments'         : 'arguments'        ,
                  'NumberOfProcesses' : 'slots'            ,
                  'start_time'        : 'start_time'       ,
                  'agent_start_time'  : 'agent_start_time' ,
                  'end_queue_time'    : 'end_queue_time'   ,
                }


        # now that we have fresh info, lets update all unit properties
        for info_key in self._unit_info :

            if  info_key in keymap : new_key = keymap[info_key]
            else                   : new_key =        info_key

          # print 'KEY: %s - %s' % (info_key, new_key)

            # this will trigger registered callbacks
            self.set_property (new_key, self._unit_info[info_key])


    # --------------------------------------------------------------------------
    #
    def __str__ (self) :

        return '%-7s: %s' % (self.id, self.description)


    # --------------------------------------------------------------------------
    #
    def __repr__ (self) :

        return str(self)


# ------------------------------------------------------------------------------

