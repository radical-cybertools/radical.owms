.. _chapter_tutorial_01:

**********************
RADICAL-OWMS Tutorial - Part 1
**********************

The first part of this RADICAL-OWMS tutorial will teach you how to use
RADICAL-OWMS to write
a very simple application that executes a bag of tasks on a remote DCI. You will
go through three phases, starting from installing RADICAL-OWMS, then configuring it, and
finally running your application.

Execution of a Bag of Tasks
===========================
We start by looking at **what** RADICAL-OWMS can do for you, then we move on and see
**how** it does it. In order to run an application with say 10 tasks, each
running an instance of gromacs with an input file and producing some output
files, do the following:

1. Use your preferred editor to edit the file ``config_application.json``;
2. Enter your username in where you see: ``"username" : "<your_user_name>"``;
3. Enter 10 in: ``"bag_size" : <number_of_tasks>``;
4. Save the file;
5. Run the following commands:

.. code-block:: bash

	export RADICAL_OWMS_VERBOSE=INFO
	python tutorial_01.py workload_gromacs.json config_application.json config_radical_owms.json

The output of your distributed application is in the directory ``output``:

.. code-block:: bash

	ls -l output/

Now, to understand why this is cool, let's have a look at the code we have executed:

.. code-block:: python

    #!/usr/bin/env python

    # tutorial_01.py

    import sys
    import radical.owms

    radical.owms.manage_workload (workload = sys.argv[1],
                          config   = sys.argv[2:])

That is all it needs! From the log messages, you may be able to discern that
RADICAL-OWMS had done the following for you:

1.  Parse the workload;
2.  expand it with some 'expand_cardinality' plugin;
3.  derive a pilot overlay;
4.  schedule the pilot overlay to some backend resources;
5.  submit those pilots;
6.  schedule the workload tasks over the pilots;
7.  stage the input file to the target resource;
8.  submit the tasks for execution;
9.  wait for them to complete;
10. fetche the results back; and
11. shut the whole thing down.

Obviously, for this one-liner to trigger that activity chain meaningfully, there
must be a number of things going on. If you need just to run a bag of task this
is everything you need to know, and you can stop the tutorial here. 

However, if you want to do more, if you need to decide how many pilots to
run, to programmatically define your application and workload, to tweak the
degree of concurrency of your tasks, or to choose alternative scheduling
algorithms both for your tasks and for your pilots, possibly across multiple
DCIs for the same workload, then keep reading :)

Configuration
=============
RADICAL-OWMS offers a powerful configuration subsystem that allows for the users to
leverage the many functionalities it implements. Most of the configuration
parameters are set to sensible defaults so that the user has to set explicitly
only those parameters for which no defaults can be provided:

* credentials and login names on the targeted DCIs; and
* parameters relative to the workload she wants to execute.

Detailed documentation about the RADICAL-OWMS configuration subsystem can be found
:ref:`chapter_configuration`. For this tutorial, the RADICAL-OWMS development team
crated a set of configuration files that you will be able to edit whether and
when required. The configuration files are:

* ``workload_gromacs.json``: Contains an abstracted description of a workload
  for an application of type "bag of tasks".  
  
* ``config_application.json``: Contains the parameters required by the bag of
  task application to run on a (set of) remote DCI. Currently RADICAL-OWMS supports only
  bag of tasks but in a near future it will support more complex distributed
  applications as, for example, different types of ensembles or workflow-based
  applications.

* ``config_radical_owms.json``: Contains those configuration parameters that are
  specific to RADICAL-OWMS and its execution.

Here a detailed analysis of each configuration file.

Workload Descriptions
---------------------
RADICAL-OWMS is designed to eventually understand a multitude of workload descriptions
- but at the moment it is equipped to accept descriptions in its own JSON
format. An exemplary description is provided with the workload configuration
files used the this part of the tutorial:

