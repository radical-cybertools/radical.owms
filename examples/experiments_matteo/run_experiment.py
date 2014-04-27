#!/usr/bin/env python

__author__    = "RADICAL Development Team"
__copyright__ = "Copyright 2014, RADICAL"
__license__   = "MIT"


import sys
import radical.owms

session = radical.owms.Session   (user_cfg = sys.argv[2:])
planner = radical.owms.Planner   (session)
planner.execute_workload (workload = sys.argv[1])

# Woohooo!  Magic has happened!

