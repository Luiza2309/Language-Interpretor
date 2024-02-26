from .DFA import DFA
from .NFA import NFA
from .Regex import parse_regex

class Lexer:
    dfa:DFA
    final_states:list

    def __init__(self, spec: list[tuple[str, str]]) -> None:
        # initialisation should convert the specification to a dfa which will be used in the lex method
        # the specification is a list of pairs (TOKEN_NAME:REGEX) 
        S = set()
        K = set()
        d = {(("initial", 0), '') : set()}
        F = set()
        final_states = []
        K.add(("initial", 0))
        
        for entry in spec:
            nfa = (parse_regex(entry[1]).thompson()).remap_states(lambda x: (entry[0], x))
            S.update(nfa.S)
            K.update(nfa.K)
            d.update(nfa.d)
            F.update(nfa.F)
            d.get((("initial", 0), '')).add(nfa.q0)
            final_states.append(nfa.F.pop())  # keep the final states of the NFAs

        self.dfa = NFA(S, K, ("initial", 0), d, F).subset_construction()
        self.final_states = final_states

    def lex(self, word: str) -> list[tuple[str, str]] | None:
        # this method splits the lexer into tokens based on the specification and the rules described in the lecture
        # the result is a list of tokens in the form (TOKEN_NAME:MATCHED_STRING)

        # if an error occurs and the lexing fails, you should return none # todo: maybe add error messages as a task

        ret = []
        lines = 0  # on which line i am; for errors
        curr_char = 0  # on which character i am; for errors
        word_length = len(word)  # to know when the word is finished

        while len(word) > 0:
            current_accept_state = ()  # possible acceptance state
            q = self.dfa.q0  # initial state of DFA
            prefix = ''  # characters taken from the word

            for character in word:
                q = self.dfa.d.get((q, character))
                if not q:  # there is an invalid character in input
                    err = "No viable alternative at character " + str(curr_char) + ", line " + str(lines)
                    return [("", err)]
                
                prefix = prefix + character

                # there are multiple states in a single state(q) because of subset construction
                if q in self.dfa.F:  # there is a token that accepts the prefix
                    for state in self.final_states:  # search the final state that accepts the prefix
                        if state in q:
                            current_accept_state = (state[0], prefix)  # save the state
                            break  # only keep the first occurance from final states
                else:
                    states = next(iter(q))
                    if '-1' == states:  # sink state
                        if current_accept_state == ():  # the prefix wasn't accepted until now
                            err = "No viable alternative at character " + str(curr_char) + ", line " + str(lines)
                            return [("", err)]
                        
                        word = word[len(current_accept_state[1]):]  # cut the prefix out of the word
                        curr_char = curr_char - len(prefix) + len(current_accept_state[1]) + 1
                        break

                curr_char = curr_char + 1
                if character == '\n':  # get on new line
                    lines = lines + 1
                    curr_char = 0

            ret.append(current_accept_state)

            if current_accept_state == ():
                err = "No viable alternative at character EOF, line " + str(lines)
                return [("", err)]

            word_length = word_length - len(current_accept_state[1])
            if word_length <= 0:  # the word is finished
                break
            
        return ret