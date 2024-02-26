from .NFA import NFA
from dataclasses import dataclass
from string import ascii_lowercase, ascii_uppercase

class Regex:
    def thompson(self) -> NFA[int]:
        raise NotImplementedError('the thompson method of the Regex class should never be called')
    
@dataclass
class Character(Regex):
    character: Regex

    def thompson(self) -> NFA[int]:
        return NFA({self.character}, {0, 1}, 0, {(0, self.character):{1}}, {1})

@dataclass
class Concat(Regex):
    right: Regex
    left: Regex

    def thompson(self) -> NFA[int]:
        nfa_right = self.right.thompson()
        nfa_left = self.left.thompson()
        nfa_right = nfa_right.remap_states(lambda x: int(x) + int(list(nfa_left.F)[0]) + 1)

        nfa_right.S.update(nfa_left.S)
        K = nfa_left.K
        K.update(nfa_right.K)
        d = nfa_left.d
        d.update(nfa_right.d)
        d[(list(nfa_left.F)[0], '')] = {nfa_right.q0}

        return NFA(nfa_right.S, K, nfa_left.q0, d, nfa_right.F)

@dataclass
class Union(Regex):
    right: Regex
    left: Regex

    def thompson(self) -> NFA[int]:
        nfa_left = self.left.thompson().remap_states(lambda x: int(x) + 1)
        nfa_right = self.right.thompson().remap_states(lambda x: int(x) + int(list(nfa_left.F)[0]) + 1)

        nfa_right.S.update(nfa_left.S)
        F = {int(list(nfa_right.F)[0]) + 1}
        K = nfa_left.K
        K.update(nfa_right.K)
        K.add(0)
        K.update(F)

        d = nfa_left.d
        d.update(nfa_right.d)
        d[(0, '')] = {nfa_right.q0, nfa_left.q0}
        d[(list(nfa_right.F)[0], '')] = F
        d[(list(nfa_left.F)[0], '')] = F

        return NFA(nfa_right.S, K, 0, d, F)

@dataclass
class Star(Regex):
    expr: Regex

    def thompson(self) -> NFA[int]:
        nfa = self.expr.thompson().remap_states(lambda x: int(x) + 1)

        F = {int(list(nfa.F)[0]) + 1}
        states = {int(list(nfa.F)[0]) + 1, nfa.q0}
        K = nfa.K
        K.add(0)
        K.update(F)
        nfa.d[(0, '')] = states
        nfa.d[(list(nfa.F)[0], '')] = states

        return NFA(nfa.S, K, 0, nfa.d, F)

@dataclass
class Plus(Regex):
    expr: Regex

    def thompson(self) -> NFA[int]:
        nfa = self.expr.thompson().remap_states(lambda x: int(x) + 1)

        F = {int(list(nfa.F)[0]) + 1}
        states = {int(list(nfa.F)[0]) + 1, nfa.q0}
        K = nfa.K
        K.add(0)
        K.update(F)
        nfa.d[(0, '')] = {nfa.q0}
        nfa.d[(list(nfa.F)[0], '')] = states

        return NFA(nfa.S, K, 0, nfa.d, F)

@dataclass
class Question(Regex):
    expr: Regex

    def thompson(self) -> NFA[int]:
        nfa = self.expr.thompson().remap_states(lambda x: int(x) + 1)

        F = {int(list(nfa.F)[0]) + 1}
        states = {int(list(nfa.F)[0]) + 1, nfa.q0}
        K = nfa.K
        K.add(0)
        K.update(F)
        nfa.d[(0, '')] = states
        nfa.d[(list(nfa.F)[0], '')] = F

        return NFA(nfa.S, K, 0, nfa.d, F)

