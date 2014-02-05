
import time
import datetime
import weakref
import troy

# ------------------------------------------------------------------------------
#
class TimedDuration (object) :
    """
    This context managed class supports the exception safe timing via with
    clauses, like::

        with TimedDuration (self, event, tags) :
            return method (*args, **kwargs)

    This mechanism is used in Timed.timed_method()

    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self, timed, event, tags) :

        if  not isinstance (tags, list) :
            tags = [tags]

        self.timed = timed
        self.event = event
        self.tags  = tags


    # --------------------------------------------------------------------------
    #
    def __enter__ (self) :

        self.timed.timed_duration_start (self.event, self.tags)


    # --------------------------------------------------------------------------
    #
    def __exit__(self, t, v, tb) :

        self.timed.timed_duration_stop (self.event, self.tags)


# ------------------------------------------------------------------------------
#
class Timed (object) :
    """
    Keep track of time durations and events.
    This class is not thread safe: multiple threads concurrently timing the same
    method will conflict.

    The following two invocations are semantically equivalent::

        # using the timed_method wrapper
        self.timed_method ('workload_manager', 
                           ['schedule()', workload.id, overlay.id], 
                           self._scheduler.schedule, [workload, overlay])

        # using explicit duration timing
        self.timed_duration_start ('workload_manager', 
                                   ['schedule()', workload.id, overlay.id])
        self._scheduler.schedule  (workload, overlay)
        self.timed_duration_stop  ('workload_manager', 
                                   ['schedule()', workload.id, overlay.id])

    The `timed_method` version, however, is guarded against exceptions from the
    called method, so should be preferred in production code.
    """

    # --------------------------------------------------------------------------
    #
    def __init__ (self, id) :

       self._current_durations = dict()
       self.timed_events       = list()
       self.timed_durations    = list()
       self.timed_components   = dict()
       self.timed_id           = id

       self.timed_event (id, 'creation')


    # --------------------------------------------------------------------------
    #
    def timed_dump (self, indent='') :

        import pprint

        print "%s= %s" % (indent, self.timed_id)
        for e in self.timed_events :
            print "%s    event    %s %s" % (indent, e['event'], e['tags'])
        for d in self.timed_durations :                       
            print "%s    duration %s %s" % (indent, d['event'], d['tags'])
        for ct in self.timed_components.keys() :
            print "%s    %s"  % (indent, ct)
            for c in self.timed_components[ct] :
                print "%s      %s"  % (indent, c)


    # --------------------------------------------------------------------------
    #
    def timed_component (self, component_type, component_id, component) :

        if  not component_type in self.timed_components :
            self.timed_components[component_type] = dict()

        if  not component_id in self.timed_components[component_type] :
            self.timed_components[component_type][component_id] = weakref.ref (component)


    # --------------------------------------------------------------------------
    #
    def timed_duration_start (self, event, tags) :

        if  not isinstance (tags, list) :
            tags = [tags]

        if  event in self._current_durations and \
            self._current_durations[event]   :
            raise RuntimeError ("cannot recursively time %s" % event)

        start   = datetime.datetime.utcnow ()
        self._current_durations[event] = {
            'start' : start, 
            'event' : event,
            'tags'  : tags,
        }

        troy._logger.info ('timed start    : %s %s : %s (UTC)' % (event, tags, start))

        return start


    # --------------------------------------------------------------------------
    #
    def timed_duration_stop (self, event, tags) :

        if  not isinstance (tags, list) :
            tags = [tags]

        if  not event in self._current_durations or \
            not self._current_durations[event]   :
            raise RuntimeError ("no timing for %s" % event)

        stop  = datetime.datetime.utcnow()
        timer = (stop - self._current_durations[event]['start']).total_seconds()

        self._current_durations[event]['stop']     = stop
        self._current_durations[event]['duration'] = timer

        self.timed_durations.append (self._current_durations[event])
        self._current_durations[event] = None

        troy._logger.info ('timed stop     : %s %s : %s (UTC)' % (event, tags, stop))
        troy._logger.info ('timed duration : %s %s : %s  sec'  % (event, tags, timer))

        return timer



    # --------------------------------------------------------------------------
    #
    def timed_event (self, event, tags) :

        if  not isinstance (tags, list) :
            tags = [tags]

        timer = datetime.datetime.utcnow ()

        self.timed_events.append ({
            'time'  : timer, 
            'event' : event, 
            'tags'  : tags,
            })

        troy._logger.info ('timed event [%s]   : %s : %s (UTC)' % (self.timed_id, event, tags))


    # --------------------------------------------------------------------------
    #
    def timed_method (self, event, tags, method, args=[], kwargs={}) :

        with TimedDuration (self, event, tags) :
            return method (*args, **kwargs)




# ------------------------------------------------------------------------------
#
def timeit (method) :

    # --------------------------------------------------------------------------
    #
    def timed (*args, **kwargs) :

        start  = time.time ()
        result = method (*args, **kwargs)
        stop   = time.time ()
        timer  = stop - start

        signature = "%s (%s, %s) " % (method.__name__, args, kwargs)
        troy._logger.info ('%30s : %6.2f sec' % (signature, timer))

        return result

    return timed

# ------------------------------------------------------------------------------

