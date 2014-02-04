
import time
import datetime
import troy

class TimedDuration (object) :

    def __init__ (self, timed, name, tag) :

        self.timed = timed
        self.name  = name
        self.tag   = tag

    def __enter__ (self) :

        self.start = self.timed.timed_duration_start (self.name, self.tag)


    def __exit__(self, t, v, tb) :

        timer  = self.timed.timed_duration_stop (self.name, self.tag)
        signature  = "%s (%s)" % (self.name, self.tag)
        troy._logger.info ('timed start    : %s : %s (UTC)' % (signature, self.start))
        troy._logger.info ('timed duration : %s : %s  sec'  % (signature, timer))



# ------------------------------------------------------------------------------
#
class Timed (object) :
    """
    keep track of time durations and events.
    This class is not thread safe.
    """

    def _timed_init (self) :

        if  not hasattr(self, '_timed_initialized') :
            self._timed_initialized = True
            self._timed_events      = dict()
            self._timed_durations   = dict()
            self._current_durations = dict()


    def timed_dump (self) :
        import pprint
        pprint.pprint (self._timed_events)
        pprint.pprint (self._timed_durations)


    def timed_duration_start (self, name, tag) :

        self._timed_init ()

        if  name in self._current_durations :
            raise RuntimeError ("cannot recursively time %s" % name)

        if  not name in self._timed_durations :
            self._timed_durations[name] = list()

        start   = datetime.datetime.utcnow ()
        namestr = "%s (%s)" % (name, tag)
        self._current_durations[name] = {
            'start' : start, 
            'name'  : namestr,
        }

        return start


    def timed_duration_stop (self, name, tag) :

        self._timed_init ()

        if  not name in self._current_durations :
            raise RuntimeError ("no timing for %s" % name)

        stop_timer = datetime.datetime.utcnow()
        timer      = (stop_timer - 
                      self._current_durations[name]['start']).total_seconds()

        self._current_durations[name]['stop']     = stop_timer
        self._current_durations[name]['duration'] = timer

        if  not name in self._timed_durations :
            self._timed_durations[name] = list()

        self._timed_durations[name].append (self._current_durations[name])
        del(self._current_durations[name])

        return timer



    def timed_event (self, name, tag) :

        self._timed_init ()

        if  not name in self._timed_events :
            self._timed_events[name] = list()

        timer = datetime.datetime.utcnow ()

        self._timed_events[name].append ({
            'time' : timer, 
            'tag'  : tag,
            })

        signature = "%s (%s)" % (name, tag)
        troy._logger.info ('timed event    : %s : %s (UTC)' % (signature, timer))


    def timed_method (self, name, tag, method, args=[], kwargs={}) :

        with TimedDuration (self, name, tag) :
            return method (*args, **kwargs)




# ------------------------------------------------------------------------------
#
def timeit (method) :

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

