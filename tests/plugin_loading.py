
import radical.utils as ru

pmgr    = ru.PluginManager ('troy', 'workload_scheduler')
default = pmgr.load ('default', 'workload', 'overlay')

print default.run ()

