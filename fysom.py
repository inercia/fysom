#
# fysom.py - pYthOn Finite State Machine - this is a port of Jake
#            Gordon's javascript-state-machine to python
#            https://github.com/jakesgordon/javascript-state-machine
#
# Copyright (C) 2011 Mansour <mansour@oxplot.com>, Jake Gordon and other
#                    contributors
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


"""
USAGE

from state_machine import FiniteStateMachine

fsm = FiniteStateMachine({
  'initial': 'green',
  'events': [
    {'name': 'warn',  'src': 'green',  'dst': 'yellow'},
    {'name': 'panic', 'src': 'yellow', 'dst': 'red'},
    {'name': 'calm',  'src': 'red',    'dst': 'yellow'},
    {'name': 'clear', 'src': 'yellow', 'dst': 'green'}
  ]
})

... will create an object with a method for each event:

  - fsm.warn()  - transition from 'green'  to 'yellow'
  - fsm.panic() - transition from 'yellow' to 'red'
  - fsm.calm()  - transition from 'red'    to 'yellow'
  - fsm.clear() - transition from 'yellow' to 'green'

along with the following members:

  - fsm.current    - contains the current state
  - fsm.isstate(s) - return True if state s is the current state
  - fsm.can(e)     - return True if event e can be fired in the current
                     state
  - fsm.cannot(e)  - return True if event s cannot be fired in the
                     current state

MULTIPLE SRC AND TO STATES FOR A SINGLE EVENT

fsm = FiniteStateMachine({
  'initial': 'hungry',
  'events': [
    {'name': 'eat',  'src': 'hungry',    'dst': 'satisfied'},
    {'name': 'eat',  'src': 'satisfied', 'dst': 'full'},
    {'name': 'eat',  'src': 'full',      'dst': 'sick'},
    {'name': 'rest', 'src': ['hungry', 'satisfied', 'full', 'sick'],
                                         'dst': 'hungry'}
  ]
})

This example will create an object with 2 event methods:

  - fsm.eat()
  - fsm.rest()

The rest event will always transition to the hungry state, while the eat
event will transition to a state that is dependent on the current state.

NOTE the rest event in the above example can also be specified as
multiple events with the same name if you prefer the verbose approach.

CALLBACKS

4 callbacks are available if your state machine has methods using the
following naming conventions:

  - on_before_<EVENT> - fired before the <EVENT>
  - on_leave_<STATE>  - fired when leaving the old <STATE>
  - on_enter_<STATE>  - fired when entering the new <STATE>
  - on_after_<EVENT>  - fired after the <EVENT>

You can affect the event in 2 ways:

  - return False from an on_before_event_ handler to cancel the event.
  - return False from an on_leave_state_ handler to perform an
    asynchronous state transition (see next section)

For convenience, the 2 most useful callbacks can be shortened:

  - on_<EVENT> - convenience shorthand for on_after_<EVENT>
  - on_<STATE> - convenience shorthand for on_enter_<STATE>

In addition, a generic on_changestate() callback can be used to call a
single function for all state changes.

All callbacks will be passed one argument 'e' which is an object with
following attributes:

  - fsm   FiniteStateMachine object calling the callback
  - event Event name
  - src   Source state
  - dst   Destination state
  - (any other keyword arguments you passed into the original event
     method)

Note that when you call an event, only one instance of 'e' argument is
created and passed to all 4 callbacks. This allows you to preserve data
across a state transition by storing it in 'e'. It also allows you to
shoot yourself in the foot if you're not careful.

Callbacks can be specified when the state machine is first created:

def on_panic(e): print 'panic! ' + e.msg
def on_calm(e): print 'thanks to ' + e.msg
def on_green(e): print 'green'
def on_yellow(e): print 'yellow'
def on_red(e): print 'red'

fsm = FiniteStateMachine({
  'initial': 'green',
  'events': [
    {'name': 'warn',  'src': 'green',  'dst': 'yellow'},
    {'name': 'panic', 'src': 'yellow', 'dst': 'red'},
    {'name': 'panic', 'src': 'green',  'dst': 'red'},
    {'name': 'calm',  'src': 'red',    'dst': 'yellow'},
    {'name': 'clear', 'src': 'yellow', 'dst': 'green'}
  ],
  'callbacks': {
    'on_panic':  onpanic,
    'on_calm':   oncalm,
    'on_green':  ongreen,
    'on_yellow': onyellow,
    'on_red':    onred
  }
})

fsm.panic(msg='killer bees')
fsm.calm(msg='sedatives in the honey pots')

Additionally, they can be added and removed from the state machine at
any time:

def printstatechange(e):
  print 'event: %s, src: %s, dst: %s' % (e.event, e.src, e.dst)

del fsm.ongreen
del fsm.onyellow
del fsm.onred
fsm.onchangestate = printstatechange

ASYNCHRONOUS STATE TRANSITIONS

Sometimes, you need to execute some asynchronous code during a state
transition and ensure the new state is not entered until you code has
completed.

A good example of this is when you run a background thread to download
something as result of an event. You only want to transition into the
new state after the download is complete.

You can return False from your on_leave__state_ handler and the state
machine will be put on hold until you are ready to trigger the
transition using transition() method.

Example: TODO

INITIALIZATION OPTIONS

How the state machine should initialize can depend on your application
requirements, so the library provides a number of simple options.

By default, if you don't specify any initial state, the state machine
will be in the 'none' state and you would need to provide an event to
take it out of this state:

fsm = FiniteStateMachine({
  'events': [
    {'name': 'startup', 'src': 'none',  'dst': 'green'},
    {'name': 'panic',   'src': 'green', 'dst': 'red'},
    {'name': 'calm',    'src': 'red',   'dst': 'green'},
  ]
})
print fsm.current # "none"
fsm.startup()
print fsm.current # "green"

If you specifiy the name of you initial event (as in all the earlier
examples), then an implicit 'startup' event will be created for you and
fired when the state machine is constructed:

fsm = FiniteStateMachine({
  'initial': 'green',
  'events': [
    {'name': 'panic', 'src': 'green', 'dst': 'red'},
    {'name': 'calm',  'src': 'red',   'dst': 'green'},
  ]
})
print fsm.current # "green"

If your object already has a startup method, you can use a different
name for the initial event:

fsm = FiniteStateMachine({
  'initial': {'state': 'green', 'event': 'init'},
  'events': [
    {'name': 'panic', 'src': 'green', 'dst': 'red'},
    {'name': 'calm',  'src': 'red',   'dst': 'green'},
  ]
})
print fsm.current # "green"

Finally, if you want to wait to call the initiall state transition
event until a later date, you can defer it:

fsm = FiniteStateMachine({
  'initial': {'state': 'green', 'event': 'init', 'defer': True},
  'events': [
    {'name': 'panic', 'src': 'green', 'dst': 'red'},
    {'name': 'calm',  'src': 'red',   'dst': 'green'},
  ]
})
print fsm.current # "none"
fsm.init()
print fsm.current # "green"

Of course, we have now come full circle, this last example pretty much
functions the same as the first example in this section where you simply
define your own startup event.

So you have a number of choices available to you when initializing your
state machine.

"""

