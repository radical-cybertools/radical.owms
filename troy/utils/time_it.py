

import time
import troy
import pymongo
import weakref
import datetime

import radical.utils as ru


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
    def __init__ (self, type, id) :

        self.timed_type            = type
        self.timed_id              = id
        self.timed_events          = list()
        self.timed_events_known    = list()
        self.timed_durations       = list()
        self.timed_durations_known = list()
        self.timed_components      = dict()
        self._timed_current        = dict()

        self.timed_event ('state', 'Created')


    # --------------------------------------------------------------------------
    #
    def timed_dump (self, _indent=None) :

        toplevel = False

        if  not _indent : 
            toplevel = True
            _indent  = ""

        print "%s  %s" % (_indent, self.timed_id)
        for e in self.timed_events :
            print "%s    event     %26s : %-15s : %s" % (_indent, e['time'], e['event'], e['tags'])
        for d in self.timed_durations :                       
            print "%s    duration  %25.2fs : %-15s : %s" % (_indent, d['duration'], d['event'], d['tags'])
        for ct in self.timed_components.keys() :
            print "%s    %s"  % (_indent, ct)
            for cid in self.timed_components[ct] :
                c = self.timed_components[ct][cid]()
                if  c :
                    print "%s      %s (%s)"  % (_indent, cid, type(c))
                    c.timed_dump (_indent+'  ')

        if  toplevel :
            print " === dumped %s ===" % self.timed_id


    # --------------------------------------------------------------------------
    #
    def timed_store (self, url) :

        # we also store the time of dump.  For a troy session
        # that gives, for example, the approximate lifetime of the session.
        self.timed_event ('state', 'Dumped')

        # get mongodb database details, and connect to it
        host, port, dbname, _, _ = ru.split_dburl (url)

        mongodb    = pymongo.MongoClient (host=host, port=port)
        database   = mongodb[dbname]

        collection = database[self.timed_id]

        # first store the session itself
        # build up an index of related components
        components = list()
        for ct in self.timed_components :
            components.append ({'type' : ct, 
                                'ids'  : self.timed_components[ct].keys ()})
        # store the timing and component info
        collection.save ({'_id'        : self.timed_id, 
                          'components' : components,
                          'events'     : self.timed_events, 
                          'durations'  : self.timed_durations})

        # then store all known components
        for component_type in self.timed_components :
            for component_id in self.timed_components[component_type] :

                component = self.timed_components[component_type][component_id]()

                if  component :
                    # weakref was valid
                    # build up an index of related components
                    components = list()
                    for ct in component.timed_components :
                        components.append ({'type' : ct, 
                                            'ids'  : component.timed_components[ct].keys ()})

                    # store the timing and component info
                    collection.save ({'_id'        : component.timed_id, 
                                      'type'       : component.timed_type, 
                                      'components' : components,
                                      'events'     : component.timed_events, 
                                      'durations'  : component.timed_durations})

        troy._logger.debug ('dumped timing to %s/%s' % (url, self.timed_id))



    # --------------------------------------------------------------------------
    #
    def timed_component (self, component, component_type, component_id) :

        if  not component_type in self.timed_components :
            self.timed_components[component_type] = dict()

        if  not component_id in self.timed_components[component_type] :
            self.timed_components[component_type][component_id] = weakref.ref (component)


    # --------------------------------------------------------------------------
    #
    def timed_duration_start (self, event, tags) :

        if  not isinstance (tags, list) :
            tags = [tags]

        if  event in self._timed_current and \
            self._timed_current[event]   :
            raise RuntimeError ("cannot recursively time %s" % event)

        start   = datetime.datetime.utcnow ()
        self._timed_current[event] = {
            'start' : start, 
            'event' : event,
            'tags'  : tags,
        }

        troy._logger.debug ('timed start    : %s %s : %s (UTC)' % (event, tags, start))

        return start


    # --------------------------------------------------------------------------
    #
    def timed_duration_stop (self, event, tags) :

        if  not isinstance (tags, list) :
            tags = [tags]

        if  not event in self._timed_current or \
            not self._timed_current[event]   :
            raise RuntimeError ("no timing for %s" % event)

        stop  = datetime.datetime.utcnow()
        timer = (stop - self._timed_current[event]['start']).total_seconds()

        self._timed_current[event]['stop']     = stop
        self._timed_current[event]['duration'] = timer

        self.timed_durations.append (self._timed_current[event])
        self._timed_current[event] = None

        troy._logger.debug ('timed stop     : %s %s : %s (UTC)' % (event, tags, stop))
        troy._logger.debug ('timed duration : %s %s : %s  sec'  % (event, tags, timer))

        return timer



    # --------------------------------------------------------------------------
    #
    def timed_event (self, event, name, tags=[], timer=None) :

        if  not isinstance (tags, list) :
            tags = [tags]

        if  not timer :
            timer = datetime.datetime.utcnow ()
        elif timer == -1 :
            timer = None


        event_sig = "%s [%s] %s" % (event, name, tags)
        if  event_sig in self.timed_events_known :
            # don't do it twice
            return

        self.timed_events_known.append (event_sig)
        self.timed_events.append ({'time'  : timer, 
                                   'event' : event, 
                                   'name'  : name,  
                                   'tags'  : tags })

        troy._logger.debug ('timed event [%s]   : %s : %s : %s' \
                         % (self.timed_id, event, name, tags))


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
        troy._logger.debug ('%30s : %6.2f sec' % (signature, timer))

        return result

    return timed

# ------------------------------------------------------------------------------

