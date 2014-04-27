#!/usr/bin/env python

__author__    = "RADICAL Development Team"
__copyright__ = "Copyright 2014, RADICAL"
__license__   = "MIT"


import sys
import radical.owms


radical.owms.manage_workload (workload = sys.argv[1], 
                              config   = sys.argv[2:])

# Woohooo!  Magic has happened!

