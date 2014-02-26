.. _chapter_tutorial_01:

****************
TROY Tutorial - Part 1
****************

The first part of this TROY tutorial will teach you how to use TROY to write a very simple application that executes a bag of tasks on a remote DCI. You will go through three phases, starting from installing TROY, then configuring it, and finally running your application.

Installation
============
Please follow the instructions to install TROY from GitHub at :ref:`installation_for_github`.

Configuration
=============
TROY offers a powerful configuration subsystem that allows the users to leverage all the functionalities it exposes. Said that, most of the configuration parameters are set to sensible defaults so that the user has to set explicitly only those parameters for which no defaults can be provided - e.g. credentials and login names on the targeted DCIs or parameters relative to the workload she wants to execute.

Detailed documentation about TROY configuration subsystem can be found :ref:`chapter_configuration`. For this tutorial we 


Execution of a Bag of Tasks
===========================

  You will find the tutorial code, along with a workload description and configuration files, under `tutorial/tutorial_01*`.

The used python program, in its entirety, is:


.. code-block:: python

    #!/usr/bin/env python
    
    import sys
    import troy
    
    troy.manage_workload (workload = sys.argv[1], 
                          config   = sys.argv[2:])
    
Edit the configuration file `config_application.json` and add your username on *.futuregrid.org:

    "*.futuregrid.org" : {
        "username"     : "<your_username>",

You can run this example with:

.. code-block:: bash

    > export TROY_VERBOSE=INFO
    > python tutorial_01.py workload_gromacs.json config_application.json config_troy.json

From the log messages, you may be able to discern that TROY:

1.  Parses the workload;
2.  expands it with some 'expand_cardinality' plugin; 
3.  derives a pilot overlay;
4.  schedules the pilot overlay to some backend resources; 
5.  submits those pilots;
6.  schedules the workload tasks over the pilots; 
7.  stages the input file to the target resource;
8.  submits the tasks for execution;
9.  waits for them to complete; 
10. fetches the results back; and 
11. shuts the whole thing down.

Obviously, for this one-liner to trigger that activity chain meaningfully, there must be a number of things going on, and this tutorial section will guide you along in understanding what exactly TROY is doing here, and, in case, how to guide TROY in that process.


Troy Workload Descriptions
--------------------------

Troy is designed to understand a multitude of workload descriptions - but at
the moment it is really only equipped to accept descriptions in its own JSON
format. An exemplary description is provided with the tutorial code, in
`tutorial/workload_gromacs.json`:

.. code-block:: python

    # cardinality: the task is run that many times all string based values 
    # will be expanded with matching values from the application config. 
    # For example, if the application config sets: 
    #     "bag_size"    : "10"
    # then: 
    #     "cardinality" : "%(bag_size)s"
    # it will expand to:
    #     "cardinality" : "10"
    # 
    # Note that the output data will be stored in `output`, relative to pwd.
    
    {
      "tasks" : 
      [
        {
          "cardinality"       : "%(bag_size)s",
          "executable"        : "%(mdrun)s",
          "working_directory" : "%(home)s/troy_tutorial/troy_tutorial_01_%(cardinal)s/",
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
2. each task runs the `mdrun` executable on an input files `topol.tpr`; and
3. a set of output files is generated.  

A number of placeholders are used:

* `%(bag_size)s`: Holds the number of tasks of the workload that TROY will execute.
* `%(home)s`: Holds the home directory on the targeted DCI.
* `%(mdrun)s`: Holds the mdrun executable location. 
* `%(cardinal)s`: a `magic` variable set by the planner plugin `plugin_planner_expand_cardinal.py` that holds the index of the iterator over the list of tasks. 

Thanks to these placeholders, the description of the workload can become resource independent. TROY's is given discretion on replacing each placeholder with an appropriate value, depending on the execution context. For example, `%(home)s` will be replaced with the appropriate home directory depending on the remote machine on which the workload will be executed.

Each placeholder is interpreted by TROY at different stages, depending on the context in which they are needed: 

* `%(home)s` and `%(mdrun)s` are resource-specific placeholders, expanded after the tasks have been scheduled on a specific resource (i.e., on a specific pilot which runs on a specific resource).
* `%(cardinal)s` is a planner-specific placeholder, therefore expanded while TROY interprets the workload. In particular, `%(cardinal)s` is set to the task number, so that, for example, the output files can be staged back under a unique file name to avoid collisions.
* `%(bag_size)s` is an application-specific placeholder, expanded immediately by TROY in order to produce its internal workload description. In the example above, `%(bag_size)s` could be part of an application config file and the users may want to change it for every run.

As documented in The values for these placeholders can be passed to TROY within one or more config files  in dedicated configuration files:

* Resource specific placeholders 

And indeed, looking closer at the config files given as command line arguments, we find exactly those information.  Here is the application config, which contains parametrization and placeholder values for workload expansion and transformations:

.. code-block:: python

    # tutorial_01_config.json
    {
        # variables we want to vary for each experiment run.  The application
        dir should point to *your* local copy of the Troy tutorial.
        "steps"            : 256,
        "bag_size"         : 5,
    
        # build up a unique session id from those variables.  This 
        # ID will be used by try to identify this run
        "session_id"       : "glomacs_%(steps)s_%(bag_size)s",
    
    
        # We add some additional, app specific information to the 
        # troy resource config, so that we can use placeholder
        # like '%(mdrun)s' in our workload descriptions.
        # This section *must* be named `resources`.
        "resources" : {
            # Ole Surehand installed gromacs on futuregrid
            "*.futuregrid.org" : {
                "mdrun"        : "/N/u/surehand/bin/mdrun"
            },
            # stampede has mdrun in path (add 'module load gromacs' in bashrc)
            "stampede.*" : {
                "mdrun"        : "mdrun"
            },
            # localhost has mdrun in path
            "localhost" : {
                "mdrun"        : "mdrun"
            }
        }
    }


And also, we have a troy configuration file, which selects the plugins Troy is
using to execute the workload, and also configures those plugins.  For the
simple configuration settings we use, the troy configuration structure looks
almost empty though:

.. code-block:: python

    # tutorial_01_config_troy.json
    {
        # frequently changing variables
        "hosts"         : "pbs+ssh://sierra.futuregrid.org",
        "pilot_size"    : "8",
        "concurrency"   : "100",
        "pilot_backend" : "sagapilot",
        "troy_strategy" : "basic_late_binding",
    
    
        # troy plugin selection
        "plugin_strategy"                : "%(troy_strategy)s",
    
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
                    "coordination_url"   : "redis://%(redis_passwd)s-REdIS@gw68.quarry.iu.teragrid.org:6379"
                },
                "sagapilot"              : {
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
                "sagapilot"            : {
                    "coordination_url" : "mongodb://ec2-184-72-89-141.compute-1.amazonaws.com:27017/"
                }
            }
        }
    }

Remember that you can move config settings which you do not consider specific to
an application into the `$HOME/.troy/` directory, so that they are automatically
picked up on every troy run,

You may have noted that we set a Troy **strategy** plugin, to the value
`basic_late_binding`.  It is at that point were we want to look deeper into
Troy's internals in the next tutorial section `FIXME: ref`.

