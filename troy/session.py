
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import saga
import troy
import logging
import radical.utils as ru
import troy.utils    as tu


def _format_log_level (log_level) :

    return {
            'debug'    : logging.DEBUG,
            'info'     : logging.INFO,
            'warning'  : logging.WARNING,
            'error'    : logging.ERROR,
            'critical' : logging.CRITICAL
            } [log_level.lower()]

    raise ValueError ('%s is not a valid value for log_level.' % log_level)



# ------------------------------------------------------------------------------
#
class Session (saga.Session, tu.Timed) : 

    # --------------------------------------------------------------------------
    #
    def __init__ (self, cfg={}, default=True, tag=None) :

        stub = 'session.'
        if  tag :
            stub = 'session.%s.' % tag

        self.id = ru.generate_id (stub, mode=ru.ID_UNIQUE)
        
        tu.Timed.__init__ (self, 'troy.Session', self.id)
        self.timed_method ('saga.Session', ['init'],  
                           saga.Session.__init__, [self, default])

        self.cfg        = troy.Configuration ()
        self.user_cfg   = cfg
        self._apitype   = 'saga.Session'

        if  'troy' in cfg :
            if 'log_level' in cfg['troy'] :
                log_level  =  cfg['troy']['log_level']
                troy._logger.setLevel (log_level)

        troy._logger.info ("session id: %s" % self.id)


    # --------------------------------------------------------------------------
    #
    def get_config (self, section=None) :

        if  section :
            return self.cfg.as_dict ().get (section, {})
        else :
            return self.cfg.as_dict ()


# ------------------------------------------------------------------------------
#
class Context (saga.Context) : 

    # --------------------------------------------------------------------------
    #
    def __init__ (self, ctype) :

        self._apitype = 'saga.Context'

        saga.Context.__init__ (self, ctype)
    

# ------------------------------------------------------------------------------

