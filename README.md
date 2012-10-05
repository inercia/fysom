
Description
===========

An improved state machine for Python

Usage
=====

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

Multiple src and to states for a single event
---------------------------------------------

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

Callbacks
---------

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

Asynchronous State Transitions
------------------------------

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

Internal State Transitions
--------------------------

You can trigger a state transition from withing the current state
transition. This state transition will be chained and will happen when
all callbacksfor current state are finished.

Example:
        def on_panic(e):
            print 'panic! ' + e.msg
            fsm.transition_to('black')

Initialization Options
----------------------

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

