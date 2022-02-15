# Micropython HFSM
Hierarchical Finite State Machine Implementation in Micro-Python

This project is a fork of https://github.com/debbynirwan/hfsm and aims to implement a HFSM in Micro Python.

Changes implemented to operate on Micro Python:
* Removed typing
* Adding dummy print based logger as logging isn't included in mp by default

Test on Micro Python version 1.18

## About
micropython-hfsm is a python library implementation of Hierarchical Finite State Machine that can be used in many fields such as 
robotics, video game, etc.

This library supports:
* Non-hierarchical FSM, a.k.a. FSM
* Multiple levels of FSM by adding child FSM to a state
* Propagating event to lower-level FSM

## Documents and Demos
Please read this article on Medium to understand HFSM: 
https://towardsdatascience.com/hierarchical-finite-state-machine-for-ai-acting-engine-9b24efc66f2

## Installation

Clone this repository and copy hfsm to your lib folder

## Example

### Simple Example
An FSM consists of states, events, and transitions. You can create simple versions:
```python
from hfsm import State, Event, StateMachine

state1 = State("state1")
state2 = State("state2")
event = Event("event")
fsm = StateMachine("fsm")

fsm.add_state(state1, initial_state=True)
fsm.add_state(state2)
fsm.add_event(event)
fsm.add_transition(state1, state2, event)

fsm.start("data")
fsm.trigger_event(event)
```

### Extending State Class
You can also extend the State class to create a user-defined State and use it in an FSM.
```python
from hfsm import State, Event, StateMachine

class IdleState(State):
    
    def __init__(self, name):
        super().__init__(name)
        self.on_entry(self.entry_callback)
        self.on_exit(self.exit_callback)
    
    def __call__(self, data):
        pass  # execute state's "do" action
    
    def entry_callback(self, data):
        pass
    
    def exit_callback(self, data):
        pass

initial = State("initial")
idle = IdleState("idle")
event = Event("event")
fsm = StateMachine("fsm")

fsm.add_state(initial, initial_state=True)
fsm.add_state(idle)
fsm.add_event(event)
fsm.add_transition(initial, idle, event)

fsm.start("data")
fsm.trigger_event(event)
```

### Hierarchical FSM
You can add a state machine as a child of a state.
```python
from hfsm import State, Event, StateMachine

class IdleState(State):
    
    def __init__(self, name, child_sm=None):
        super().__init__(name, child_sm)
        self.on_entry(self.entry_callback)
        self.on_exit(self.exit_callback)
    
    def __call__(self, data):
        pass  # execute state's "do" action
    
    def entry_callback(self, data):
        pass
    
    def exit_callback(self, data):
        pass

child_initial = State("initial")
child_idle = IdleState("idle")
child_event = Event("event")
child_fsm = StateMachine("fsm")

child_fsm.add_state(child_initial, initial_state=True)
child_fsm.add_state(child_idle)
child_fsm.add_event(child_event)
child_fsm.add_transition(child_initial, child_idle, child_event)

initial = State("initial")
idle = IdleState("idle", child_sm=child_fsm)
event = Event("event")
fsm = StateMachine("fsm")

fsm.add_state(initial, initial_state=True)
fsm.add_state(idle)
fsm.add_event(event)
fsm.add_transition(initial, idle, event)

fsm.start("data")
fsm.trigger_event(event, propagate=True)
```
