

import os
import saga
import getpass

import pilot         as pilot_module
import radical.utils as ru

from   radical.owms.constants import *
import radical.owms


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'overlay_provisioner', 
    'name'        : 'bigjob', 
    'version'     : '0.1',
    'description' : 'this is a scheduler which provisions bigjob pilots.'
  }

# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (radical.owms.PluginBase):
    """
    This plugin creates pilots via the BigJob Pilot API.

    **Configuration Options:**

    * `coordination_url`: the redis URL to be used by BigJob.  The environment
        variable COORDINATION_URL is used as fallback.
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        radical.owms.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)


    # --------------------------------------------------------------------------
    #
    def init (self):

        self._coord = None

        if  'coordination_url' in self.cfg :
            self._coord = self.cfg['coordination_url']

        elif 'COORDINATION_URL' in os.environ :
            self._coord = os.environ['COORDINATION_URL'] 

        else :
            radical.owms._logger.error ("No COORDINATION_URL set for bigjob backend")
            radical.owms._logger.info  ("example: export COORDINATION_URL=redis://<pass>@gw68.quarry.iu.teragrid.org:6379")
            radical.owms._logger.info  ("Contact Radica@Ritgers for the redis password")
            raise RuntimeError ("Cannot use bigjob backend - no COORDINATION_URL -- see debug log for details")

        radical.owms._logger.debug ('using bj coordination url %s' % self._coord)
        self.cp_service = pilot_module.PilotComputeService (self._coord)


    # --------------------------------------------------------------------------
    #
    def provision (self, overlay) :
        """
        provision the pilots of the overlay -- inspect that overlay, dig out the pilots
        and their description, check state, and instantiate them via the backend
        system.
        """

        # we simply assign all pilots to localhost
        for pid in overlay.pilots.keys() :

            owms_pilot = overlay.pilots[pid]
 
            # only BOUND pilots have a target resource assigned.
            if  owms_pilot.state not in [BOUND] :
                raise RuntimeError ("Can only provision pilots in BOUND state (%s)" % owms_pilot.state)

            # translate information into bigjob speak
            pilot_descr  = pilot_module.PilotComputeDescription ()
            pilot_descr.resource_url        = owms_pilot.resource
            pilot_descr.number_of_processes = owms_pilot.description['size']
            pilot_descr.walltime            = owms_pilot.description['walltime']
            pilot_descr.queue               = owms_pilot.description['queue']
            pilot_descr.working_directory   = "%s/radical_owms_agents/" % owms_pilot.description['home']


            # and create the pilot
          # print "creating pilot with '%s'" % pilot_descr
            bj_pilot = self.cp_service.create_pilot (pilot_descr)

            # register the backend pilot with the radical.owms pilot instance -- that
            # instance will decide how long the pilot handle is kept alive, or
            # when to do a reconnect
            owms_pilot._set_instance (instance_type = 'bigjob', 
                                      provisioner   = self, 
                                      instance      = bj_pilot, 
                                      native_id     = bj_pilot.get_url ())

            radical.owms._logger.info ('overlay  provision: provision pilot  %s : %s ' \
                            % (owms_pilot, owms_pilot._get_instance ('bigjob')))


    # --------------------------------------------------------------------------
    #
    def pilot_reconnect (self, native_id) :
        """
        the pilot lost the instance, and needs to reconnect...
        This is what is getting called on radical.owms.Pilot._get_instance, if that
        radical.owms.Pilot doesn't have that instance anymore...
        """

        bj_pilot = pilot_module.PilotCompute (pilot_url=native_id)

        return bj_pilot
 
 
    # --------------------------------------------------------------------------
    #
    def pilot_get_info (self, pilot) :
        """
        pilot inspection: get all possible information for the pilot, and return
        in a dict.  This dict SHOULD contain 'state' at the very least -- but
        check the pilot_inspection unit test for more recommended attributes.
        """
 
 
        # find out what we can about the pilot...
        bj_pilot= pilot._get_instance ('bigjob')
 
        info     = dict ()
        bj_units = bj_pilot.list_compute_units ()
 
        info['units'] = dict ()
        for bj_unit in bj_units :
            unit = radical.owms.ComputeUnit (pilot.session, 
                                     _native_id=bj_unit.get_url (), 
                                     _pilot_id=pilot.id)
            info['units'][unit.id] = unit

        if  'description' in info :
            # what the fuck?
            info['description'] = eval(info['description'])

        # register bigjob events when they have a valid time stamp.  This may
        # register them multiple times though, but duplication is filtered out
        # on time keeping level
        details = bj_pilot.get_details ()
      # import pprint
      # pprint.pprint (details)
        
        if 'start_time' in details and details['start_time'] :
            pilot.timed_event ('monitor', 'submission', 
                               tags  = ['bigjob', 'start_time'], 
                               timer = details['start_time'])

        if 'end_queue_time' in details and details['end_queue_time'] :
            pilot.timed_event ('monitor', 'start', 
                               tags  = ['bigjob', 'end_queue_time'], 
                               timer = details['end_queue_time'])

        if 'end_time' in details and details['end_time'] :
            pilot.timed_event ('monitor', 'stop', 
                               tags  = ['bigjob', 'end_time'], 
                               timer = details['end_time'])

        if 'last_contact' in details and details['last_contact'] :
            pilot.timed_event ('monitor', 'heartbeat', 
                               tags  = ['bigjob', 'last_contact'], 
                               timer = details['last_contact'])

        if 'start_staging_time' in details and details['start_staging_time'] :
            pilot.timed_event ('monitor', 'start_staging', 
                               tags  = ['bigjob', 'start_staging_time'], 
                               timer = details['start_staging_time'])

 
        # translate bj state to radical.owms state
        # hahaha python switch statement hahahahaha
        info['state'] =  {"New"    : DESCRIBED, 
                          "Running": PROVISIONED, 
                          "Failed" : FAILED, 
                          "Done"   : DONE, 
                          "Unknown": UNKNOWN}.get (bj_pilot.get_state (), UNKNOWN)
 
        return info
 
 
    # --------------------------------------------------------------------------
    #
    def pilot_cancel (self, pilot) :
        """
        bye bye bye Junimond, es ist vorbei, bye bye...
        """
 
        bj_pilot = pilot._get_instance ('bigjob')
        bj_pilot.cancel ()


# ------------------------------------------------------------------------------

