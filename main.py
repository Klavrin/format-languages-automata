import random


class Grammar:
    def __init__(self):
        self.start_state = "S"
        self.transitions = {
            "S": ["aS", "bB"],
            "B": ["cB", "aD", "d"],
            "D": ["aB", "b"],
        }

    def generate_string(self):
        current_state = self.start_state
        result = ""

        while True:
            production = random.choice(self.transitions[current_state])
            result += production[0]

            if len(production) == 1:
                break

            current_state = production[1]

        return result


class FiniteAutomaton:
    def __init__(self, states, alphabet, transitions, start_state, final_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = final_states

    def string_belong_to_language(self, input_string):
        current_states = {self.start_state}

        for i, symbol in enumerate(input_string):
            next_states = set()
            is_last = i == len(input_string) - 1

            for state in current_states:
                if (state, symbol) in self.transitions:
                    next_states.update(self.transitions[(state, symbol)])

                if is_last:
                    if state == "B" and symbol == "d":
                        return True
                    if state == "D" and symbol == "b":
                        return True

            current_states = next_states

            if not current_states and not is_last:
                return False

        return any(state in self.final_states for state in current_states)


if __name__ == "__main__":
    grammar = Grammar()

    fa = FiniteAutomaton(
        states={"S", "B", "D"},
        alphabet={"a", "b", "c", "d"},
        transitions={
            ("S", "a"): ["S"],
            ("S", "b"): ["B"],
            ("B", "c"): ["B"],
            ("B", "a"): ["D"],
            ("D", "a"): ["B"],
        },
        start_state="S",
        final_states={"B", "D"},
    )

    for _ in range(5):
        word = grammar.generate_string()
        print(f"Word: {word}")
        print("String belongs to language:", fa.string_belong_to_language(word))
        print()

    custom_word = "hello"
    print(f"Word: {custom_word}")
    print("String belongs to language:", fa.string_belong_to_language(custom_word))
