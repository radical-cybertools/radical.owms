#!/usr/bin/env python

__author__    = "TROY Development Team"
__copyright__ = "Copyright 2014, RADICAL"
__license__   = "MIT"


import sys
import troy


# ------------------------------------------------------------------------------
#
def usage (msg) :

    if  msg :
        print "\n\terror: %s\n" % msg

    print "\tUsage: %s <workload> <config>" % sys.argv[0]
    print
    print """
        <workload>    troy workload description (JSON)
        <config>      application description   (JSON)

"""

    if  msg : sys.exit (-1) 
    else    : sys.exit ( 0)


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) < 3 : usage ('parameter mismatch') 
    if 'help' in sys.argv : usage ()
        
    workload_description = sys.argv[1]
    application_configs  = sys.argv[2:]

    troy.manage_workload (workload = workload_description,
                          config   = application_configs)

    # Woohooo!  Magic has happened!

