
__author__    = "Andre Merzky, Ole Weidner"
__copyright__ = "Copyright 2012-2013, The SAGA Project"
__license__   = "MIT"


import radical.utils.testing  as rut


# ------------------------------------------------------------------------------
#
class TestConfig (rut.TestConfig): 

    #-----------------------------------------------------------------
    # 
    def __init__ (self, cfg_file):

        # initialize configuration.  We only use the 'saga.tests' category from
        # the config file.
        rut.TestConfig.__init__ (self, cfg_file, 'troy.tests')


# ------------------------------------------------------------------------------