.. code-block:: python

    # ------------------------------------------------------------------------------
    #
    # workload_gromacs.json
    #
    # This file defines a simple gromacs workload, i.e. a number of gromacs tasks
    # with input and output staging.
    #
    # cardinality: 
    #     the task is run that many times all string based values will be expanded
    #     with matching values from the application config.  
    #
    #     For example, if the application config sets 
    #         "bag_size"    : 10
    #     then 
    #         "cardinality" : "%(bag_size)s"
    #     will expand to 
    #         "cardinality" : "10"
    #
    #     The placeholder "%(cardinal)s" will expand to the sequential task number
    #     (0..9 in our example).
    #
    # Other placeholders will be expanded depending on the resource the task will
    # land on, such as "%(username)s", "%(mdrun)s" or "%(home)".   Note that the
    # mdrun location is set in 'config_application.json'.
    #
    # Note that the output data will be stored in `output`, relative to pwd.
    # 

    {
      "tasks" :
      [
        {
          "cardinality"       : "%(bag_size)s",
          "executable"        : "%(mdrun)s",
          "working_directory" : "%(home)s/radical_owms_tutorial/radical_owms_tutorial_01_%(cardinal)s/",
          "inputs"            : ["input/topol.tpr > topol.tpr"],
          "outputs"           : ["output/%(demo_id)s_state.cpt.%(cardinal)s   < state.cpt",
                                 "output/%(demo_id)s_confout.gro.%(cardinal)s < confout.gro",
                                 "output/%(demo_id)s_ener.edr.%(cardinal)s    < ener.edr",
                                 "output/%(demo_id)s_traj.trr.%(cardinal)s    < traj.trr",
                                 "output/%(demo_id)s_md.log.%(cardinal)s      < md.log"]
        }
      ]
    }

The basic structure of this workload is as follow:

1. A set of tasks are described;
2. each task runs the ``mdrun`` executable on an input files ``topol.tpr``; and
3. a set of output files is generated.

A number of placeholders are used:

* ``%(bag_size)s``: Holds the number of tasks of the workload that RADICAL-OWMS will execute.
* ``%(home)s``: Holds the home directory on the targeted DCI.
* ``%(mdrun)s``: Holds the mdrun executable location, for the target resource.
* ``%(cardinal)s``: a ``magic`` variable set by the planner plugin ``plugin_planner_expand_cardinal.py`` that holds the index of the iterator over the list of tasks.

Thanks to these placeholders, the description of the workload can become
resource independent. RADICAL-OWMS's is given discretion on replacing each placeholder
with an appropriate value, depending on the execution context. For example,
``%(home)s`` will be replaced with the appropriate home directory depending on
the remote machine on which the workload will be executed.

Each placeholder is interpreted by RADICAL-OWMS at different stages, depending on the
context in which they are needed:

* ``%(home)s`` and ``%(mdrun)s`` are resource-specific placeholders, expanded
  after the tasks have been scheduled on a specific resource (i.e., on
  a specific pilot which runs on a specific resource).

* ``%(cardinal)s`` is a planner-specific placeholder, therefore expanded while
  RADICAL-OWMS interprets the workload. In particular, ``%(cardinal)s`` is set to the
  task number, so that, for example, the output files can be staged back under
  a unique file name to avoid collisions.

* ``%(bag_size)s`` is an application-specific placeholder, expanded immediately
  by RADICAL-OWMS upon workload parsing, in order to produce its internal workload
  description. In the example above, ``%(bag_size)s`` could be part of an
  application config file and the users may want to change it for every run.

The values for these placeholders are set on the application configuration file.
This is just a convention because, as explained in :ref:`chapter_configuration`,
all the configuration directives can be written into a single file, or split
into arbitrary files.

Application Configuration
-------------------------
The application configuration file contains parametrization and placeholder
values for workload expansion and transformations:

