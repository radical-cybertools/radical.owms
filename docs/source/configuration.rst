
.. _chapter_configuration:

*************
Configuration
*************

In order to use TROY, the user needs to: 

* Copy or write a set of configuration files.
* Add some mandatory configuration parameters to one or more of these files.

This chapter describes the configuration mechanism of TROY and offers sample files with both **mandatory** and **optional** configuration parameters.

.. note:: Due to its flexibility, composability, and large set of capabilities, TROY depends on a number of configuration parameters. Such dependency is planned to be progressively reduced along the TROY development roadmap.


Configuration Mechanism
=======================
TROY pulls config settings from different locations, in this order:

1. any config files in `$(HOME)/.troy/`
2. any files or directory pointed to by `$TROY_CONFIG`
3. any configuration passed to a class:`troy.Session` constructor

Configuration files are expected to be in `JSON` format -- Python-like comments are allowed though.  When passing settings to a `troy.Session`, one can pass a list of configuration locations (files or directories), or directly a Python dictionary with the respective settings.

Additionally, TROY uses a number of internal configurations, be it for default
configuration, or for details of some known and frequently used target resources (mostly on FutureGrid and XSEDE).


Required Configuration Settings
===============================
In order to create a pilot overlay on some target resources, TROY needs to know some details about those resources, such as `username`, `queue` to be used, etc. While some of those information are stored in an internal TROY configuration file, others need to be provided by the user.  A typical configuration file for a local machine and some FutureGrid machines may look like:

.. code-block:: python

    # $HOME/.troy/resource.json
    {
        "hosts"                     : "pbs+ssh://sierra.futuregrid.org,ssh://lakota",

        # augment the TROY resource configuration
        "resources"                 : {
    
            # add a local resource for testing -- it does not use any queuing
            # system
            "lakota"                : {
                "type"              : ["ssh"],
                "home"              : "/home/%(username)s/"
                "username"          : "surehand"
            },
    
            # change some user specific variable for existing TROY config entries
            "*.futuregrid.org"      : {
                "username"          : "winnetou"
            },
            "sierra.futuregrid.org" : {
                "queue"             : "batch"
            }
        }
    }

.. note:: You may use **placeholders** in configuration strings. For example:  `"/home/%(username)s/"`. Placeholders can refer to top-level settings in other configuration sources, or to configuration settings for specific resources. For example, the `hosts` setting is later referenced in the `resources` settings for the overlay scheduler plugin. For more details, see below.

.. note:: You may also use **wildcards** to specify settings for classes of resources. For example: `"*.futuregrid.org"`.  Wildcards are only evaluated for resource config sections.

Beyond providing information about the target resources, TROY may also require
users to provide settings for the pilot backends. Both the backends that are currently supported - i.e., `sagapilot` and `BigJob` - require, for example, a coordination URL. Further, TROY needs to know what target resources are considered eligible for use.

The example configuration section below shows how to pass those settings to
respective TROY plugins. Note again the use of placeholders.

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

.. note:: These settings should be sufficient to run the examples in the TROY tutorial. Beyond that, the rest of this Chapter provides details on additional settings for TROY and its plugins.

Referencing Settings in Workloads
=================================



Additional Configuration Settings
=================================
There are two main types of configurations in TROY: Those which apply to TROY
plugins, and those which apply to TROY internals, such as the selection of
plugins. The config snippet below shows the complete set of plugin selection
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


The list of available plugins cab found 'FIXME: here`. For each plugin, the
respective configuration section is structured as follow:

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

Here a concrete example:

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

You will recognize this structure from the Section `Required Configuration Settings`. The list of configurable options is for each plugin documented on the respective plugin page, see 'FIXME: here`.