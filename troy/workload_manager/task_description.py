

import radical.utils   as ru
import saga.attributes as sa


# ------------------------------------------------------------------------------
#
class TaskDescription (sa.Attributes) :
    """
    The `TaskDescription` class is a simple container for attributes which
    describe a :class:`Task`, i.e. a workload element.  `TaskDescription`s are
    submitted to :class:`WorkloadManager` instances on `add_task`, and ar
    internally used to create :class:`Task` instances.

    FIXME: description of supported attributes goes here
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, dictionary={}) :


        # set attribute interface properties
        self._attributes_extensible  (True)  # FIXME
        self._attributes_camelcasing (True)
    
        # register attributes
        # FIXME

        self.update (dictionary)


    # --------------------------------------------------------------------------
    #
    def __deepcopy__ (self, memo) :
        other = TaskDescription ()
        return self._attributes_deep_copy (other)



# ------------------------------------------------------------------------------
#
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

