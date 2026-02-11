import random


class FiniteAutomaton:
    def __init__(self, states, alphabet, transitions, start_state, final_state):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.final_state = final_state

    def stringBelongToLanguage(self, inputString):
        current_state = self.start_state
        for char in inputString:
            if (current_state, char) in self.transitions:
                current_state = self.transitions[(current_state, char)]
            else:
                return False
        return current_state == self.final_state


class Grammar:
    def __init__(self, Vn, Vt, P, S):
        self.Vn = Vn
        self.Vt = Vt
        self.P = P
        self.S = S

    def generateString(self):
        word = self.S
        while any(char in self.Vn for char in word):
            nt = word[-1]
            production = random.choice(self.P[nt])
            word = word[:-1] + production
        return word

    def toFiniteAutomaton(self):
        transitions = {}
        for state, rules in self.P.items():
            for rule in rules:
                if len(rule) == 2:
                    symbol, next_state = rule[0], rule[1]
                    transitions[(state, symbol)] = next_state
                elif len(rule) == 1:
                    symbol = rule[0]
                    transitions[(state, symbol)] = "F"

        return FiniteAutomaton(
            states=self.Vn | {"F"},
            alphabet=self.Vt,
            transitions=transitions,
            start_state=self.S,
            final_state="F",
        )


if __name__ == "__main__":
    Vn = {"S", "B", "D"}
    Vt = {"a", "b", "c", "d"}
    P = {"S": ["aS", "bB"], "B": ["cB", "d", "aD"], "D": ["aB", "b"]}
    S = "S"

    my_grammar = Grammar(Vn, Vt, P, S)
    gen_strings = []

    print("Generated Strings:")
    for _ in range(5):
        generated_string = my_grammar.generateString()
        print(generated_string)
        gen_strings.append(generated_string)

    fa = my_grammar.toFiniteAutomaton()

    for str in gen_strings:
        print(f"\nChecking '{str}': {fa.stringBelongToLanguage(str)}")
