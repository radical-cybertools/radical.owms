#!/usr/bin/env python

__author__    = "TROY Development Team"
__copyright__ = "Copyright 2014, RADICAL"
__license__   = "MIT"


import sys
import troy


troy.manage_workload (workload = sys.argv[1], 
                      config   = sys.argv[2:])

