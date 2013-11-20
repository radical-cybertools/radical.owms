
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

_idx = 0

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
        for pid in overlay.pilots.keys() :
            pilot = overlay.pilots[pid]
 
            if  pilot.state not in [BOUND] :
                raise RuntimeError ("Can only provision pilots in BOUND state (%s)" % pilot.state)

            global _idx
            
            # FIXME: ceck state
            bj_manager   = bigjob.bigjob (coordination_url=os.environ['COORDINATION_URL'])
            bj_pilot_url = bj_manager.start_pilot_job (pilot._resource,
                               working_directory='/home/merzky/agent')

            _idx += 1

            pilot._set_instance ('bigjob', self, [bj_pilot_url, bj_manager])

            print 'overlay  provision: provision pilot  %s : %s ' \
                % (pilot, pilot._get_instance ('bigjob'))


    # --------------------------------------------------------------------------
    #
    def pilot_cancel (self, pilot) :

        bj_pilot_url, bj_manager = pilot._get_instance ('bigjob')
        bj_manager.cancel ()


# ------------------------------------------------------------------------------

