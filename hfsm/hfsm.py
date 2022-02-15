"""Hierarchical Finite State Machine

Description:
    HFSM (Hierarchical Finite State Machine) implements full feature of HFSM.

License:
    Copyright 2020 Debby Nirwan

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
try:
    import logging
    log = logging.getLogger(__name__)
except ImportError:
    class logging:
        def critical(self, entry):
            print('CRITICAL: ' + entry)
        def error(self, entry):
            print('ERROR: ' + entry)
        def warning(self, entry):
            print('WARNING: ' + entry)
        def info(self, entry):
            print('INFO: ' + entry)
        def debug(self, entry):
            print('DEBUG: ' + entry)
    log = logging()


class State(object):

    def __init__(self, name, child_sm=None):
        self._name = name
        self._entry_callbacks = []
        self._exit_callbacks = []
        self._child_state_machine = child_sm
        self._parent_state_machine = None

    def __repr__(self):
        return f"State={self._name}"

    def __eq__(self, other):
        if other.name == self._name:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __call__(self, data):
        pass

    def on_entry(self, callback):
        self._entry_callbacks.append(callback)

    def on_exit(self, callback):
        self._exit_callbacks.append(callback)

    def set_child_sm(self, child_sm):
        if not isinstance(child_sm, StateMachine):
            raise TypeError("child_sm must be the type of StateMachine")
        if self._parent_state_machine and self._parent_state_machine == \
                child_sm:
            raise ValueError("child_sm and parent_sm must be different")
        self._child_state_machine = child_sm

    def set_parent_sm(self, parent_sm):
        if not isinstance(parent_sm, StateMachine):
            raise TypeError("parent_sm must be the type of StateMachine")
        if self._child_state_machine and self._child_state_machine == \
                parent_sm:
            raise ValueError("child_sm and parent_sm must be different")
        self._parent_state_machine = parent_sm

    def start(self, data):
        log.debug(f"Entering {self._name}")
        for callback in self._entry_callbacks:
            callback(data)
        if self._child_state_machine is not None:
            self._child_state_machine.start(data)

    def stop(self, data):
        log.debug(f"Exiting {self._name}")
        for callback in self._exit_callbacks:
            callback(data)
        if self._child_state_machine is not None:
            self._child_state_machine.stop(data)

    def has_child_sm(self) -> bool:
        return True if self._child_state_machine else False

    @property
    def name(self):
        return self._name

    @property
    def child_sm(self):
        return self._child_state_machine

    @property
    def parent_sm(self):
        return self._parent_state_machine


class ExitState(State):

    def __init__(self, status="Normal"):
        self._name = "ExitState"
        self._status = status
        super().__init__(self._status + self._name)

    @property
    def status(self):
        return self._status


class Event(object):

    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return f"Event={self._name}"

    def __eq__(self, other):
        if other.name == self._name:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def name(self):
        return self._name


class Transition(object):

    def __init__(self, event: Event, src: State, dst: State):
        self._event = event
        self._source_state = src
        self._destination_state = dst
        self._condition = None
        self._action = None

    def __call__(self, data):
        raise NotImplementedError

    def add_condition(self, callback):
        self._condition = callback

    def add_action(self, callback):
        self._action = callback

    @property
    def event(self):
        return self._event

    @property
    def source_state(self):
        return self._source_state

    @property
    def destination_state(self):
        return self._destination_state


class NormalTransition(Transition):

    def __init__(self, source_state: State, destination_state: State,
                 event: Event):
        super().__init__(event, source_state, destination_state)
        self._from = source_state
        self._to = destination_state

    def __call__(self, data):
        if not self._condition or self._condition(data):
            log.info(f"NormalTransition from {self._from} to {self._to} caused by {self._event}")
            if self._action:
                self._action(data)
            self._from.stop(data)
            self._to.start(data)

    def __repr__(self):
        return f"Transition {self._from} to {self._to} by {self._event}"


class SelfTransition(Transition):

    def __init__(self, source_state: State, event: Event):
        super().__init__(event, source_state, source_state)
        self._state = source_state

    def __call__(self, data):
        if not self._condition or self._condition(data):
            log.info(f"SelfTransition {self._state}")
            if self._action:
                self._action(data)
            self._state.stop(data)
            self._state.start(data)

    def __repr__(self):
        return f"SelfTransition on {self._state}"


class NullTransition(Transition):

    def __init__(self, source_state: State, event: Event):
        super().__init__(event, source_state, source_state)
        self._state = source_state

    def __call__(self, data):
        if not self._condition or self._condition(data):
            log.info(f"NullTransition {self._state}")
            if self._action:
                self._action(data)

    def __repr__(self):
        return f"NullTransition on {self._state}"


class StateMachine(object):

    def __init__(self, name):
        self._name = name
        self._states = []
        self._events = []
        self._transitions = []
        self._initial_state = None
        self._current_state = None
        self._exit_callback = None
        self._exit_state = ExitState()
        self.add_state(self._exit_state)
        self._exited = True

    def __eq__(self, other):
        if other.name == self._name:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self._name

    def start(self, data):
        if not self._initial_state:
            raise ValueError("initial state is not set")
        self._current_state = self._initial_state
        self._exited = False
        self._current_state.start(data)

    def stop(self, data):
        if not self._initial_state:
            raise ValueError("initial state is not set")
        if self._current_state is None:
            raise ValueError("state machine has not been started")
        self._current_state.stop(data)
        self._current_state = self._exit_state
        self._exited = True

    def on_exit(self, callback):
        self._exit_callback = callback

    def is_running(self) -> bool:
        if self._current_state and self._current_state != self._exit_state:
            return True
        else:
            return False

    def add_state(self, state: State, initial_state: bool = False):
        if state in self._states:
            raise ValueError("attempting to add same state twice")
        self._states.append(state)
        state.set_parent_sm(self)
        if not self._initial_state and initial_state:
            self._initial_state = state

    def add_event(self, event: Event):
        self._events.append(event)

    def add_transition(self, src: State, dst: State, evt: Event):
        transition = None
        if src in self._states and dst in self._states and evt in self._events:
            transition = NormalTransition(src, dst, evt)
            self._transitions.append(transition)
        return transition

    def add_self_transition(self, state, evt):
        transition = None
        if state in self._states and evt in self._events:
            transition = SelfTransition(state, evt)
            self._transitions.append(transition)
        return transition

    def add_null_transition(self, state, evt):
        transition = None
        if state in self._states and evt in self._events:
            transition = NullTransition(state, evt)
            self._transitions.append(transition)
        return transition

    def trigger_event(self, evt: Event, data = None,
                      propagate: bool = False):
        transition_valid = False
        if not self._initial_state:
            raise ValueError("initial state is not set")

        if self._current_state is None:
            raise ValueError("state machine has not been started")

        if propagate and self._current_state.has_child_sm():
            log.debug(f"Propagating evt {evt} from {self} to {self._current_state.child_sm}")
            self._current_state.child_sm.trigger_event(evt, data, propagate)
        else:
            for transition in self._transitions:
                if transition.source_state == self._current_state and \
                        transition.event == evt:
                    self._current_state = transition.destination_state
                    transition(data)
                    if isinstance(self._current_state, ExitState) and \
                            self._exit_callback and not self._exited:
                        self._exited = True
                        self._exit_callback(self._current_state, data)
                    transition_valid = True
                    break
            if not transition_valid:
                log.warning(f"Event {evt} is not valid in state {self._current_state}")

    @property
    def exit_state(self):
        return self._exit_state

    @property
    def current_state(self):
        return self._current_state

    @property
    def name(self):
        return self._name