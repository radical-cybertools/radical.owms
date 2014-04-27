.. _chapter_tutorial_03:

******************************
RADICAL-OWMS Tutorial - Part 3
******************************

The second part of this tutorial illustrated how workloads can be created programmatically in RADICAL-OWMS, and it hinted at the existence of several manager classes: :class:`radical.owms.Planner`, :class:`radical.owms.WorkloadManager`, and :class:`radical.owms.OverlayManager`.  The third and last part of this tutorial will expand on the capabilities of those managers, and show how they provide very fine grained control over the execution strategy of the workload of a distributed application. If you look at `tutorial_03.py`, all  code beginning from line 50 downwards is basically replacing this single line from `tutorial_02.py`:

.. code-block:: python

    radical.owms.execute_workload (workload, planner, overlay_mgr, workload_mgr,
                           strategy=strategy)

You can run ``tutorial_03.py`` exactly like ``tutorial_03.py`` as it will accept the same config settings:

.. code-block:: bash

	export RADICAL_OWMS_VERBOSE=INFO
	python tutorial_03.py config_application.json config_radical_owms.json


Note that the code in `tutorial_03.py` is implementing exactly the execution
strategy which was previously encapsulated in the used strategy plugin.  

**At this point, please skim through that code (and comments!) to get an idea on the type of actions the execution strategy is comprised of.**

There are two major aspects to designing an execution strategy: the setup and
configuration of the RADICAL-OWMS manager classes, to make them fit for purpose; and the
order of calls on those manager classes, to express the actual strategy.  
This tutorial section will shortly describe both aspects, but cannot target for
complete coverage of the topic.  The reader shoul, however, be able to make use
of the RADICAL-OWMS Library Reference and Plugin Documentation once completing this
tutorial, for further guidelines and more in-depths information.

.. note:: Once an execution strategy is created, and it proves useful to you for
   repeated use, you may consider to put it into a **RADICAL-OWMS strategy plugin**.  That
   will make your application code simpler, and easier for others to use.


The RADICAL-OWMS Manager Classes
================================

RADICAL-OWMS features three different manager classes:

* :class:`radical.owms.Planner`: the Planner performs the following actions, among
  others:

  * **expand the workload:** expansion plugins can be used to transform a
    workload -- in our examples, we use the `cardinality` expander plugin to
    multiply the number of tasks, according to their cardinality.

  * **derive an overlay:** use plugins which will, by inspecting the workload,
    determine what type of overlay (size and structure) will be needed to
    execute that workload.

* :class:`radical.owms.WorkloadManager`: the WorkloadManager performs the following
  actions, among others:

  * **parse the workload:** parser plugins will create a :class:`radical.owms.Workload`
    instances just like the one created in the provious tutorial example.

  * **translate a workload:** use translator plugins to convert Tasks into pilot
    level compute units -- there is not necessarily a 1:1 mapping of tasks to
    units!

  * **schedule a workload:** scheduler plugins will bind the units to the
    overlay pilots assigned to them in the provious step.

* :class:`radical.owms.OverlayManager`: the OverlayManager performs the following
  actions, among others:

  * **translate an overlay:** use translator plugins to translate an overlay
    description (as created by the planner) into a set of pilot descriptions.

  * **schedule an overlay:** scheduler plugins will bind the pilots in an
    overlay to a specific resource, based on pilot properties and resource
    information.

  * **provision an overlay:** pilot backend plugins will submit the pilots to
    the respective target resources.



**Not that *all* activities are performed by plugins!**


Configuring RADICAL-OWMS Manager Classes
========================================

It may not come as a surprise for the careful tutorial attendee that we already
configures RADICAL-OWMS managers in part one and two.  Please revisit the
`config_radical_owms.json` config file -- it contains sections for each of the manager
classes.   That configuration is passed to the :class:`radical.owms.Session`
construction, and the thus configured session is passed to the manager classes
in turn:

.. code-block:: python

    # ------------------------------------------------------------------------------
    #
    # Configure session, get application config elements
    #
    configs  = sys.argv[1:]
    session  = radical.owms.Session (configs)
    
    ...
    
    # ------------------------------------------------------------------------------
    #
    # create managers within session (and its configs)
    #
    planner      = radical.owms.Planner         (session)
    overlay_mgr  = radical.owms.OverlayManager  (session)
    workload_mgr = radical.owms.WorkloadManager (session)

The managers thus receive their setup from the session, and the same
configurations we have used in the previous tutorial parts will apply.

There are two components to a manager configuration:

* specify the plugins to use, for each manager
* configure the plugins

The excerpt below from `config_radical_owms.json` shows those elements which are related
to the configuration of the :class:`radical.owms.WorkloadManager` class:

.. code-block:: python

   {
       "hosts"         : "pbs+ssh://sierra.futuregrid.org",
       "pilot_size"    : "4",
       "pilot_backend" : "radical.pilot",
   
       "overlay_manager"                : {
   
           # plugin selection for overlay manager
           "plugin_overlay_scheduler"   : "round_robin",
           "plugin_overlay_provisioner" : "%(pilot_backend)s",
   
           # plugin configuration for overlay manager
           "overlay_provisioner"        : {
               "bigjob"                 : {
                   "coordination_url"   : "redis://%(redis_passwd)s@gw68.quarry.iu.teragrid.org:6379"
               },
               "radical.pilot"          : {
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

* RADICAL-OWMS :ref:`chapter_configuration` 
  
* RADICAL-OWMS Manager Reference: :class:`radical.owms.Planner`, :class:`radical.owms.OverlayManager`
  and :class:`radical.owms.WorkloadManager`, 

* RADICAL-OWMS Plugin Reference: :ref:`chapter_plugin_reference`


The Usage of RADICAL-OWMS Manager Classes
=========================================

The second part of an execution strategy is the order in which the managers are
used.  For example, the overlay can be scheduled before the workload is
scheduled, or vice versa.  In fact, those two options are the main difference
between the early and late binding strategy plugins provided by RADICAL-OWMS!

In pseudo-code:

.. code-block:: python

   if 'binding' == 'late' :
   {
       ... `tutorial_03.py`
       overlay_mgr.schedule_overlay   (overlay)
       workload_mgr.schedule_workload (workload, overlay)
       ...
   }
   else :
   {
       ... 
       workload_mgr.schedule_workload (workload, overlay)
       overlay_mgr.schedule_overlay   (overlay)
       ...
   }

At this point, the interested user may want to change the `tutorial_03.py` from
an early binding scheme to a late binding scheme.  To do so:

* open `tutorial_03.py`
* search for 'NOTE' (around line 70)
* cut the section between the fat bars
* move it to *after* the workload scheduling part (around line 95 in the
  original version)
* save and run as before.

The log messages should now reflect the changed execution order.


