
from   radical.owms.constants import *
import radical.owms


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
        self.cfg      = session.get_config ("%s:%s" % (scope, self.config_path))

        # call plugin.init() as plugin initializer -- if that does not exist,
        # the init() method from below is called as a fallback

        radical.owms._logger.info ("init plugin %s" % (self.longname))
        self.init ()



    # --------------------------------------------------------------------------
    #
    def init (self):

      # radical.owms._logger.debug ("init plugin %s (fallback)" % self.name)
        pass


# ------------------------------------------------------------------------------

