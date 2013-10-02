
import troy.utils.plugin_manager

pm = troy.utils.plugin_manager.PluginManager ('workload_scheduler')

default_scheduler = pm.load ('default', 'workload', 'overlay')

print default_scheduler.run ()

