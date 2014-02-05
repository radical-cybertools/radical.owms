

import os
import sinon

import radical.utils as ru
from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_dispatcher', 
    'name'        : 'sinon', 
    'version'     : '0.1',
    'description' : 'this is a dispatcher which submits to sinon pilots.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (troy.PluginBase):

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :
        """
        invoked when plugin is loaded. Only do sanity checks, no other
        initialization
        """

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def init (self):
        """
        invoked by user of plugin, i.e. a overlay manager.  May get invoked
        multiple times -- plugins are singletons, and thus shared amongst all
        overlay managers!
        """

        self._coord = None

        if  'coordination_url' in self.cfg :
            self._coord = self.cfg['coordination_url']

        elif 'COORDINATION_URL' in os.environ :
            self._coord = os.environ['COORDINATION_URL'] 

        else :
            troy._logger.error ("No COORDINATION_URL set for sinon backend")
            troy._logger.info  ("example: export COORDINATION_URL=redis://<pass>@gw68.quarry.iu.teragrid.org:6379")
            troy._logger.info  ("Contact Radica@Ritgers for the redis password")
            raise RuntimeError ("Cannot use sinon backend - no COORDINATION_URL -- see debug log for details")

        self._sinon  = sinon.Session (database_url = self._coord)


    # --------------------------------------------------------------------------
    #
    def dispatch (self, workload, overlay) :
        """
        Dispatch a given workload: examine all tasks in the WL to find the
        defined CUs, and dispatch them to the pilot system.  
        """

        for tid in workload.tasks.keys () :

            task = workload.tasks[tid]

            for uid in task.units.keys () :

                unit = task.units[uid]

                # sanity check for CU state -- only in BOUND state we can 
                # rely on a pilot being assigned to the CU.
                if  unit.state not in [BOUND] :
                    raise RuntimeError ("Can only dispatch units in BOUND state (%s)" % unit.state)


                # get the unit description, and the target pilot ID
                unit_descr = unit.description
                pilot_id   = unit['pilot_id']

                # reconnect to the given pilot -- this is likely to pull the
                # instance from a cache, so should not cost too much.
                pilot      = troy.Pilot (self.session, pilot_id, _instance_type='sinon')
                troy._logger.info ('workload dispatch : dispatch %-18s to %s' \
                                % (uid, pilot._get_instance('sinon')[1]))
                
                # translate our information into bigjob speak, and dispatch
                # a cu for the CU
                sinon_cu_descr = sinon.ComputeUnitDescription ()
                for key in unit_descr :

                    # ignore Troy level keys
                    # FIXME: this should be a positive filter, not a negative
                    # one, to shield against evolving troy...
                    if  key in ['tag', 'inputs', 'outputs', 'stdin', 'stdout'] :
                        continue

                    elif key in ['working_directory'] :
                        sinon_cu_descr['WorkingDirectoryPriv'] = unit_descr[key]

                    else :
                        sinon_cu_descr[key] = unit_descr[key]


                # FIXME: sanity check for pilot type
                [sinon_um, sinon_pm, sinon_pilot] = pilot._get_instance ('sinon')
                sinon_cu = sinon_um.submit_units (sinon_cu_descr)

                # attach the backend instance to the unit, for later state
                # checks etc. We leave it up to the unit to decide if it wants
                # to cache the instance, or just the ID and then later
                # reconnect.
                unit._set_instance ('sinon', self, 
                                    instance  = [sinon_um,     sinon_cu],
                                    native_id = [sinon_um.uid, sinon_cu.uid])


    # --------------------------------------------------------------------------
    #
    def unit_reconnect (self, native_id) :
        """
        the unit lost the instance, and needs to reconnect...
        This is what is getting called on troy.Unit._get_instance, if that
        troy.Unit doesn't have that instance anymore...
        """

        troy._logger.debug ("reconnect to sinon cu %s" % native_id)
        sinon_um_id = native_id[0]
        sinon_cu_id = native_id[1]

        sinon_um    = self._sinon.get_unit_managers (sinon_um_id)
        sinon_cu    = sinon_um.get_units (sinon_cu_id)

        return [sinon_um, sinon_cu]


    # --------------------------------------------------------------------------
    #
    def unit_get_info (self, unit) :
        """
        unit inspection: get all possible information for the unit, and return
        in a dict.  This dict SHOULD contain 'state' at the very least -- but
        check the pilot_inspection unit test for more recommended attributes.
        """

        # find out what we can about the pilot...
        [sinon_um, sinon_cu] = unit._get_instance ('sinon')

        info = {'uid'              : sinon_cu.uid,
                'description'      : sinon_cu.description,
                'state'            : sinon_cu.state,
                'state_details'    : sinon_cu.state_details,
                'execution_details': sinon_cu.execution_details,
                'submission_time'  : sinon_cu.submission_time,
                'start_time'       : sinon_cu.start_time,
                'stop_time'        : sinon_cu.stop_time}


        # translate sinon state to troy state
        if  'state' in info :
            # hahaha python switch statement hahahahaha
            info['state'] =  {sinon.states.PENDING  : PENDING, 
                              sinon.states.RUNNING  : RUNNING, 
                              sinon.states.ACTIVE   : RUNNING, 
                              sinon.states.DONE     : DONE, 
                              sinon.states.CANCELED : CANCELED, 
                              sinon.states.FAILED   : FAILED, 
                              sinon.states.UNKNOWN  : UNKNOWN}.get (info['state'], UNKNOWN)

      # print 'unit_get_info: %s' % info
        # unit_get_info: {'state_details'     : None, 
        #                 'state'             : 'Done', 
        #                 'uid'               : '52f22c8af2291a13649baf23', 
        #                 'submission_time'   : datetime.datetime(2014, 2, 5, 12, 20, 26, 744000), 
        #                 'execution_details' : [u'localhost:3'], 
        #                 'stop_time'         : datetime.datetime(2014, 2, 5, 12, 20, 41, 890000), 
        #                 'start_time'        : datetime.datetime(2014, 2, 5, 12, 20, 40, 884000), 
        #                 'description'       : <sagapilot.compute_unit_description.ComputeUnitDescription object at 0x27ea990>}

        # register sinon events when they have a valid time stamp.  This may
        # register them multiple times though, but duplication is filtered out
        # on time keeping level
        if 'submission_time' in info and info['submission_time'] :
            unit.timed_event ('submission', 'sinon', info['submission_time'])

        if 'start_time' in info and info['start_time'] :
            unit.timed_event ('start', 'sinon', info['start_time'])

        if 'stop_time' in info and info['stop_time'] :
            unit.timed_event ('stop', 'sinon', info['stop_time'])


        return info


    # --------------------------------------------------------------------------
    #
    def unit_cancel (self, unit) :
        """
        bye bye bye Junimond, es ist vorbei, bye bye...
        """

        [sinon_um, sinon_cu] = unit._get_instance ('sinon')
        sinon_cu.cancel ()


# ------------------------------------------------------------------------------

