

# ------------------------------------------------------------------------------
#
PLUGIN_DESCRIPTION = {
    'type'        : 'workload_scheduler', 
    'name'        : 'round_robin', 
    'version'     : '0.1',
    'description' : 'simple scheduler, assigns CUs to pilots in round-robin fashion.'
  }


# ------------------------------------------------------------------------------
#
class PLUGIN_CLASS (object) :
    """
    This class implements the (trivial) round-robin workload scheduler algorithm for
    TROY.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self) :

        print "create the round-robin workload_scheduler plugin"


    # --------------------------------------------------------------------------
    #
    def schedule (self, workload, overlay) :

        with workload.lock () and overlay.lock () :

            # if  not overlay.pilots :
            #     raise ValueError ("no pilots to schedule over")
            #
            # next_pilot = 0
            #
            # for t in workload.tasks :
            #     for c in t.compute_units :
            #         c.target_pilot = overlay.pilots[next_pilot].id
            #         next_pilot += 1
            #         if  next_pilot >= len (overlay.pilots) :
            #             next_pilot  = 0
            #

            # do nothing
            pass


# ------------------------------------------------------------------------------

