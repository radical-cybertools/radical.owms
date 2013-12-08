

import time
import subprocess
import radical.utils as ru

from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'overlay_provisioner', 
    'name'        : 'default', 
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

        exe        =           self.descr['executable']
        args       = ' '.join (self.descr['arguments'])
        env_list   =           self.descr['environment']
        env        = dict()

        for env_entry in env_list :
            key, val = env_entry.split ('=', 1)
            env[key] = val


        command    = "%s %s" % (exe, args)
        self._proc = subprocess.Popen (command, shell=True, env=env, 
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
        self.state = _RUNNING

        troy._logger.debug ("running unit %s (%s)" % (self.id, command))


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

    def __init__ (self, obj) :

        self.id    = ru.generate_id ('d.p.')
        self.units = dict()
        self.state = _NEW
        self.obj   = obj

        troy._logger.debug ("new     pilot %s" % (self.id))


    def run (self) :

        self.state = _RUNNING
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
class PLUGIN_CLASS (object) :
    """
    This class implements the defaul overlay provisioner for TROY.  It simply
    assumes that the application is its own pilot, and does not create a new
    pilot...
    """

    __metaclass__ = ru.Singleton


    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        self.description = PLUGIN_DESCRIPTION
        self.name        = "%(name)s_%(type)s" % self.description
        self.pilots      = dict()


    # --------------------------------------------------------------------------
    #
    def init (self, cfg):

        troy._logger.info ("init the default overlay provisioner plugin")
        
        self.cfg = cfg.as_dict ().get (self.name, {})


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
        units = p.list_units ()
 
        # hahaha python switch statement hahahahaha
        info['state'] =  {_NEW      : DESCRIBED, 
                          _RUNNING  : PROVISIONED, 
                          _FAILED   : FAILED, 
                          _CANCELED : CANCELED, 
                          _DONE     : DONE}.get (p.state, UNKNOWN)
 
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

