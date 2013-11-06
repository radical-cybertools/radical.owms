
import pilot


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
            
            bj_manager = bigjob.BigJobManager ()
            bj_pilot   = bj_manager.create_pilot (pilot.descr)

            pilot._set_instance ([bj_pilot, bj_manager])
            pilot._bind ('ssh://localost')


# ------------------------------------------------------------------------------

