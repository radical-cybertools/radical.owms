
__author__ = "TROY Development Team"
__copyright__ = "Copyright 2013, RADICAL"
__license__ = "MIT"


import radical.utils      as ru
import troy.utils         as tu
from   troy.constants import *
import troy


"""
Manages the pilot-based overlays for TROY.
"""


# -----------------------------------------------------------------------------
#
class OverlayManager (tu.Timed) :
    """
    Generates and instantiates an overlay. An overlay consists of pilot
    descriptions and instances.

    Capabilities provided:

    * Get information about resources [from ResourceInformation(Bundle)]:
      - Queues:
        . Name;
        . allowed walltime;
        . prediction on queuing time depending on the job size.
    * Get general information about workload: 
      - Total time required for its execution [from Planner];
      - total space required for its execution [from Planner]:
        . # of cores.
    * Get information about compute unit [from WorkloadManager]:
      - Time required;
      - Space required:
        . # of cores.
      - Grouping with other Units.
    * describe pilots.
    * Schedule pilots on resources.
    * Provision pilots on resources [by means of Provisioner].

    """


    # this map is used to translate between troy pilot IDs and native backend
    # IDs. 
    _pilot_id_map = dict ()

    # --------------------------------------------------------------------------
    #
    def __init__ (self, session     = None, 
                        translator  = AUTOMATIC,
                        scheduler   = AUTOMATIC,
                        provisioner = AUTOMATIC) :
        """
        Create a new overlay manager instance.

        Use default plugins if not otherwise indicated.  Note that the
        provisioner plugin is actually not owned by the OverlayManager, but by
        the pilots of the Overlay managed by the OverlayManager.
        """

        if  session : self.session = session
        else:         self.session = troy.Session ()


        # We leave actual plugin initialization for later, in case a strategy
        # wants to alter / complete the plugin selection

        self.plugins = dict ()
        self.plugins['translator']  = translator
        self.plugins['scheduler' ]  = scheduler
        self.plugins['provisioner'] = provisioner

        self._plugin_mgr = None

        self.id = ru.generate_id ('olm.')

        tu.Timed.__init__            (self, 'troy.OverlayManager', self.id)
        self.session.timed_component (self, 'troy.OverlayManager', self.id)


    # --------------------------------------------------------------------------
    #
    def _init_plugins (self, workload_mgr=None) :

        if  self._plugin_mgr :
            # we don't allow changes once plugins are loaded and used, for state
            # consistency.  If a workload_manager was given, warn for possible
            # configuration violation.
            if  workload_mgr :
                troy._logger.warning ("Ignore overlay_mgr re-initialization")
            return

        # for each plugin set to 'AUTOMATIC', do the clever thing
        #
        if  self.plugins['translator']  == AUTOMATIC :
            self.plugins['translator']  = 'max_pilot_size'
        if  self.plugins['scheduler' ]  == AUTOMATIC :
            self.plugins['scheduler' ]  = 'local'

        # if AUTOMATIC, try to match the provisioner plugin with the workload
        # dispatcher plugin
        if  self.plugins['provisioner']  == AUTOMATIC :
            if  workload_mgr :
                self.plugins['provisioner'] = workload_mgr.plugins['dispatcher']
        if  self.plugins['provisioner']  == AUTOMATIC :
            self.plugins['provisioner']  = 'local'

      # troy._logger.debug ("initializing overlay  manager (%s)" % self.plugins)

        self._plugin_mgr  = ru.PluginManager ('troy')

        # FIXME: error handling
        self._translator  = self._plugin_mgr.load ('overlay_translator',  self.plugins['translator' ])
        self._scheduler   = self._plugin_mgr.load ('overlay_scheduler',   self.plugins['scheduler'  ])
        self._provisioner = self._plugin_mgr.load ('overlay_provisioner', self.plugins['provisioner'])

        if  not self._translator  : raise RuntimeError ("Could not load translator  plugin")
        if  not self._scheduler   : raise RuntimeError ("Could not load scheduler   plugin")
        if  not self._provisioner : raise RuntimeError ("Could not load provisioner plugin")

        self._translator .init_plugin (self.session, 'overlay_manager')
        self._scheduler  .init_plugin (self.session, 'overlay_manager')
        self._provisioner.init_plugin (self.session, 'overlay_manager')

        troy._logger.info ("initialized  overlay manager (%s)" % self.plugins)


    # --------------------------------------------------------------------------
    #
    @classmethod
    def register_overlay (cls, overlay) :
        ru.Registry.register (overlay)


    # --------------------------------------------------------------------------
    #
    @classmethod
    def unregister_overlay (cls, overlay_id) :
        ru.Registry.unregister (overlay_id)


    # --------------------------------------------------------------------------
    #
    @classmethod
    def native_id_to_pilot_id (cls, native_id) :

        for troy_id in cls._pilot_id_map :
            if  native_id == cls._pilot_id_map[troy_id] :
                return troy_id

        return None


    # --------------------------------------------------------------------------
    #
    @classmethod
    def pilot_id_to_native_id (cls, pilot_id, native_id=None) :

        # FIXME: this is not threadsafe.
        # FIXME: load from disk on first call

        if  native_id :

            # register id
            if  pilot_id in cls._pilot_id_map :
                raise ValueError ("Cannot register that pilot id -- already known")
            cls._pilot_id_map[pilot_id] = native_id
            # FIXME: dump to disk

        else :

            # lookup id
            if  not pilot_id in cls._pilot_id_map :
                raise ValueError ("no such pilot known '%s'" % pilot_id)
            return cls._pilot_id_map[pilot_id]


    # --------------------------------------------------------------------------
    #
    @classmethod
    def get_overlay (cls, overlay_id, _manager=None) :
        """
        We don't care about locking at this point -- so we simply release the
        overlay immediately...
        """
        if  not overlay_id :
            return None

        if  not overlay_id.startswith ('ol.') :
            raise ValueError ("'%s' does not represent a overlay" % overlay_id)

        overlay = ru.Registry.acquire (overlay_id, ru.READONLY)
        ru.Registry.release (overlay_id)

        if  _manager :
            _manager.timed_component (overlay, 'troy.Overlay', overlay_id)

        return overlay


    # --------------------------------------------------------------------------
    #
    def translate_overlay(self, overlay_id):
        """
        Inspect backend resources, and select suitable resources for the
        overlay.

        See the documentation of the :class:`Overlay` class on how exactly the
        scheduler changes and/or annotates the given overlay.
        """

        overlay = self.get_overlay (overlay_id)

        self.timed_component (overlay, 'troy.Overlay', overlay.id)

        # make sure the overlay is 'fresh', so we can translate it it
        if  overlay.state != DESCRIBED :
            raise ValueError ("overlay '%s' not in DESCRIBED state" % overlay.id)

        # make sure manager is initialized
        self._init_plugins ()

        # hand over control over overlay to the scheduler plugin, so it can do
        # what it has to do.
        overlay.timed_method ('translate', [], 
                              self._translator.translate, [overlay])

        # mark overlay as 'translated'
        overlay.state = TRANSLATED


    # --------------------------------------------------------------------------
    #
    def schedule_overlay (self, overlay_id) :
        """
        Inspect backend resources, and select suitable resources for the
        overlay.

        See the documentation of the :class:`Overlay` class on how exactly the
        scheduler changes and/or annotates the given overlay.
        """

        overlay = self.get_overlay (overlay_id)

        self.timed_component (overlay, 'troy.Overlay', overlay.id)

        # make sure the overlay is 'fresh', so we can schedule it
        if  overlay.state != TRANSLATED :
            raise ValueError ("overlay '%s' not in TRANSLATED state" % overlay.id)

        # make sure manager is initialized
        self._init_plugins ()

        # hand over control over overlay to the scheduler plugin, so it can do
        # what it has to do.
        overlay.timed_method ('schedule', [], 
                              self._scheduler.schedule, [overlay])

        # mark overlay as 'scheduled'
        overlay.state = SCHEDULED


    # --------------------------------------------------------------------------
    #
    def provision_overlay (self, overlay_id) :
        """
        Create pilot instances for each pilot described in the overlay.

        See the documentation of the :class:`Overlay` class on how exactly the
        scheduler changes and/or annotates the given overlay.
        """

        overlay = self.get_overlay (overlay_id)

        self.timed_component (overlay, 'troy.Overlay', overlay.id)

        # make sure the overlay is 'fresh', so we can schedule it
        if  overlay.state != SCHEDULED :
            raise ValueError ("overlay '%s' not in SCHEDULED state" % overlay.id)

        # make sure manager is initialized
        self._init_plugins ()

        # now that the pilots are bound and about to be dispatched, we can fix the
        # resource placeholders in the pilot descriptions
        for pilot_id, pilot in overlay.pilots.iteritems() :

            # get troys idea of resource configuration
            resource_cfg = self.session.get_resource_config (pilot.resource)

            # and merge it conservatively into the pilot config
            ru.dict_merge (pilot.description, resource_cfg, policy='preserve')

            # expand values with resource config settings
            for key, val in pilot.description.iteritems() :
                if  isinstance (val, basestring) :
                    pilot.description[key] = val % resource_cfg

            import pprint
            pprint.pprint (pilot.description)


        # hand over control over overlay to the provisioner plugin, so it can do
        # what it has to do.
        overlay.timed_method ('provision', [], 
                              self._provisioner.provision, [overlay])

        # mark overlay as 'provisioned'
        overlay.state = PROVISIONED


    # --------------------------------------------------------------------------
    #
    def cancel_overlay (self, overlay_id) :
        """
        cancel the referenced overlay, i.e. all its pilots
        """

        overlay = self.get_overlay (overlay_id)

        self.timed_component (overlay, 'troy.Overlay', overlay.id)

        overlay.timed_method ('cancel', [], overlay.cancel)
        overlay.cancel ()


# -----------------------------------------------------------------------------

