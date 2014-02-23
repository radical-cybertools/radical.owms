
Part 2: Executing a Workload via Troy
========================================

The first tutorial will guide you through the use of the simplest possible Troy
program.  You will find the tutorial code, along with a workload description and
configuration files, under `FIXME: examples/tutorial/tutorial_01*`.

The used python program, in its entirety, is:


.. code-block:: python

    #!/usr/bin/env python
    
    import sys
    import troy
    
    troy.manage_workload (workload = sys.argv[1], 
                          config   = sys.argv[2:])
    

You can run this example with:


.. code-block:: bash

    > export TROY_VERBOSE=INFO
    > python tutorial_01_gromacs.py  tutorial_01_workload.json \
             tutorial_01_config.json tutorial_01_config_troy.json


From the log messages, you may be able to discern that Troy 

* parses the workload,
* expands it with some 'expand_cardinality' plugin, 
* derives a pilot overlay,
* schedules the pilot overlay to some backend resources, 
* submits those pilots,
* then schedules the workload tasks over the pilots, 
* stages the input file to the target resource, 
* submits the tasks for execution, 
* then waits for them to complete before 
* fetching the results back and 
* shutting the whole thing down.

Obviously, for this one-liner to trigger that activity chain meaningfully, there
must be a number of things going on, and this tutorial section will guide you
along in understanding what exactly Troy is doing here, and how to guide Troy in
that process.


Troy Workload Descriptions
----------------------------------------

Troy is designed to understand a multitude of workload descriptions -- but at
the moment is really only equipped to accept descriptions in its own JSON
format.  An exemplary description is provided with the tutorial code, as
`FIXME:examples/tutorial/tutorial_01_workload.json`


.. code-block:: python

    # cardinality: the task is run that many times
    # all string based values will be expanded with matching values from
    # the application config.  For example, if the application config sets 
    #     "bag_size"    : "10"
    # then 
    #     "cardinality" : "%(bag_size)s"
    # will expand to 
    #     "cardinality" : "10"
    
    {
      "tasks" : 
      [
        {
          "cardinality"       : "%(bag_size)s",
          "executable"        : "%(mdrun)s",
          "working_directory" : "%(home)s/troy_tutorial/troy_tutorial_01_%(cardinal)s/",
          "inputs"            : ["%(local_appdir)s/input/topol.tpr > topol.tpr"],
          "outputs"           : ["output/%(demo_id)s_state.cpt.%(cardinal)s   < state.cpt",
                                 "output/%(demo_id)s_confout.gro.%(cardinal)s < confout.gro",
                                 "output/%(demo_id)s_ener.edr.%(cardinal)s    < ener.edr",
                                 "output/%(demo_id)s_traj.trr.%(cardinal)s    < traj.trr",
                                 "output/%(demo_id)s_md.log.%(cardinal)s      < md.log"]
        }
      ]
    }

The basic structure of this workload is easy to grasp: it described a set of
tasks, each running the `mdrun` executable on an input files `topol.tpr`,
generating a set of output files.  The structure contains, however, a number of
placeholders, such as `%(mdrun)s` and `%(cardinal)s`.  The reason for that is
that the above description is resource independent -- it is at Troy's discretion
on what machine that `mdrun` executable will run.  As such, the exact path name
of the executable cannot be known in advance, and neither can things like
hostname, username, certain path elements, etc.  Those resource specific
placeholders are only replaced after the tasks got scheduled on a specific
resource (or more specific: in a specific pilot which runs on a specific
resource).

Other placeholders get expanded while Troy interprets the workload.  In
particular `%(cardinal)s` is set to the task number, so that for example the
output files can be staged back under a unique file name to avoid collisions.

Finally, there are placeholders which the user may want to change for every run.
In the example above this might be `%(bag_size)s`, which could be part of an
application config file.

And indeed, looking closer at the config files given as command line arguments,
we find exactly those information.  Here is the application config, which
contains parametrization and placeholder values for workload expansion and
transormations:

.. code-block:: python

    # tutorial_01_config.json
    {
        # variables we want to vary for each experiment run
        "steps"            : 256,
        "bag_size"         : 5,
        "local_appdir"     : "/home/winnetou/troy/examples/tutorial/",
    
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
        "strategy"      : "basic_late_binding",
    
    
        # troy plugin selection
        "plugin_strategy"                : "%(strategy)s",
    
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

