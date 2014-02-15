
from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
class PluginBase (object) :

    # --------------------------------------------------------------------------
    #
    def __init__ (self, description) :

        self.description = description
        self.type        = "%(type)s"          % description
        self.name        = "%(name)s"          % description
        self.longname    = "%(type)s_%(name)s" % description
        self.config_path = "%(type)s:%(name)s" % description


    # --------------------------------------------------------------------------
    #
    def init_plugin (self, session, scope) :

        self.session  = session
        self.troy_cfg = session.get_config ()
        self.cfg      = session.get_config ("%s:%s" % (scope, self.config_path))

        # call plugin.init() as plugin initializer -- if that does not exist,
        # the init() method from below is called as a fallback

        troy._logger.info ("init plugin %s" % (self.longname))
        self.init ()



    # --------------------------------------------------------------------------
    #
    def init (self):

      # troy._logger.debug ("init plugin %s (fallback)" % self.name)
        pass


# ------------------------------------------------------------------------------