__author__ = 'Mansour'
__copyright__ = 'Copyright 2011, Mansour and Jake Gordon'
__credits__ = ['Mansour', 'Jake Gordon']
__license__ = 'MIT'
__version__ = '1.0'
__maintainer__ = 'Mansour'
__email__ = 'mansour@oxplot.com'



class StateError(Exception):
    pass

class FiniteStateMachine(object):

    def __init__(self, cfg):
        """
        Initialize the state machine with a diccionary
        """
        self._apply(cfg)

    def isstate(self, state):
        """
        Return TRUE if the current state matches the argumnet provided
        """
        return self.current == state

    def can(self, event):
        """
        Return TRUE if the machine can receive an event
        """
        return event in self._map and self.current in self._map[event] \
            and not hasattr(self, 'transition')

    def cannot(self, event):
        return not self.can(event)

    def _apply(self, cfg):
        init = cfg['initial'] if 'initial' in cfg else None
        if not isinstance(init, dict):
            init = {'state': init}
        events = cfg['events'] if 'events' in cfg else []
        callbacks = cfg['callbacks'] if 'callbacks' in cfg else {}
        tmap = {}
        self._map = tmap

        def add(e):
            src = e['src'] if isinstance(e['src'], (list, tuple)) else [e['src']]
            if e['name'] not in tmap:
                tmap[e['name']] = {}
            
            try:
                for s in iter(src):
                    tmap[e['name']][s] = e['dst']
            except TypeError, te:
                tmap[e['name']][src] = e['dst']

        if init:
            if 'event' not in init:
                init['event'] = 'startup'
            add({'name': init['event'], 'src': None, 'dst': init['state']})

        for e in events:
            add(e)

        for name in tmap:
            setattr(self, name, self._build_event(name))

        for name in callbacks:
            setattr(self, name, callbacks[name])

        self.current        = None
        self.current_dst    = None
        
        if init and 'defer' not in init:
            getattr(self, init['event'])()


    def transition_to(self, dst, event = None):
        """
        Preoduces an internal transition to another state
        
        You can call this method from a on_* callback if you want to make the machine
        to move to another state when _all_callbacks for current state have been processed.
        """
        setattr(self, 'next_state', self._build_event(event     = event,
                                                      src_state = self.current_dst,
                                                      dst_state = dst))
        return True
        
    def _build_event(self, event, src_state = None, dst_state = None):

        def fn(**kwargs):
            if hasattr(self, 'transition'):
                #if not hasattr(self, 'next_state'):
                #    self.transition_to(dst, event = None)
                #else:
                raise StateError("event %s inappropriate because previous"
                                 " transition did not complete" % event)
                
            if event and self.current:
                if not self.can(event):
                    raise StateError("event %s inappropriate in current state"
                                     " %s" % (event, self.current))

            if src_state is None:   src = self.current
            else:                   src = src_state
            
            if dst_state is None:   dst = self._map[event][src]
            else:                   dst = dst_state

            ## build the 'e' object that we will pass to the on_* callbacks
            class _e_obj(object): pass
            
            e = _e_obj()
            e.fsm, e.event, e.src, e.dst = self, event, src, dst
            for k in kwargs:
                setattr(e, k, kwargs[k])

            ## invoke all the callbacks
            if self.current != dst:    
                self.current_dst = dst
                
                if self._before_event(e) == False:  return False
                
                def _tran():
                    delattr(self, 'transition')
                    self.current = dst
                    self._enter_state(e)
                    self._change_state(e)
                    self._after_event(e)

                    if hasattr(self, 'next_state'):
                        next_state = getattr(self, 'next_state')
                        delattr(self, 'next_state')
                        next_state()
                        
                    return True
                
                self.transition = _tran
            
            if self._leave_state(e) != False:
                if hasattr(self, 'transition'):
                    return self.transition()
            return False

        return fn

    def _before_event(self, e):
        fnname = 'on_before_' + str(e.event).lower()
        if hasattr(self, fnname):
            return getattr(self, fnname)(e)

    def _after_event(self, e):
        for fnname in ['on_after_' + str(e.event).lower(), 'on_' + str(e.event).lower()]:
            if hasattr(self, fnname):
                return getattr(self, fnname)(e)

    def _leave_state(self, e):
        fnname = 'on_leave_' + str(e.src).lower()
        if hasattr(self, fnname):
            return getattr(self, fnname)(e)

    def _enter_state(self, e):
        for fnname in ['on_enter_' + str(e.dst).lower(), 'on_' + str(e.dst).lower()]:
            if hasattr(self, fnname):
                return getattr(self, fnname)(e)

    def _change_state(self, e):
        fnname = 'on_change_state'
        if hasattr(self, fnname):
            return getattr(self, fnname)(e)

if __name__ == '__main__':
    pass
