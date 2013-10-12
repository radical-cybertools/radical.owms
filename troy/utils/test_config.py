
__author__    = "Andre Merzky, Ole Weidner"
__copyright__ = "Copyright 2012-2013, The SAGA Project"
__license__   = "MIT"


import radical.utils          as ru


# ------------------------------------------------------------------------------
#
class TestConfig (ru.TestConfig): 

    #-----------------------------------------------------------------
    # 
    def __init__ (self, cfg_file):

        # initialize configuration.  We only use the 'saga.tests' category from
        # the config file.
        ru.TestConfig.__init__ (self, cfg_file, 'troy.tests')


# ------------------------------------------------------------------------------
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

