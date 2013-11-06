
import os
import bigjob


from   troy.constants import *


# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'overlay_provisioner', 
    'name'        : 'bigjob', 
    'version'     : '0.1',
    'description' : 'this is a scheduler which provisions bigjob pilots.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the bigjob overlay provisioner for
    TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        print "create the bigjob overlay_provisioner plugin"


    # --------------------------------------------------------------------------
    #
    def provision (self, overlay) :

        # we simply assign all pilots to localhost
        for pilot in overlay.pilots :
            
            # FIXME: ceck state
            bj_manager   = bigjob.bigjob (coordination_url=os.environ['COORDINATION_URL'])
            bj_pilot_url = bj_manager.start_pilot_job (pilot.resource)


            pilot._set_instance ([bj_pilot_url, bj_manager])


# ------------------------------------------------------------------------------

