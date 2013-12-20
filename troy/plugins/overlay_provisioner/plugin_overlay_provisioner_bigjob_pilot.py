
import os
import pilot         as pilot_module
import radical.utils as ru

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'overlay_provisioner', 
    'name'        : 'bigjob_pilot', 
    'version'     : '0.1',
    'description' : 'this is a scheduler which provisions bigjob pilots.'
  }

# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the bigjob_pilot overlay provisioner for
    TROY.
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :
        """
        invoked when plugin is loaded. Only do sanity checks, no other
        initialization
        """

        self.description = PLUGIN_DESCRIPTION
        self.name        = "%(name)s_%(type)s" % self.description


    # --------------------------------------------------------------------------
    #
    def init (self, cfg):
        """
        invoked by user of plugin, i.e. a overlay manager.  May get invoked
        multiple times -- plugins are singletons, and thus shared amongst all
        overlay managers!
        """

        troy._logger.info ("init the bigjob_pilot overlay provisioner plugin")
        
        self.cfg = cfg.as_dict ().get (self.name, {})

        if  not 'COORDINATION_URL' in os.environ :
            troy._logger.error ("No COORDINATION_URL set for bigjob_pilot backend")
            troy._logger.info  ("example: export COORDINATION_URL=redis://<pass>@gw68.quarry.iu.teragrid.org:6379")
            troy._logger.info  ("Contact Radica@Ritgers for the redis password")
            raise RuntimeError ("Cannot use bigjob_pilot backend - no COORDINATION_URL set -- see debug log for details")

        self._coord     = os.environ['COORDINATION_URL'] 
        self.cp_service = pilot_module.PilotComputeService (self._coord)


    # --------------------------------------------------------------------------
    #
    def provision (self, overlay) :
        """
        provision a given overlay -- inspect that overlay, dig out the pilots
        and their description, check state, and instantiate them via the backend
        system.
        """

        # we simply assign all pilots to localhost
        for pid in overlay.pilots.keys() :

            pilot = overlay.pilots[pid]
 
            # only BOUND pilots have a target resource assigned.
            if  pilot.state not in [BOUND] :
                raise RuntimeError ("Can only provision pilots in BOUND state (%s)" % pilot.state)

            # translate information into bigjob speak
            pilot_descr                     = pilot_module.PilotComputeDescription ()
            pilot_descr.service_url         = pilot._resource
            pilot_descr.number_of_processes = pilot.description['size']

            if  'futuregrid' in pilot._resource :
                # FIXME: uh oh...
                pilot_descr.working_directory = '/N/u/merzky/agent/' 

            if  'localhost' in pilot._resource :
                # FIXME: uh oh...
                pilot_descr.working_directory = '%s/bj_agent' % os.environ['HOME']

            # and create the pilot
            bj_pilot = self.cp_service.create_pilot (pilot_descr)

            # register the backend pilot with the troy pilot instance -- that
            # instance will decide how long the pilot handle is kept alive, or
            # when to do a reconnect
            pilot._set_instance (instance_type = 'bigjob_pilot', 
                                 provisioner   = self, 
                                 instance      = bj_pilot, 
                                 native_id     = bj_pilot.get_url ())

            troy._logger.info ('overlay  provision: provision pilot  %s : %s ' \
                            % (pilot, pilot._get_instance ('bigjob_pilot')))


    # --------------------------------------------------------------------------
    #
    def pilot_reconnect (self, native_id) :
        """
        the pilot lost the instance, and needs to reconnect...
        This is what is getting called on troy.Pilot._get_instance, if that
        troy.Pilot doesn't have that instance anymore...
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
        bj_pilot= pilot._get_instance ('bigjob_pilot')
 
        info     = dict ()
        bj_units = bj_pilot.list_compute_units ()
 
        info['units'] = dict ()
        for bj_unit in bj_units :
            unit = troy.ComputeUnit (_native_id=bj_unit.get_url (), _pilot_id=pilot.id)
            info['units'][unit.id] = unit
 
        # translate bj state to troy state
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
 
        bj_pilot = pilot._get_instance ('bigjob_pilot')
        bj_pilot.cancel ()


# ------------------------------------------------------------------------------

