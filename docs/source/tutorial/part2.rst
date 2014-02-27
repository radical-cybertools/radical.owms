.. _chapter_tutorial_02:

**********************
TROY Tutorial - Part 2
**********************

Once understood how simple TROY can make running a bag of task, the second
part of this tutorial will show you how TROY can be used programmatically
so to gain control over the many aspects involved into executing a
distributed application.

We will do two things: 

1. Construct our own workload in python (and therefore no longer need the workload file ``workload_gromacs.json``); and
2. experiment with different execution strategies.

Where the python file for Part 1 was very simple, ``tutorial_02.py`` is a
bit more elaborate (but still relatively simple!).

We will now walk through the code, not in a fully sequential order, but
we will touch upon every line eventually.

Starting a Session
==================

.. code-block:: python

    #
    # Configure session, get application config elements
    #
    configs  = sys.argv[1:]
    session  = troy.Session (configs)

Here we get the files that were passed as command line arguments and create
a TROY session with of it.  A :class:`troy.Session` is essentially a container
for TROY configuration settings, and for security contexts (which are not
discussed in this Tutorial).


Constructing a Workload
=======================

.. code-block:: python

    #
    # define tasks
    #
    task_descr = troy.TaskDescription()
    task_descr.executable  =  "%(mdrun)s"
    task_descr.cardinality =  "%(bag_size)s"
    task_descr.inputs      =  ["input/topol.tpr > topol.tpr"]
    task_descr.outputs     =  ["output/%(session_id)s_state.cpt.%(cardinal)s   < state.cpt",
                               "output/%(session_id)s_confout.gro.%(cardinal)s < confout.gro",
                               "output/%(session_id)s_ener.edr.%(cardinal)s    < ener.edr",
                               "output/%(session_id)s_traj.trr.%(cardinal)s    < traj.trr",
                               "output/%(session_id)s_md.log.%(cardinal)s      < md.log"]
    task_descr.working_directory = "%(home)s/troy_tutorial/troy_tutorial_02_%(cardinal)s/"

This snippet of code defines a task, that is semantically equivalent
to the task defined in ``workload_gromacs.json`` and although the syntax
is different, I'm sure you will see the similarity.

.. code-block:: python

    #
    # construct workload
    #
    workload = troy.Workload (session, task_descr)

With this call, the task description is associated with the session and a
workload handle is returned.  Some placeholders in the task description
attributes are replaced with the session configuration settings at this point,
others are only replaced later, during workload execution.


Managing Managers and Submission
================================

.. code-block:: python

    #
    # create managers within session (and its configs)
    #
    planner      = troy.Planner         (session)
    overlay_mgr  = troy.OverlayManager  (session)
    workload_mgr = troy.WorkloadManager (session)

The architecture of TROY <link> is very modular and consists of many
components that can be configured and used independently.
Here we create a Planner, Overlay Manager and Workload Manager using the
configuration that we had associated with the session.

.. code-block:: python

    #
    # execute workload
    #
    troy.execute_workload (workload, planner, overlay_mgr, workload_mgr,
                           strategy=strategy)

With the instantiated Workload, the configured Planner and Managers we
are now ready to execute the workload.

Execution of a Bag of Tasks (again)
===================================

The execution of the experiment is similar to part 1 of the tutorial, but
this time we don't pass the workload as a json file (as we define the
workload inside our application).

1. Remain in the directory ``tutorial``;
2. We can reuse the changes to ``config_application.json``;
3. Run the following commands:

.. code-block:: bash

	> export TROY_VERBOSE=INFO
	> python tutorial_02.py config_application.json config_troy.json

Sit back, relax, and enjoy the horses do the work!
The execution should look similar to that of earlier runs.

Execution Strategies
====================

You may remember that we ended Part 1 of this tutorial with a reference to
execution strategies.
There was one piece of code of Part 2 that we did not touch upon yet.

.. code-block:: python

    strategy = session.cfg.get ('troy_strategy', troy.AUTOMATIC)

The line above tries to get the strategy from the config. If it is not
set, it falls back to automatic setting.

Now that we have run the tutorial with the default 'Late Binding'
Execution Strategy we will change the strategy to 'Early Binding'
and investigate the effect.

We change the line displayed above into the one shown below by editing the file ``tutorial_02.py``:

.. code-block:: python

    strategy = 'basic_early_binding'

This is all that is required to in theory make drastic changes to the
(policy of) the execution.

Note that a change with the same effect could also have been made in
the configuration, specifically in ``config_troy.json`` (line 13).

.. code-block:: json

    "troy_strategy" : "basic_late_binding",


Now that we have changed the strategy, we can run the program again by:

.. code-block:: bash

    > python tutorial_02.py config_application.json config_troy.json
    
    