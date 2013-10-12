

import saga.attributes as sa


# ------------------------------------------------------------------------------
#
class Description (sa.Attributes) :
    """ 
    Base class for `TaskDescription`, `RelationDescription` etc.  

    Instances of this class and its derivates should never be deep-copied --
    only one representation of any described entity should exist in Troy, and
    referenced as needed. (This is not enforced On Python level though)

    This base class provides a reentrant lock, so that all transformations on
    the description can be implemented thread-safe.
    """
    self._rlock = threading.RLock ()


# ------------------------------------------------------------------------------
#
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

