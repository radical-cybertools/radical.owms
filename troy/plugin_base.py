
from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
class PluginBase (object) :

    # --------------------------------------------------------------------------
    #
    def __init__ (self, description) :

        self.description = description
        self.name        = "%(name)s_%(type)s" % self.description


    # --------------------------------------------------------------------------
    #
    def init_plugin (self, session):

        troy._logger.info ("init plugin %s" % (self.name))
        
        self.session    = session
        self.global_cfg = session.cfg
        self.cfg        = session.cfg.as_dict ().get (self.name, {})

        # call plugin.init() as plugin initializer -- if that does not exist,
        # the init() method from below is called as a fallback
        self.init ()


    # --------------------------------------------------------------------------
    #
    def init (self):

      # troy._logger.debug ("init plugin %s (fallback)" % self.name)
        pass


# ------------------------------------------------------------------------------

