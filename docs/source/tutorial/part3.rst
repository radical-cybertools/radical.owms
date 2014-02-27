.. _chapter_tutorial_01:

**********************
TROY Tutorial - Part 3
**********************

The second part showed how workloads can be created programatically in TROY, and
it hinted at the existence of several manager classes: :class:`troy.Planner`,
:class:`troy.WorkloadManager`, and :class:`troy.OverlayManager`.  This last part
of the tutorial will expand on the capabilities of those managers, and show how
those provide very fine grained control over the execution strategy of the
application workload.  If you look at `tutorial_03.py`, all  code beginning from
line 50 downwards is basically replacing this single line from `tutorial_02.py`


.. note:: Once an execution strategy is created, and it proves useful to you for
repeated use, you may consider to put it into a **TROY strategy plugin**.  That
will make your application code simpler, and easier for others to use.


There are two major aspects to designing an execution strategy: the setup and
configuration of the TROY manager classes, to make them fit for purpose; and the
order of calls on those manager classes, to express the actual strategy.  
This tutorial section will shortly describe both aspects, but cannot target for
complete coverage of the topic.  The reader shoul, however, be able to make use
of the TROY Library Reference and Plugin Documentation once completing this
tutorial, for further guidelines and more in-depths information.


The Troy Manager Classes
================================




Configuring Troy Manager Classes
================================

It may not come as a surprise for the careful tutorial attendee that we already
configures TROY managers in part one and two.  Please revisit the
`config_troy.json` config file -- it contains sections for each of the manager
classes.   That configuration is passed to the :class:`troy.Session`
construction, and the thus configured session is passed to the manager classes
in turn:

.. code-block:: python

    # ------------------------------------------------------------------------------
    #
    # Configure session, get application config elements
    #
    configs  = sys.argv[1:]
    session  = troy.Session (configs)
    
    ...
    
    # ------------------------------------------------------------------------------
    #
    # create managers within session (and its configs)
    #
    planner      = troy.Planner         (session)
    overlay_mgr  = troy.OverlayManager  (session)
    workload_mgr = troy.WorkloadManager (session)

The managers thus receive their setup from the session, and the same
configurations we have used in the previous tutorial parts will apply.

There are two components to a manager configuration:

* specify the plugins to use, for each manager
* configure the plugins

The excerpt below from `config_troy.json` shows those elements which are related
to the configuration of the :class:`troy.WorkloadManager` class:

.. code-block:: python

   {
       "hosts"         : "pbs+ssh://sierra.futuregrid.org",
       "pilot_size"    : "4",
       "pilot_backend" : "sagapilot",
   
       "overlay_manager"                : {
   
           # plugin selection for overlay manager
           "plugin_overlay_scheduler"   : "round_robin",
           "plugin_overlay_provisioner" : "%(pilot_backend)s",
   
           # plugin configuration for overlay manager
           "overlay_provisioner"        : {
               "bigjob"                 : {
                   "coordination_url"   : "redis://%(redis_passwd)s@gw68.quarry.iu.teragrid.org:6379"
               },
               "sagapilot"              : {
                   "coordination_url"   : "mongodb://ec2-184-72-89-141.compute-1.amazonaws.com:27017/"
               }
           },docs/source
           "overlay_scheduler"          : {
               "round_robin"            : {
                   "resources"          : "%(hosts)s"
               }
           },
           "overlay_translator"         : {
               "max_pilot_size"         : {
                   "pilot_size"         : "%(pilot_size)s"
               }
           }
       }
   }

The same mechanism holds for all other managers, and for all plugin types.  For
further configuration details, please refer to:

* TROY :ref:`chapter_configuration` 
  
* TROY Manager Reference: :class:`troy.Planner`, :class:`troy.OverlayManager`
  and :class:`troy.WorkloadManager`, 

* TROY Plugin Reference: :ref:`chapter_plugin_reference`


The Usage of Troy Manager Classes
=================================

