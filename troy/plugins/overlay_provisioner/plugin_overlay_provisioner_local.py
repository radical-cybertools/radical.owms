

import os
import time
import subprocess
import radical.utils as ru

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'overlay_provisioner', 
    'name'        : 'local', 
    'version'     : '0.1',
    'description' : 'this is a scheduler which provisions no pilots.'
  }


# ------------------------------------------------------------------------------
#
_NEW      = 'New'
_RUNNING  = 'Running'
_FAILED   = 'Failed'
_DONE     = 'Done'
_CANCELED = 'Canceled'


# ------------------------------------------------------------------------------
#
class _Unit (object) :

    def __init__ (self, descr) :

        self.id     = ru.generate_id ('d.u.')
        self.descr  = descr
        self._state = _NEW
        self.start  = None
        self.proc   = None
        self.retval = None

        if  not 'executable' in self.descr :
            self.descr['executable'] = '/bin/true'

        if  not 'arguments' in self.descr :
            self.descr['arguments'] = list()

        if  not 'environment' in self.descr :
            self.descr['environment'] = list()

        troy._logger.debug ("new     unit %s" % (self.id))



    def run (self) :

        assert (self.state == _NEW)

        env = dict()

        for key in os.environ.keys() :
            env[key] = os.environ[key]

        for env_entry in self.descr['environment'] :
            key, val = env_entry.split ('=', 1)
            env[key] = val

        pwd     = self.descr.get ('working_directory', '.')
        command = "cd %s ; %s %s" % (pwd, self.descr['executable'], 
                                     ' '.join (self.descr['arguments'])) 

        troy._logger.debug ("running unit %s (%s)" % (self.id, command))

        self._proc   = subprocess.Popen ([command], env=env,
                                         shell=True,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
        self.state   = _RUNNING
        self.start   = time.time()



    def get_state (self) :

        if  self._state in [_NEW, _DONE, _FAILED, _CANCELED] :
            return self._state

        if  self._state in [_RUNNING] :

            if  self._proc.poll () is not None :
                self.retval = self._proc.returncode

                if  self.retval == 0 :
                    self._state = _DONE
                else :
                    self._state = _FAILED

                out, err = self._proc.communicate()
                troy._logger.debug ("unit finished: %s" % self.id)
                troy._logger.debug ("     exitcode: %s" % self.retval)
                troy._logger.debug ("     output  : %s" % out)
                troy._logger.debug ("     error   : %s" % err)

        return self._state


    def set_state (self, val) :
        self._state = val

    state = property (get_state, set_state)


    def wait (self) :

        while self.state not in [_DONE, _FAILED, _CANCELED] :

            time.sleep (0.1)


    def cancel (self) :


        if  self.state in [_RUNNING] :
            self._proc.terminate ()
            self._proc.kill      ()

        self.state = _CANCELED

        troy._logger.debug ("cancel  unit %s" % (self.id))



# ------------------------------------------------------------------------------
#
class _Pilot (object) :

    def __init__ (self, pilot) :

        self.id    = ru.generate_id ('d.p.')
        self.units = dict()
        self.state = _NEW
        self.start = None
        self.pilot = pilot
        self.descr = pilot.description

        troy._logger.debug ("new     pilot %s" % (self.id))


    def run (self) :

        self.state = _RUNNING
        self.start = time.time()
        troy._logger.debug ("run     pilot %s" % (self.id))


    def submit_unit (self, descr) :

        unit = _Unit (descr)
        unit.run ()
        self.units[unit.id] = unit

        troy._logger.debug ("submit  unit %s to pilot %s" % (unit.id, self.id))

        return unit


    def list_units (self) :

        return self.units.keys ()


    def cancel (self) :

        troy._logger.debug ("cancel  pilot %s" % (self.id))
        self.state = _CANCELED


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (troy.PluginBase):
    """
    This class implements the defaul overlay provisioner for TROY.  It simply
    assumes that the application is its own pilot, and does not create a new
    pilot...
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        troy.PluginBase.__init__ (self, PLUGIN_DESCRIPTION)

        self.pilots = dict()
        self.state  = _NEW


    # --------------------------------------------------------------------------
    #
    def provision (self, overlay) :

        # we simply assign all pilots to localhost
        for pid in overlay.pilots.keys() :

            pilot = overlay.pilots[pid]
 
            if  pilot.state not in [BOUND] :
                raise RuntimeError ("Can only provision pilots in BOUND state (%s)" % pilot.state)

            resource = ru.Url (pilot.resource)

            if  resource.scheme != 'fork'      \
            or  resource.host   != 'localhost' :
                    raise ValueError ("Can only provision to fork://localhost (%s)" % resource)

            p = _Pilot (pilot)
            p.run ()

            self.pilots[p.id] = p
        
            pilot._set_instance (instance_type = 'default', 
                                 provisioner   = self, 
                                 instance      = p,
                                 native_id     = p.id)

            troy._logger.info ('overlay  provision: provision pilot  %s : %s ' % (pilot, p))


    # --------------------------------------------------------------------------
    #
    def pilot_reconnect (self, native_id) :

        if  native_id in self.pilots :
            return self.pilots[native_id]

        raise LookupError ("no pilot %s known" % native_id)

 
    # --------------------------------------------------------------------------
    #
    def pilot_get_info (self, pilot) :
 
 
        # find out what we can about the pilot...
        p = pilot._get_instance ('default')
 
        info  = dict ()
        info['units'] = dict()

        for unit_id in p.list_units () :
            unit = troy.ComputeUnit (_native_id=unit_id, _pilot_id=pilot.id)
            info['units'][unit.id] = unit

        # hahaha python switch statement hahahahaha
        info['state'] =  {_NEW      : DESCRIBED, 
                          _RUNNING  : PROVISIONED, 
                          _FAILED   : FAILED, 
                          _CANCELED : CANCELED, 
                          _DONE     : DONE}.get (p.state, UNKNOWN)

        # for inspection compatibility
        info['native_description'] = p.descr
        info['start_time']         = p.start
        info['last_contact']       = time.time ()
        info['end_queue_time']     = -1
        info['processes_per_node'] = 1 
        info['slots']              = 1
        info['working_directpry']  = os.getcwd ()
        info['service_url']        = 'fork://localhost' 
 
        return info
 
 
    # --------------------------------------------------------------------------
    #
    def pilot_cancel (self, pilot) :
 
        p   = pilot._get_instance ('default')
        pid = p.id

        p.cancel ()

        if  pid in self.pilots :
            self.pilots[pid] = None
            del self.pilots[pid]


# ------------------------------------------------------------------------------

