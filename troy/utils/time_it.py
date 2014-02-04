
import time
import datetime
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
    def timed_dump (self) :

        import pprint

        print '- events %d ---------------------'  % len(self.timed_events)
        pprint.pprint (self.timed_events)
        print '- durations %d ------------------'  % len(self.timed_durations)
      # for d in self.timed_durations :
      #     print ' ----- %d ' % len(d)
      #     pprint.pprint (d)
      #     print ' ----- '
        pprint.pprint (self.timed_durations)
        print '- current %d --------------------' % len(self._current_durations)
        pprint.pprint (self._current_durations)
        for component_id in self.timed_components :
            print '- component %s --------------' % component_id
            self.timed_components[component_id].timed_dump ()



    # --------------------------------------------------------------------------
    #
    def timed_component (self, component, component_id) :

        if  component_id in self.timed_components :
            # simply ignore
            pass
        else :
            self.timed_components[component_id] = component


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

