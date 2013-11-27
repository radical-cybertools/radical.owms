
.. _chapter_plugin_writing

***************************
Writing SAGA-Python Plugins
***************************

.. note::

   This part of the SAGA-Python documentation is not for *users* of SAGA-Python,
   but rather for implementors of backend plugins.



.. _plugin_structure:

Plugin Structure
----------------

A Troy plugin is a Python module with well defined structure.  The
module must expose a class ``PLUGIN_CLASS``, and a dictionary ``PLUGIN_DESCRIPTION``, similar to this::

    PLUGIN_DESCRIPTION = {
        'type'        : 'planner',
        'name'        : 'bundles',
        'version'     : '0.1',
        'description' : 'This is the bundles planner.'
      }

    class PLUGIN_CLASS (object) :
        pass

What specific methods a plugin has to implement depends on the respective plugin
type -- simplest approach is to copy the respective default plugin and customize
the existing methods.


.. _plugin_registration:

Plugin Registration
-------------------

Troy plugins are automatically loaded once they ar installed in the correct
location -- i.e. once they are placed next to the existing plugins, with the
same naming scheme.



.. _plugin_state:

Plugin State
------------

The used plugin manager considers plugins to be singletons -- i.e. they will be
loaded only *once* per application lifetime, and any plugin invokation will use
the very same instance.  That makes it easy to maintain state over multiple
calls -- but plugin developers need to consciously shield invokations from side
effects of earlier calls.
  

.. _plugin_exceptions:

Exception Handling
------------------

Plugins should never to terminate an application -- while Troy does not prevent
intentional aborts (for example via `sys.exit()`), Troy will convert any
exceptions raised in the plugins into warnings, and will attempt to continue
operation.


.. _plugin_logging:

Plugin Logging
--------------

Plugins have access to the Troy logging system::

    troy.logger.info ("loading plugin my_plugin")


