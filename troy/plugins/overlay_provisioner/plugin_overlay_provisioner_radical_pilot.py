

import os
import getpass

import radical.pilot as rp
import radical.utils as ru

from   troy.constants import *
import troy


FGCONF    = 'https://raw.github.com/radical-cybertools/radical.pilot/master/configs/futuregrid.json'
XSEDECONF = 'https://raw.github.com/radical-cybertools/radical.pilot/master/configs/xsede.json'
WALLTIME_OVERHEAD = 10.0


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'overlay_provisioner', 
    'name'        : 'radical.pilot', 
    'version'     : '0.1',
    'description' : 'this is a plugin which provisions radical.pilot pilots.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (troy.PluginBase):
    """
    This plugin creates pilots via the RADICAL-Pilot Pilot API.

    **Configuration Options:**

    * `coordination_url`: the redis URL to be used by RADICAL-Pilot.  The environment
        variable COORDINATION_URL is used as fallback.
    * `walltime_overhead`:   a constant walltime offset to add to troy-derived
        pilot walltimes, to cater for radical.pilot internal overhead.
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)

        self._credentials = list()
        self._coord       = None


    # --------------------------------------------------------------------------
    #
    def init (self):

        # dig parameters out of the config
        self._overhead = float(self.cfg.get ('walltime_overhead', WALLTIME_OVERHEAD))

        if  'coordination_url' in self.cfg :
            self._coord = self.cfg['coordination_url']

        elif 'COORDINATION_URL' in os.environ :
            self._coord = os.environ['COORDINATION_URL'] 

        else :
            troy._logger.error ("No COORDINATION_URL set for radical.pilot backend")
            troy._logger.info  ("example: export COORDINATION_URL=redis://<pass>@gw68.quarry.iu.teragrid.org:6379")
            troy._logger.info  ("Contact Radica@Ritgers for the redis password")
            raise RuntimeError ("Cannot use radical.pilot backend - no COORDINATION_URL -- see debug log for details")


        self._rp = rp.Session (database_url = self._coord)


    # --------------------------------------------------------------------------
    #
    def provision (self, overlay) :
        """
        provision a given overlay -- inspect that overlay, dig out the pilots
        and their description, check state, and instantiate them via the backend
        system.

        For each pilot, we need to also keep the pilot manager and the unit
        manager -- otherwise we are not able to reconnec to to pilots and units.
        So whenever a pilot is created, we immediately also create a unit
        manager, ad pass it around with the PM and pilot instance.
        """

        for pid in overlay.pilots.keys() :

            troy_pilot = overlay.pilots[pid]
 
            # only BOUND pilots have a target resource assigned.
            if  troy_pilot.state not in [BOUND] :
                raise RuntimeError ("Can only provision BOUND pilots (%s)" % troy_pilot.state)

            # translate information into bigjob speak
            pilot_descr = rp.ComputePilotDescription ()
            pilot_descr.resource = troy_pilot.description['hostname']
            pilot_descr.cores    = troy_pilot.description['size']
            pilot_descr.runtime  = troy_pilot.description['walltime'] + self._overhead
            pilot_descr.queue    = troy_pilot.description['queue']

            if  'home' in troy_pilot.description and troy_pilot.description['home']:
                print troy_pilot.description['home']
                pilot_descr.sandbox  = "%s/troy_agents/" % troy_pilot.description['home']

            troy._logger.info ('overlay  provision: provision   pilot  %s : %s : %s' \
                            % (pid, troy_pilot.resource, pilot_descr))

            if  'username' in troy_pilot.description :
                username = troy_pilot.description['username']

                if  username and username not in self._credentials :
                    self._credentials.append (username)

                    cred = rp.SSHCredential()
                    cred.user_id = username
                    self._rp.add_credential(cred)
                    print "added username %s @ %s" % (username, pilot_descr.resource)


            # and create the pilot overlay
            rp_um    = rp.UnitManager  (session   = self._rp, 
                                        scheduler = 'direct_submission')
            rp_pm    = rp.PilotManager (session   = self._rp, 
                                        resource_configurations = [FGCONF, XSEDECONF])
            rp_pilot = rp_pm.submit_pilots (pilot_descr)

            rp_um.add_pilots (rp_pilot)

            troy_pilot._set_instance (instance_type = 'radical.pilot', 
                                      provisioner   = self, 
                                      instance      = [rp_um,     rp_pm,     rp_pilot], 
                                      native_id     = [rp_um.uid, rp_pm.uid, rp_pilot.uid])

            troy._logger.info ('overlay  provision: provisioned pilot  %s : %s (%s)' \
                            % (troy_pilot, 
                               troy_pilot._get_instance ('radical.pilot')[2], 
                               troy_pilot.resource))


    # --------------------------------------------------------------------------
    #
    def pilot_reconnect (self, native_id) :
        """
        the pilot lost the instance, and needs to reconnect...
        This is what is getting called on troy.Pilot._get_instance, if that
        troy.Pilot doesn't have that instance anymore...
        """

        rp_um_id    = native_id[0]
        rp_pm_id    = native_id[1]
        rp_pilot_id = native_id[2]

        rp_um       = self._rp.get_unit_managers  (rp_um_id)
        rp_pm       = self._rp.get_pilot_managers (rp_pm_id)
        rp_pilot    = rp_pm.get_pilots            (rp_pilot_id)

        return [rp_um, rp_pm, rp_pilot]
    
 
    # --------------------------------------------------------------------------
    #
    def pilot_get_info (self, pilot) :
        """
        pilot inspection: get all possible information for the pilot, and return
        in a dict.  This dict SHOULD contain 'state' at the very least -- but
        check the pilot_inspection unit test for more recommended attributes.
        """
 
 
        # find out what we can about the pilot...
        [rp_um, rp_pm, rp_pilot] = pilot._get_instance ('radical.pilot')

      # rp_pilot._attributes_dump ()

        info = { 'uid'              : rp_pilot.uid, 
                 'description'      : rp_pilot.description, 
                 'state'            : rp_pilot.state, 
                 'log'              : rp_pilot.log, 
                 'resource_detail'  : rp_pilot.resource_detail, 
                 'cores_per_node'   : rp_pilot.resource_detail['cores_per_node'],
                 'nodes'            : rp_pilot.resource_detail['nodes'],
                 'unit_ids'         : list(),
               # 'unit_ids'         : rp_pilot.units,          # FIXME
                 'unit_managers'    : list(),
               # 'unit_managers'    : rp_pilot.unit_managers,  # FIXME
                 'pilot_manager'    : rp_pilot.pilot_manager, 
                 'submission_time'  : rp_pilot.submission_time, 
                 'start_time'       : rp_pilot.start_time, 
                 'stop_time'        : rp_pilot.stop_time, 
             }

        
      # # FIXME
      # for rp_unit_id in rp_pilot.units :
      #     
      #     unit = troy.ComputeUnit (pilot.session, 
      #                              _native_id=[rp_um.uid, rp_unit_id], 
      #                              _pilot_id=pilot.id)
      #     info['units'][unit.id] = unit
 
        # translate radical.pilot state to troy state
        # hahaha python switch statement hahahahaha
        info['state'] =  {rp.states.PENDING  : PROVISIONED, 
                          rp.states.RUNNING  : PROVISIONED, 
                          rp.states.DONE     : COMPLETED, 
                          rp.states.CANCELED : CANCELED, 
                          rp.states.FAILED   : FAILED, 
                          rp.states.UNKNOWN  : UNKNOWN}.get (rp_pilot.state, UNKNOWN)
 
      # import pprint
      # pprint.pprint (info)
      #
      # {'cores_per_node'   : 4,
      #  'description'      : <radical.pilot.compute_pilot_description.ComputePilotDescription object at 0x28d6a50>,
      #  'nodes'            : [u'localhost'],
      #  'pilot_manager'    : <radical.pilot.pilot_manager.PilotManager object at 0x28d6e10>,
      #  'resource_detail' : {'cores_per_node': 4, 'nodes': [u'localhost']},
      #  'start_time'       : datetime.datetime(2014, 2, 5, 13, 4, 56, 145000),
      #  'state'            : 'Provisioned',
      #  'log'              : [u"Created agent directory 'file://localhost/home/merzky/troy_agents/pilot-52f236e4f2291a42e669a2b0/'",
      #                        u"Copied 'file://localhost//home/merzky/saga/troy/ve/bin/bootstrap-and-run-agent' script to agent directory",
      #                        u"Copied
      #                        'file://localhost//home/merzky/saga/troy/ve/local/lib/python2.7/site-packages/radical.pilot-0.4-py2.7.egg/radical.pilot/agent/radical.pilot-agent.py' script to agent directory",
      #                        u"Pilot Job successfully submitted with JobID '[fork://localhost]-[20505]'"],
      #  'stop_time'        : None,
      #  'submission_time'  : datetime.datetime(2014, 2, 5, 13, 4, 42, 239000),
      #  'uid'              : '52f236e4f2291a42e669a2b0',
      #  'unit_ids'         : [],
      #  'unit_managers'    : []}


        # register radical.pilot events when they have a valid time stamp.  This may
        # register them multiple times though, but duplication is filtered out
        # on time keeping level
        if 'submission_time' in info and info['submission_time'] :
            pilot.timed_event ('monitor', 'submission', 
                               tags  = ['radical.pilot', 'submission_time'],
                               timer = info['submission_time'])

        if 'start_time' in info and info['start_time'] :
            pilot.timed_event ('monitor', 'start', 
                               tags  = ['radical.pilot', 'start_time'],
                               timer = info['start_time'])

        if 'stop_time' in info and info['stop_time'] :
            pilot.timed_event ('monitor', 'stop', 
                               tags  = ['radical.pilot', 'stop_time'],
                               timer = info['stop_time'])

        return info
 
 
    # --------------------------------------------------------------------------
    #
    def pilot_cancel (self, pilot) :
 
        [rp_um, rp_pm, rp_pilot] = pilot._get_instance ('radical.pilot')
        rp_pilot.cancel ()


# ------------------------------------------------------------------------------

