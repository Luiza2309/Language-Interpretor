from .DFA import DFA
from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs

@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        states: set[STATE] = {state}
        stack = [state]
        while stack:
            elements = self.d.get((stack.pop(), EPSILON))
            if elements:
                for e in elements:
                    if not e in states:
                        stack.append(e)
                        states.add(e)

        return states
        
    def subset_construction(self) -> DFA[frozenset[STATE]]:
        alphabet = self.S - {EPSILON}
        initial_state = frozenset(self.epsilon_closure(self.q0))
        states = {initial_state}
        dictionary = {}
        final_states = set()
        stack = [initial_state]

        while stack:
            top = stack.pop()

            for character in alphabet:
                new_state = set()
                final = False
                for element in top:
                    q = self.d.get((element, character))

                    if q:
                        for e in q:
                            new_state.update(self.epsilon_closure(e))

                    if element in self.F:
                        final = True
                    
                if final:
                    final_states.add(frozenset(top))

                if not new_state:
                    if not frozenset({"-1"}) in states:
                        states.add(frozenset({"-1"}))
                    dictionary[(top, character)] = frozenset({"-1"})
                else:
                    if not new_state in states:
                        states.add(frozenset(new_state))
                        stack.append(frozenset(new_state))
                    dictionary[(top, character)] = frozenset(new_state)

            if frozenset({"-1"}) in states:
                for character in alphabet:
                    dictionary[(frozenset({"-1"}), character)] = frozenset({"-1"})

        return DFA(alphabet, states, initial_state, dictionary, final_states)


    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        # optional, but may be useful for the second stage of the project. Works similarly to 'remap_states'
        # from the DFA class. See the comments there for more details.
        K = {f(x) for x in self.K}
        q0 = f(self.q0)
        d = {(f(state), character):{f(value) for value in values} for ((state, character), values) in self.d.items()}
        F = {f(x) for x in self.F}

        return NFA(self.S, K, q0, d, F)