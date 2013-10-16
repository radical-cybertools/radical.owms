

import copy
import threading

import radical.utils   as ru
import saga.attributes as sa


# ------------------------------------------------------------------------------
#
class Task (sa.Attributes) :
    """
    The `Task` class represents a element of work to be performed on behalf of
    an application, and is part of a workload managed by Troy.

    Task instances are created and owned by the :class:`Workload` class they are
    part of -- only that class should change its composition and state.  Tasks
    are created according to a :class:`TaskDescription`, i.e. a set of key-value
    pairs describing the represented workload element.

    As tasks are components of a :class:`Workload`, they are subject to the
    transformations the workload undergoes (see :class:`Workload` documentation
    for details).  During that process, tasks are enriched with additional
    information, which are kept as additional member attributes::

     - *`Task.translated = list()`*: This list will contain a list of
       :class:`ComputeUnitDescriptions` in which the task has been translated
       into.  In the case of task decomposition, a task may contain multiple of
       those :class:`ComputeUnitDescription`s; in the case of task aggregation,
       only one of the tasks may contain such a description, while the other
       aggregated tasks contain none (i.e. have an empty list).  This list will
       be initialized to `None` before the translation step.

       FIXME: re-think aggregation / decomposition.  Does the above map to CU
       semantics?

     - *`Task.scheduled = dict()`*: This dictionary will map the aforementioned
       :class:`ComputeUnitDescription`s to pilot IDs -- the later dispatching is
       to submit the units to exactly those pilots.  Before scheduling, this
       dict is initialized to `None`.

     - *`Task.dispatched = dict()`*: This dictionary will, similarly to
       `Task.scheduled`, map the :class:`ComputeUnitDescription`s to pilot
       *instances* -- i.e. to those instances to which the respective CUs have
       been submitted to.  Before scheduling, this dict is initialized to
       `None`.  

    FIXME: it will be difficult to keep the different lists in sync, in
    particular on re-scheduling and re-translation.  It might be cleaner to move
    the scheduled/dispatched annotations into the CU descriptions.

    FIXME: do we need states for tasks?  Like: NEW, TRANSLATED, SCHEDULED,
    DISPATCHED, DONE?  Sounds useful on a first glance, but on re-schedule etc
    (see comments in workload manager), the states quickly become meaningless...
    But related to that will be the workload state inspection from the upper
    layers, and from the overlay manager (which better not plan pilots for
    completed tasks :P).
    """


    # --------------------------------------------------------------------------
    #
    def __init__ (self, description) :
        """
        Create a new workload element, aka Task, according to the description..

        Each new task is assigned a new ID.

        Later implementations may allow for an additional id parameter, 
        to reconnect to the thus identified task instance.  
        """

        # make this instance lockable
        self.lock = threading.RLock ()

        # initialize state
        tid   = ru.generate_id ('t.')
        descr = copy.deepcopy  (description)

        if  not 'tag' in descr :
            raise ValueError ("no 'tag' in TaskDescription")

        # initialize members to support workload transformations.
        self.translated = None
        self.scheduled  = None
        self.dispatched = None

        # set attribute interface properties
        self._attributes_extensible  (False)
        self._attributes_camelcasing (True)

        # register attributes
        self._attributes_register   ('id',          tid,       sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('tag',         descr.tag, sa.STRING, sa.SCALAR, sa.READONLY)
        self._attributes_register   ('description', descr,     sa.ANY,    sa.SCALAR, sa.READONLY)
         
        # FIXME: complete attribute list, dig attributes from description,
        # perform sanity checks


# ------------------------------------------------------------------------------
#
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

