
from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
class PluginBase (object) :

    # --------------------------------------------------------------------------
    #
    def __init__ (self, description) :

        self.description = description
        self.name        = "%(type)s_%(name)s" % self.description


    # --------------------------------------------------------------------------
    #
    def init_plugin (self, session):

        troy._logger.info ("init plugin %s" % (self.name))

        self.session    = session
        self.global_cfg = session.cfg.as_dict ()

        # merge user configuration into global_config
        self.global_cfg.update (session.user_cfg)

        self.cfg        = self.global_cfg.get (self.name, dict())

        # call plugin.init() as plugin initializer -- if that does not exist,
        # the init() method from below is called as a fallback
        self.init ()


    # --------------------------------------------------------------------------
    #
    def init (self):

      # troy._logger.debug ("init plugin %s (fallback)" % self.name)
        pass


# ------------------------------------------------------------------------------

