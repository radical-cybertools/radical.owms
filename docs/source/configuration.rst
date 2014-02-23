.. _chapter_configuration:

********************************************************************************
Configuration
********************************************************************************

Troy is designed to become a very flexible and powerful software, which operates
wich provides a diverse set of algorithms and strategies to execute very diverse
workloads over very diverse types of infrastructures.  While Troy will
eventually grow into a state where it can gather all required informations and
settings on its own, it is at the moment dependent on a number of external
configuration settings.

This chapter describes various types of settings.  The total amount may look
daunting to the new users -- but in fact the number of *required* settings is
fairly small.   So this chapter will first focus on the required settings to get
the tutorial examples working, and will then cover the complete set of Troy
configuration settings in more detail.

Before describing the setting options, however, we will shortly descrive the
different ways settings can be communicated to Troy.


Configuration Mechanism
========================================

Troy pulls config settings from different locations, in this order

* any config files in `$(HOME)/.troy/`
* any files or directory pointed to by `$TROY_CONFIG`
* any configuration passed to a class:`troy.Session` constructor

Configuration files are expected to be in `JSON` format -- python like comments
are allowed though.  When passing settings to a `troy.Session`, one can pass
a list of configuration locations (files or directories), or directly a Python
dictionary with the respective settings.

Additionally, Troy uses a number of internal configurations, be it for default
configuration, or for details of some known and frequently used target resourecs
(motly on FutureGrid and XSEDE).


Required Configuration Settings
========================================

In order to create a pilot overlay on some target resources, Troy needs to know
some details about those resources, such as `username`, `queue` to be used, etc.
While some of those information are stored in an internal troy configuration
file, others need to be provided by the user.  A typical configuration file for
a local machine and some futuregrid machines may look like:

.. code-block:: python

    # $HOME/troy/resource.json
    {
        "hosts"                     : "pbs+ssh://sierra.futuregrid.org,ssh://lakota",

        # augment the troy resource configuration
        "resources"                 : {
    
            # add a local resource for testing -- it does not use any queuing
            # system
            "lakota"                : {
                "type"              : ["ssh"],
                "home"              : "/home/%(username)s/"
                "username"          : "surehand"
            },
    
            # change some user specific variable for existing troy config entries
            "*.futuregrid.org"      : {
                "username"          : "winnetou"
            },
            "sierra.futuregrid.org" : {
                "queue"             : "batch"
            }
        }
    }


.. note:: You may use some placeholders in configuration strings, like above in
          `"/home/%(username)s/"` -- those placeholders can refer to top-level 
          settings in other configuration sources, or from settings sections for 
          specific resources.  For example, the `hosts` setting is later
          referenced in the `resources` settings for the overlay scheduler
          plugin, see below.

.. note:: You may also use wildcards to specify settings for classes of resources, such as
          used above for `"*.futuregrid.org"`.  Wildcards are only evaluated for resource
          config sections.


Beyond providing information about the target resources, Troy may also require
users to provide settings for the used pilot backends.  Both currently supported
backends, `saga-pilot` and `bigjob`, require for example a coordination URL.
Further, Troy needs to know what target resources are considered eligible for
use.

The example configuration section below shows how to pass those settings to
respective Troy plugins.  Note again the use of placeholders.

.. code-block:: python

    # $HOME/.troy/pilots.config
    {
        "redis_password"               : "secret",
        "bigjob_coordination_url"      : "redis://%(redis_passwd)s-REdIS@gw68.quarry.iu.teragrid.org:6379",
        "sagapilot_coordination_url"   : "mongodb://ec2-184-72-89-141.compute-1.amazonaws.com:27017/",

        "workload_manager"             : {
            "workload_dispatcher"      : {
                "bigjob"               : {
                    "coordination_url" : "%(bigjob_coordination_url)s"
                },
                "sagapilot"            : {
                    "coordination_url" : "%(sagapilot_coordination_url)s"
                }
            }
        },

        "overlay_manager"              : {
            "overlay_provisioner"      : {
                "bigjob"               : {
                    "coordination_url" : "%(bigjob_coordination_url)s"
                },
                "sagapilot"            : {
                    "coordination_url" : "%(sagapilot_coordination_url)s"
                }
            },
            "overlay_scheduler"        : {
                "round_robin"          : {
                    "resources"        : "%(hosts)s"
                }
            }
        }
    }


.. note:: Those settings should be sufficient to run the Troy tutorial
          examples.  Beyond that this chapter provides details on additional 
          settings fro Troy and Troy plugins below.


Referencing Settings in Workloads
========================================




Additional Configuration Settings
========================================

There are two main types of configurations in Troy: those which apply to Troy
plugins, and those which apply to Troy internals, such as the selection of
plugins.  The config snippet below shows the complete set of plugin selection
settings, with their default values:


.. code-block:: python
     
    {
        "plugin_strategy"                : "basic_late_binding",

        "planner"                        : {
            "plugin_planner_derive"      : "maxcores",
            "plugin_planner_expand"      : "noop"
        },

        "workload_manager"               : {
            "plugin_workload_translator" : "direct",
            "plugin_workload_scheduler"  : "round_robin",
            "plugin_workload_dispatcher" : "local"
        },

        "overlay_manager"                : {
            "plugin_overlay_translator"  : "max_pilot_size",
            "plugin_overlay_scheduler"   : "round_robin",
            "plugin_overlay_provisioner" : "local"
        }
    }


The list of available plugins is available 'FIXME: here`; for each plugin, the
respective configuration section is structured like:

.. code-block:: python
     
    {
        "plugin_scope"                   : {
            "plugin_type"                : {
                "plugin_name"            : {
                    "plugin_setting"     : "value"
                }
            }
        }
    }



or as illustrated by example:

.. code-block:: python
     
    {
        "workload_manager"               : {
            "plugin_workload_dispatcher" : {
                "sagapilot"              : {
                    "coordination_url"   : "redis://localhost"
                }
            }
        }
    }

You will recognize this structure from the `Required Configuration Settings`
section.  The list of configurable options is for each plugin documented on the
respective plugin page, see 'FIXME: here`.


