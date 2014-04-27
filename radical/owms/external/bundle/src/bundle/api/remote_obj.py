# This is the code that visits the warehouse.
import sys
import Pyro4
import Pyro4.util

sys.excepthook = Pyro4.util.excepthook

def getBundleManagerRO(ro_name="PYRONAME:BundleManager"):
    bm = Pyro4.Proxy(ro_name)
    return bm
