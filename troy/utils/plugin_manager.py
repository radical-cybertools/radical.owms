
import imp
import sys
import os


# ------------------------------------------------------------------------------
#
class PluginManager (object) :
    """ 
    The TROY plugin management and loading utility.

    The plugin manater allows to manage plugins of a specific type, such as
    'WorkloadScheduler', 'OverlayScheduler', 'Planner', etc.  For that type, the
    manager can search for installed plugins, list and describe plugins found,
    load plugins, and instantiate the plugin for further use in the TROY code
    base.

    Example::

       pm = troy.PluginManager ('planner')

       for plugin_name in pm.list () :
           print plugin_name
           print pm.describe (plugin_name)

        default_plugin = pm.load ('default')

        default_plugin.init (app_description)
        (overlay_description, workload_description) = default_plugin.run ()

    The plugins are expected to follow a specific naming and coding schema to be
    recognized by the plugin manager.  The naming schema is:

        troy.plugins.[type].plugin_[type]_[name].py

    i.e. for the code example above: `troy.plugins.planner.plugin_planner_default.py`

    The plugin code consists of two parts:  a plugin description, and a plugin
    class.  The description is a module level dictionary named
    `PLUGIN_DESCRIPTION`, the plugin class must be named `PLUGIN_CLASS`, and
    must have a class constructor `__init__(*args, **kwargs)` to create plugin
    instances for further use within TROY.  

    At this point, we leave the definition of the exact plugin signature open,
    but expect that to be strictly defined per plugin type in the future.
    """


    #---------------------------------------------------------------------------
    # 
    def __init__ (self, ptype) :
        """
        ptype: type of plugins to manage
        """

        if  not ptype :
            raise Exception ('no plugin type specified')

        self._ptype   = ptype
        self._plugins = {}

        # load adaptors
        self._load_plugins ()

        print "-------------------------------------------"
        print self._plugins
        print "-------------------------------------------"


    #---------------------------------------------------------------------------
    # 
    def _load_plugins (self) :
        """ 
        Load all plugins of the given type.  All previously loaded plugins are
        thrown away.
        """

        # search for plugins in all system module paths
        for path in sys.path :

            # we only load plugins installed under the troy hierarchy
            ppath = "%s/troy/plugins/%s/"  %  (path, self._ptype)

            if  os.path.isdir (ppath) :

                # we assume that all python sources in that location are
                # suitable plugins
                pfs = os.listdir (ppath)

                for pfile in pfs :

                    # ignore non-python rubbish
                    if  not pfile.endswith ('.py') :
                        continue

                    # ignore other plugin types
                    if  not pfile.startswith ("plugin_%s" % self._ptype) :
                        continue

                    # strip the trailing '.py' to get plugin name, and also
                    # strip plugin type prefix
                    prefix_len = len ("plugin_%s_" % self._ptype)
                    pf_name    = pfile[prefix_len:-3]
                    mod_name   = "troy.plugins.%s.%s" % (self._ptype, pfile[:-3])

                    # load and register the plugin
                    plugin = imp.load_source (mod_name, "%s/%s" % (ppath, pfile))
                    self._plugins[pf_name] = {
                        'class'       : plugin.PLUGIN_CLASS,
                        'version'     : plugin.PLUGIN_DESCRIPTION['version'],
                        'description' : plugin.PLUGIN_DESCRIPTION['description']
                    }


    #---------------------------------------------------------------------------
    # 
    def load (self, name, *args, **kwargs) :
        """
        check if a plugin with given name was loaded, if so, instantiate its
        plugin class, initialize and return in.
        """
        if  not name in self._plugins :
            raise Exception ("No such plugin %s" % name)

        return self._plugins[name]['class'](*args, **kwargs)


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

