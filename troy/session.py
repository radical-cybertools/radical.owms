
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import saga
import troy
import logging

def _format_log_level (log_level) :

    return {
            'debug'    : logging.DEBUG,
            'info'     : logging.INFO,
            'warning'  : logging.WARNING,
            'error'    : logging.ERROR,
            'critical' : logging.CRITICAL
            } [log_leverl.lower()]

    raise ValueError ('%s is not a valid value for log_level.' \
                   % (log_level, log_level))



# ------------------------------------------------------------------------------
#
class Session (saga.Session) : 

    def __init__ (self, cfg={}, default=True) :

        self.cfg      = troy.Configuration ()
        self.user_cfg = cfg
        self._apitype = 'saga.Session'

        if  'troy' in cfg :
            if 'log_level' in cfg['troy'] :
                log_level  =  cfg['troy']['log_level']
                troy._logger.setLevel (log_level)

        saga.Session.__init__ (self, default)


    def get_config (self, section=None) :

        if  section :
            return self.cfg.as_dict ().get (section, {})
        else :
            return self.cfg.as_dict ()



    
# ------------------------------------------------------------------------------
#
class Context (saga.Context) : 

    def __init__ (self, ctype) :

        self._apitype = 'saga.Context'

        saga.Context.__init__ (self, ctype)
    

# ------------------------------------------------------------------------------