.. code-block:: python

    # config_application.json

    {
        # variables we want to vary for each experiment run.
        "steps"            : 256,
        "bag_size"         : 5,

        # build up a unique session id from those variables.  This
        # ID will be used by try to identify this run.
        "session_id"       : "gromacs_%(steps)s_%(bag_size)s",

        # We add some additional, app specific information to the
        # RADICAL-OWMS resource configuration, so that we can use placeholder
        # like '%(mdrun)s' in our workload descriptions.
        # This section *must* be named `resources`.
        "resources" : {
            # Mark installed gromacs on futuregrid
            "*.futuregrid.org" : {
                "username"     : "merzky",
                "mdrun"        : "/N/u/marksant/bin/mdrun"
            },

            # stampede has mdrun in path (add 'module load gromacs' in bashrc)
            "stampede.*" : {
                "home"         : "/home1/01083/tg803521",
                "username"     : "tg803521",
                "mdrun"        : "mdrun"
            },

            # localhost has mdrun in path
            "localhost" : {
                "mdrun"        : "mdrun"
            }
        }
    }

RADICAL-OWMS Configuration
--------------------------

We also have a RADICAL-OWMS configuration file, which selects the plugins RADICAL-OWMS is using
to execute the workload, and also configures those plugins. For the simple
configuration settings we use, the RADICAL-OWMS configuration structure looks almost
empty though:

.. code-block:: python

    # config_radical_owms.json

    {
    	# frequently changing variables
    	"hosts"                 : "pbs+ssh://sierra.futuregrid.org",
        "pilot_size"            : "4",
        "concurrency"           : "100",
        "pilot_backend"         : "radical.pilot",
        "radical_owms_strategy" : "late_binding",


        # radical.owms plugin selection
        "plugin_strategy"                : "%(radical_owms_strategy)s",

        "planner"                        : {
            "plugin_planner_expand"      : "cardinal",
            "plugin_planner_derive"      : "maxcores",
        },
        "workload_manager"               : {
            "plugin_workload_translator" : "direct",
            "plugin_workload_scheduler"  : "round_robin",
            "plugin_workload_dispatcher" : "%(pilot_backend)s"
        },
        "overlay_manager"                : {
            "plugin_overlay_translator"  : "max_pilot_size",
            "plugin_overlay_scheduler"   : "round_robin",
            "plugin_overlay_provisioner" : "%(pilot_backend)s"
        },

        # plugin configurations
        "planner"                        : {
            "derive"                     : {
                "concurrent"             : {
                    "concurrency"        : "%(concurrency)s"
                }
            }
        },

        "overlay_manager"                : {
            "overlay_provisioner"        : {
                "bigjob"                 : {
                    "coordination_url"   : "redis://%(redis_passwd)s@gw68.quarry.iu.teragrid.org:6379"
                },
                "radical.pilot"          : {
                    "coordination_url"   : "mongodb://ec2-184-72-89-141.compute-1.amazonaws.com:27017/"
                }
            },
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
        },

        "workload_manager"             : {
            "workload_dispatcher"      : {
                "bigjob"               : {
                    "coordination_url" : "redis://%(redis_passwd)s@gw68.quarry.iu.teragrid.org:6379"
                },
                "radical.pilot"        : {
                    "coordination_url" : "mongodb://ec2-184-72-89-141.compute-1.amazonaws.com:27017/"
                }
            }
        }
    }

Remember that you can move config settings which you do not consider specific to
an application into the ``$HOME/.radical.owms/`` directory, so that they are
automatically picked up on every RADICAL-OWMS run.  For example, the above setting would
benefit from a config file like

.. code-block:: python

    # $HOME/.radical.owms/config_passwords.json

    {
        "redis_passwd" : "secret-password"
    }

if you want to run the examples over BigJob pilots -- that password is then
expanded in the settings for the bigjob coordination URL, and will not be shared
if you pass your config files to other users, or if you push them into a code
repository.

.. You may have noted that we set a RADICAL-OWMS **strategy** plugin, to the value
   ``basic_late_binding``:  that is the point where we want to look deeper into
   RADICAL-OWMS's internals in the next tutorial section :ref:`chapter_tutorial_02`.

We will look deeper into RADICAL-OWMS's internals in the next tutorial section
:ref:`chapter_tutorial_02`.

