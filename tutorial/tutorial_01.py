#!/usr/bin/env python

__author__    = "TROY Development Team"
__copyright__ = "Copyright 2014, RADICAL"
__license__   = "MIT"


import sys
import troy


session = troy.manage_workload (workload = sys.argv[1], 
                                config   = sys.argv[2:])

session.timed_store('mongodb://ec2-184-72-89-141.compute-1.amazonaws.com:27017/timing/')

# Woohooo!  Magic has happened!

