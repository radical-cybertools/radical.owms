

import time
import troy
import pprint
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

       self.timed_event ('timed_create', id)


    # --------------------------------------------------------------------------
    #
    def timed_dump (self, indent='') :

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
    def timed_store (self, url) :

        # make sure this is only called for a troy.Session
        if  not self.timed_type == 'troy.Session' :
            raise TypeError ('timed_store works on a troy.Session, not %s' % self.timed_type)


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

                component  = self.timed_components[component_type][component_id]()
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

        troy._logger.info ('timed start    : %s %s : %s (UTC)' % (event, tags, start))

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

        troy._logger.info ('timed stop     : %s %s : %s (UTC)' % (event, tags, stop))
        troy._logger.info ('timed duration : %s %s : %s  sec'  % (event, tags, timer))

        return timer



    # --------------------------------------------------------------------------
    #
    def timed_event (self, event, tags, timer=None) :

        if  not isinstance (tags, list) :
            tags = [tags]

        if  not timer :
            timer = datetime.datetime.utcnow ()
        elif timer == -1 :
            timer = datetime.datetime.utcfromtimestamp (0)


        event_sig = "%s %s" % (event, tags)
        if  event_sig in self.timed_events_known :
            # don't do it twice
            return

        self.timed_events_known.append (event_sig)
        self.timed_events.append ({'time'  : timer, 
                                   'event' : event, 
                                   'tags'  : tags })

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