def parse_regex(regex: str) -> Regex:
    stack = []
    queue = []
    iterator = 0
    operands = ['+', '|', '?', '*', '(', ')', '[', ']', '\\']
    character_before = False

    #iterate over the input
    while iterator < len(regex):
        # if the character is not an operand (letters, numbers, _, & etc.)
        if not regex[iterator] in operands and not regex[iterator].isspace():
            # it will go in the queue
            queue.append(Character(regex[iterator]))

            j = iterator - 1
            while regex[j] == " ":
                j = j - 1

            # concatenation
            if character_before or (j >= 0 and regex[j] in ['+', '?', '*', ')', ']', '\\']):
                while stack and stack[-1] in ['+', '*', '?']:
                    queue.append(stack.pop())
                stack.append("**")  # add a symbol to differentiate concatenation from the others

            if iterator + 1 < len(regex) and regex[iterator + 1] in ['(', '[', '\\']:
                while stack and stack[-1] in ['+', '*', '?']:
                    queue.append(stack.pop())
                stack.append("**")  # add a symbol to differentiate concatenation from the others

            character_before = True
        # if the character is an operand
        elif regex[iterator] in operands:
            # it will go in the stack
            # if the top of the stack has a greater priority than my current operand then it wil go in the queue and the current operand will go in the stack
            if regex[iterator] == '*':
                queue.append('*')
            elif regex[iterator] == '+':
                queue.append('+')
            elif regex[iterator] == '?':
                queue.append('?')
            elif regex[iterator] == '|':
                while stack and stack[-1] in ['+', '*', '?', "**"]:
                    queue.append(stack.pop())
                stack.append('|')
            elif regex[iterator] == '(':
                stack.append('(')
            elif regex[iterator] == ')':
                # pop from the stack and enqueue the operands until i find a '('
                while stack and stack[-1] != '(':
                    queue.append(stack.pop())
                stack.pop()
            elif regex[iterator] == '[':
                # get the next character and make reunion between all characters in the interval
                character = regex[iterator + 1]
                if character == '0':
                    r = Union(Character('0'), Character('1'))
                    for i in range(2, 10):
                        r = Union(r, Character(str(i)))
                elif character == 'a':
                    r = Union(Character('a'), Character('b'))
                    for i in ascii_lowercase:
                        if i != 'a' and i != 'b':
                            r = Union(r, Character(str(i)))
                elif character == 'A':
                    r = Union(Character('A'), Character('B'))
                    for i in ascii_uppercase:
                        if i != 'A' and i != 'B':
                            r = Union(r, Character(str(i)))
                queue.append(r)
                iterator = iterator + 4
            elif regex[iterator] == '\\':
                queue.append(Character(regex[iterator + 1]))

            character_before = False

            if regex[iterator] == '\\':
                j = iterator + 2
            else:
                j = iterator + 1
            while j < len(regex) and regex[j] == " ":
                j = j + 1

            if j < len(regex):
                if (regex[iterator] in ['*', '+', '?', ')', ']', '\\'] and regex[j] in ['(', '[', '\\']):
                    while stack and stack[-1] in ['+', '*', '?']:
                        queue.append(stack.pop())
                    stack.append("**")

            if regex[iterator] == '\\':
                iterator = iterator + 1
        # if the character is an operand but it is considered part of the regex
        elif regex[iterator] == '\n':
            queue.append(Character('\n'))
        elif regex[iterator] == '\t':
            queue.append(Character('\t'))
            
        iterator = iterator + 1

    # empty the stack and put the operands in the queue
    while stack:
        queue.append(stack.pop())
    
    iterator = 0
    operands.append("**")
    # add characters on the stack until i found an operand
    while queue:
        current_element = queue.pop(0)
        if not current_element in operands:
            stack.append(current_element)
        else:
            # depending on the operand i take out of the stack one or two characters and make the operation and put the result back on the stack
            if current_element == '*':
                stack.append(Star(stack.pop()))
            elif current_element == '+':
                stack.append(Plus(stack.pop()))
            elif current_element == '?':
                stack.append(Question(stack.pop()))
            elif current_element == '|':
                stack.append(Union(stack.pop(), stack.pop()))
            elif current_element == "**":
                stack.append(Concat(stack.pop(), stack.pop()))

    return stack.pop()