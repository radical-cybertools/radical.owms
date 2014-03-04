
__author__ = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__ = "MIT"


import threading

import radical.utils  as ru
import troy.utils     as tu
from   troy.constants import *
import troy


# ------------------------------------------------------------------------------
#
class Planner (tu.Timed) :
    """
    The `Planner` class represents the upper layer, i.e. the application facing
    layer, of Troy, and thus hosts the API that ultimately will be used by end
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

        tu.Timed.__init__            (self, 'troy.Planner', self.id)
        self.session.timed_component (self, 'troy.Planner', self.id)

        self._plugin_mgr = None
        self.plugins = dict ()


        # setup plugins from aruments
        #
        # We leave actual plugin initialization for later, in case a strategy
        # wants to alter / complete the plugin selection
        #
        cfg = session.get_config ('planner')

        self.plugins['strategy'] = cfg.get ('plugin_planner_strategy', AUTOMATIC)
        self.plugins['derive']   = cfg.get ('plugin_planner_derive',   AUTOMATIC)



    # --------------------------------------------------------------------------
    #
    def _init_plugins (self, workload=None) :

        if  self._plugin_mgr :
            # we don't allow changes once plugins are loaded and used, for state
            # consistency
            return

      # troy._logger.debug ("initializing planner (%s)" % self.plugins)

        # for each plugin set to 'AUTOMATIC', do the clever thing
        if  self.plugins['strategy'] == AUTOMATIC :
            self.plugins['strategy'] = 'basic_late_binding'
        if  self.plugins['derive'  ] == AUTOMATIC :
            self.plugins['derive'  ] = 'maxcores'


        # load plugins
        self._plugin_mgr = ru.PluginManager ('troy')
        self._strategy   = self._plugin_mgr.load ('strategy', self.plugins['strategy'])
        self._derive     = self._plugin_mgr.load ('derive',   self.plugins['derive'])

        if  not self._strategy :
            raise RuntimeError ("Could not load strategy overlay_derive plugin")

        if  not self._derive :
            raise RuntimeError ("Could not load planner overlay_derive plugin")

        self._strategy.init_plugin (self.session, 'planner')
        self._derive.init_plugin   (self.session, 'planner')

        troy._logger.info ("initialized  planner (%s)" % self.plugins)


    # ------------------------------------------------------------------------------
    #
    def execute_workload (workload) :
        """
        Parse and execute a given workload, i.e., translate, bind and dispatch it,
        and then wait until its execution is completed.  For that to happen, we also
        need to plan, translate, schedule and dispatch an overlay, obviously...
        """
    
        overlay_mgr  = troy.OverlayManager  (self.session)
        workload_mgr = troy.WorkloadManager (self.session)

        workload_id  = None
    
        if  isinstance (workload, basestring) :
            if  workload.beginswith ('wl.') :
                workload_id = workload
            else :
                # we assume this string points to a file containing a workload description 
                parsed_workload = workload_mgr.parse_workload (workload)
        elif  isinstance (workload, troy.Workload) :
            workload_id = workload.id
        else :
            raise TypeError ("workload needs to be a troy.Workload or a filename "
                             "pointing to a workload description, not '%s'" 
                             % type (workload))
    
        # hand over control the selected strategy plugin, 
        # so it can do what it has to do.
        strategy.execute (workload_id, self, overlay_mgr, workload_mgr)


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
        workload = troy.WorkloadManager.get_workload(workload_id)

        self.timed_component (workload, 'troy.Workload', workload.id)

        # Workload doesn't need to be EXPANDED, but if it is only DESCRIBED,
        # it can't be parametrized.
        if  workload.state not in [EXPANDED, DESCRIBED]:
            raise ValueError("workload '%s' not in DESCRIBED or EXPANDED "
                             "state" % workload.id)
        elif workload.state is DESCRIBED and workload.parametrized:
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

