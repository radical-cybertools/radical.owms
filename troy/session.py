
__author__    = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import saga
import troy


# ------------------------------------------------------------------------------
#
class Session (saga.Session) : 

    def __init__ (self, cfg={}, default=True) :

        self.cfg      = troy.Configuration ()
        self.user_cfg = cfg
        self._apitype = 'saga.Session'

        saga.Session.__init__ (self, default)

    
# ------------------------------------------------------------------------------
#
class Context (saga.Context) : 

    def __init__ (self, ctype) :

        self._apitype = 'saga.Context'

        saga.Context.__init__ (self, ctype)
    

# ------------------------------------------------------------------------------

