#!/usr/bin/env python

__author__    = "TROY Development Team"
__copyright__ = "Copyright 2014, RADICAL"
__license__   = "MIT"


import sys
import troy

session = troy.Session (user_cfg = sys.argv[2:])
planner = troy.Planner (session)

planner.execute_workload (workload = sys.argv[1])
                      
# Woohooo!  Magic has happened!

