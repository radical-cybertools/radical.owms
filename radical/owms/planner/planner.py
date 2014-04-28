
__author__    = "RADICAL Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__   = "MIT"


import radical.owms
from   radical.owms import utils as ou
import radical.utils             as ru


# ------------------------------------------------------------------------------
#
class Planner (ou.Timed) :
    """
    The `Planner` class represents the upper layer, i.e. the application facing
    layer, of radical.owms, and thus hosts the API that ultimately will be used by end
    users.  That API allows to submit application workloads, and to monitor
    their execution progress.

    Internally, the planner will transform the given workload into an internal
    representation upon which the follow-up transformations of the
    :class:`WorkloadManager` class will operate.  It will further derive an
    overlay description suitable to run the workload, which downstream will be
    enacted by the :class:`OverlayManager`.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self, session) :
        """
        Create a new planner instance for this workload.

        Use the default planner plugin if not indicated otherwise
        """

        self.session = session
        self.id      = ru.generate_id ('planner.')

        ou.Timed.__init__            (self, 'radical.owms.Planner', self.id)
        self.session.timed_component (self, 'radical.owms.Planner', self.id)

        self._plugin_mgr = None
        self.plugins = dict ()


        # setup plugins from aruments
        #
        # We leave actual plugin initialization for later, in case a strategy
        # wants to alter / complete the plugin selection
        #
        cfg = session.get_config ('planner')

        self.plugins['strategy'] = cfg.get ('plugin_planner_strategy', radical.owms.AUTOMATIC)
        self.plugins['derive']   = cfg.get ('plugin_planner_derive',   radical.owms.AUTOMATIC)



    # --------------------------------------------------------------------------
    #
    def _init_plugins (self, workload=None) :

        if  self._plugin_mgr :
            # we don't allow changes once plugins are loaded and used, for state
            # consistency
            return

        # for each plugin set to 'AUTOMATIC', do the clever thing
        if  self.plugins['strategy'] == radical.owms.AUTOMATIC :
            self.plugins['strategy'] = 'late_binding'
        if  self.plugins['derive'  ] == radical.owms.AUTOMATIC :
            self.plugins['derive'  ] = 'maxcores'


        # load plugins
        self._plugin_mgr = ru.PluginManager ('radical.owms')
        self._strategy   = self._plugin_mgr.load ('planner_strategy', self.plugins['strategy'])
        self._derive     = self._plugin_mgr.load ('planner_derive',   self.plugins['derive'])

        if  not self._strategy :
            raise RuntimeError ("Could not load strategy overlay_derive plugin")

        if  not self._derive :
            raise RuntimeError ("Could not load planner overlay_derive plugin")

        self._strategy.init_plugin (self.session, 'planner')
        self._derive.init_plugin   (self.session, 'planner')

        radical.owms._logger.info ("initialized  planner (%s)" % self.plugins)


    # ------------------------------------------------------------------------------
    #
    def execute_workload (self, workload) :
        """
        Parse and execute a given workload, i.e., translate, bind and dispatch it,
        and then wait until its execution is completed.  For that to happen, we also
        need to plan, translate, schedule and dispatch an overlay, obviously...
        """
    
        overlay_mgr  = radical.owms.OverlayManager  (self.session)
        workload_mgr = radical.owms.WorkloadManager (self.session)

        workload_id  = None
    
        if  isinstance (workload, basestring) :
            if  workload.startswith ('wl.') :
                print 'is id %s' % workload
                workload_id = workload
            else :
                print 'is path %s' % workload
                # we assume this string points to a file containing a workload description 
                workload_id = workload_mgr.parse_workload (workload)
        elif  isinstance (workload, radical.owms.Workload) :
            print 'is instance %s' % workload
            workload_id = workload.id
        else :
            raise TypeError ("workload needs to be a radical.owms.Workload or a filename "
                             "pointing to a workload description, not '%s'" 
                             % type (workload))
    
        workload = radical.owms.WorkloadManager.get_workload (workload_id)

        self.timed_component (workload, 'radical.owms.Workload', workload_id)

        # Workload needs to be in DESCRIBED state to be expanded
        if  workload.state not in [radical.owms.DESCRIBED]:
            raise ValueError("workload '%s' not in DESCRIBED state" % workload.id)

        # make sure manager is initialized
        self._init_plugins (workload)

        # hand over control the selected strategy plugin, 
        # so it can do what it has to do.
        self._strategy.execute (workload_id, self, overlay_mgr, workload_mgr)


    # --------------------------------------------------------------------------
    #
    def derive_overlay (self, workload_id):
        """
        create overlay plan (description) from workload.

        Notes

        . Derive implies a workload. Does it make sense to think about a
          def describe_overlay() in which a workload is not provided? I am
          thinking about a stronger notion of 'early binding' in which pilots
          would be created preemptively. Do we see any use case for this?

        . I find the overloading of the term 'planner' confusing. self here is
          a planner. Then there is a private planner that is a planner plug-in
          that has a method with the same name (derive_overlay) of self. I
          believe this overloading hides a confusion about how we use plugins
          in the planner. Plugins should be specific, something that implement
          _alternative_ ways (i.e. algorithms) to solve a well-specified,
          unique, task within the overarching, composite action tat we call
          'planning'. See further comments on the bundles.

        . Do we have a state model for an overlay? I found the states listed
          in constants.py (shall we put them in something like states.py?). Do
          we use/set them in the planner?

        TODO

        . One of the reason to have a planner (Mark will have more to tell us
          soon about all the other functionalities) is to check that the
          workload as a whole makes sense given the available resources.
          Therefore, as part of the actions of the planner I would add both
          spatial and time dimensions of the overlay (as partially done in
          the overlay bundles plugin):
          - Max/Min amount of cores requires by the workload. If Max > of
            the cores available from the accessible resources, raise Exception.
          - Max/Min queing time required by the given workload. If Max > of
            the cores available from the accessible resources, raise Exception.
          - Max/Min degree of concurrency for the given workload - derived
            from the two previous parameters.

        """

        # Get the workload from the repo
        workload = radical.owms.WorkloadManager.get_workload(workload_id)

        self.timed_component (workload, 'radical.owms.Workload', workload.id)

        # Workload doesn't need to be EXPANDED, but if it is only DESCRIBED,
        # it can't be parametrized.
        if  workload.state not in [radical.owms.EXPANDED, radical.owms.DESCRIBED]:
            raise ValueError("workload '%s' not in DESCRIBED or EXPANDED " 
                             "state" % workload.id)
        elif workload.state is radical.owms.DESCRIBED and workload.parametrized:
            raise ValueError("Parametrized workload '%s' not EXPANDED yet."
                             % workload.id)

        # make sure manager is initialized
        self._init_plugins (workload)

        # derive overlay from workload
        overlay_descr = workload.timed_method ('derive_overlay', [], 
                                               self._derive.derive_overlay, [workload])

        # mark the origin of the overlay description
        overlay_descr['workload_id'] = workload_id

        # Only pass the ID back
        return overlay_descr


# ------------------------------------------------------------------------------

