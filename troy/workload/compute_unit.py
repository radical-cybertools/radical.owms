

__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.utils   as ru
import saga.attributes as sa

from   troy.constants import *
import troy


"""
Represent a compute unit, as element of a troy.Task in a troy.Workload.
"""

# ------------------------------------------------------------------------------
#
class ComputeUnit (sa.Attributes) :
    """
    The `ComputeUnit` class represents the smallest element of work to be
    performed on behalf of an application, and is part of a workload managed by
    Troy.  More specifically, `Task`s are decomposed into `ComputeUnit`s

    ComputeUnits are created according to a :class:`ComputeUnitDescription`,
    i.e. a set of key-value pairs describing the represented workload element.
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, param=None, _native_id=None, _task=None, _pilot_id=None) :
        """
        Create a new ComputeUnit, according to the description, or reconnect to with an ID

        Each new CU is assigned a new ID.
        """

        if  _native_id :
            # back-translate native if to troy id
            param = str(troy.WorkloadManager.native_id_to_unit_id (_native_id))

        if isinstance (param, basestring) :
            uid       = param
            descr     = troy.ComputeUnitDescription ()
            reconnect = True

        elif isinstance (param, troy.ComputeUnitDescription) :
            uid       = ru.generate_id ('cu.')
            descr     = param
            reconnect = False

        else :
            raise TypeError ("ComputeUnit constructor accepts either a uid (string) or a "
                             "description (troy.ComputeUnitDescription), not '%s'" \
                          % type(param))


        # set attribute interface properties
        self._attributes_extensible  (False)
        self._attributes_camelcasing (True)

        # register attributes
        self._attributes_register   (ID,                  uid,        sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   (STATE,               DESCRIBED,  sa.STRING, sa.SCALAR, sa.WRITEABLE) # FIXME
        self._attributes_register   (DESCRIPTION,         descr,      sa.ANY,    sa.SCALAR, sa.READONLY)
        self._attributes_register   ('pilot_id',          _pilot_id,  sa.STRING, sa.SCALAR, sa.WRITEABLE) # FIXME
        self._attributes_register   ('task',              _task,      sa.ANY,    sa.SCALAR, sa.READONLY)
        self._attributes_register   ('NativeID',          _native_id, sa.STRING, sa.SCALAR, sa.WRITEABLE)  # FIXME

        # info from backend
        self._attributes_register   ('JobID',                   None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('Tag',                     None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('Executable',              None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('Arguments',               None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('Slots',                   None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('StartTime',               None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('AgentStartTime',          None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('EndQueueTime',            None, sa.STRING, sa.SCALAR, sa.READONLY)

        # info from backend - wishes
        self._attributes_register   ('Size',                    None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('Resource',                None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('ProcessesPerNode',        None, sa.INT   , sa.SCALAR, sa.READONLY)
        self._attributes_register   ('WorkingDirectory',        None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('Project',                 None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('Queue',                   None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('WallTimeLimit',           None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('AffinityDatacenterLabel', None, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('AffinityMachineLabel',    None, sa.STRING, sa.SCALAR, sa.READONLY)























         
        # FIXME: complete attribute list, dig attributes from description,
        # perform sanity checks

        self._pilot_id      = None
        self._dispatcher    = None
        self._instance      = None
        self._instance_type = None
        self._unit_info     = None

        self._attributes_set_global_getter (self._get_attribute, flow=self._DOWN)


        if  reconnect :
            # we need to get instance and instance type -- but for that we 
            # need to find the provisioner.  So we cycle through all overlay 
            # provision plugins, and ask them if they know about our ID.

            if  self.task :
                # ha, shortcut found: task should know provisioner
                dispatcher = self.task.manager._dispatcher ()

                try :
                    self._dispatcher    = dispatcher
                    self._instance      = dispatcher.unit_reconnect (_native_id)
                    self._instance_type = dispatcher.name
                except :
                    pass

            # lets check if the above shortcut applied:
            if not self._instance :

                # ok, need to serach provisioner after all...
                plugin_mgr = ru.PluginManager ('troy')
                native_id = troy.WorkloadManager.unit_id_to_native_id (uid)

                # FIXME: error handling
                candidates = plugin_mgr.list ('workload_dispatcher')

                for candidate in candidates :
                    dispatcher = plugin_mgr.load ('workload_dispatcher', candidate)

                    try :
                        self._instance      = dispatcher.unit_reconnect (native_id)
                        self._instance_type = candidate
                        self._dispatcher    = dispatcher
                    except :
                        pass

            if  not self._instance :
                raise ValueError ("Could not reconnect to unit %s" % uid)

            self.native_id = native_id

            # refresh unit information and state from the backend
            self._get_attribute ()


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

        if  self.state not in [DONE, FAILED, CANCELED] :
            troy._logger.warning ('cancel unit %s' % self.id)

            if  self._dispatcher :
                self._dispatcher.unit_cancel (self._instance)

            self.state = CANCELED


    # --------------------------------------------------------------------------
    #
    def _bind (self, pilot_id) :

        if  self.state not in [DESCRIBED] :
            raise RuntimeError ("Can only bind pilots in DESCRIBED state (%s)" % self.state)
            
        self._pilot_id = pilot_id
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


    # --------------------------------------------------------------------------
    #
    def _get_instance (self, instance_type) :

        if  instance_type != self._instance_type :
            raise RuntimeError ("unit instance type is '%s', not '%s'" \
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
            # return the currently set value.  Use UP-flow so that the 
            # attrib interface is not calling getters (duh!).
            return self._attributes_i_get (key, flow='UP')

        if  key == 'resource' : return self._resource
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

        # we don't have the requested backend info -- fall back to attribs
        return self._attributes_i_get (key, flow='UP')


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


        # now that we have fresh info, lets update all unit attributes
        for info_key in self._unit_info :

            if  info_key in keymap : new_key = keymap[info_key]
            else                   : new_key =        info_key

          # print 'KEY: %s - %s' % (info_key, new_key)

            # this will trigger registered callbacks
            self._attributes_i_set (new_key, self._unit_info[info_key],
                                    force=True, flow=self._UP)


    # --------------------------------------------------------------------------
    #
    def __str__ (self) :

        return '%-7s: %s' % (self.id, self.description)


    # --------------------------------------------------------------------------
    #
    def __repr__ (self) :

        return str(self)


    # --------------------------------------------------------------------------
    #
    def _dump (self) :

        self._attributes_dump ()


# ------------------------------------------------------------------------------

