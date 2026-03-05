from collections import defaultdict, deque


class FiniteAutomaton:
    def __init__(self):
        self.states = set()
        self.alphabet = set()
        self.start_state = None
        self.final_states = set()

        self.transitions = defaultdict(lambda: defaultdict(set))

    def add_transition(self, from_state, symbol, to_state):
        self.transitions[from_state][symbol].add(to_state)

    def is_deterministic(self):
        for state in self.transitions:
            for symbol in self.transitions[state]:
                if len(self.transitions[state][symbol]) > 1:
                    return False
        return True

    def convert_to_dfa(self):
        dfa = FiniteAutomaton()
        dfa.alphabet = self.alphabet.copy()

        name_map = {}
        queue = deque()

        start_set = frozenset([self.start_state])

        name_map[start_set] = str(set(start_set))
        dfa.start_state = name_map[start_set]
        dfa.states.add(name_map[start_set])
        queue.append(start_set)

        if self.contains_final(start_set):
            dfa.final_states.add(name_map[start_set])

        while queue:
            current = queue.popleft()
            current_name = name_map[current]

            for symbol in self.alphabet:
                next_set = set()

                for state in current:
                    if state in self.transitions and symbol in self.transitions[state]:
                        next_set.update(self.transitions[state][symbol])

                if not next_set:
                    continue

                next_frozen = frozenset(next_set)

                if next_frozen not in name_map:
                    name_map[next_frozen] = str(next_set)

                next_name = name_map[next_frozen]

                if next_name not in dfa.states:
                    dfa.states.add(next_name)
                    queue.append(next_frozen)

                    if self.contains_final(next_set):
                        dfa.final_states.add(next_name)

                dfa.add_transition(current_name, symbol, next_name)

        return dfa

    def contains_final(self, states_set):
        for s in states_set:
            if s in self.final_states:
                return True
        return False

    def to_regular_grammar(self):
        grammar = defaultdict(list)

        for state in self.transitions:
            for symbol in self.transitions[state]:
                for nxt in self.transitions[state][symbol]:
                    grammar[state].append(f"{symbol}{nxt}")

                    if nxt in self.final_states:
                        grammar[state].append(symbol)

        return grammar

    def print_automaton(self, title="Finite Automaton"):
        print("\n" + "=" * 40)
        print(title)
        print("=" * 40)

        print("States:", ", ".join(sorted(self.states)))
        print("Alphabet:", ", ".join(sorted(self.alphabet)))
        print("Start state:", self.start_state)
        print("Final states:", ", ".join(sorted(self.final_states)))

        print("\nTransitions:")
        for state in sorted(self.transitions):
            for symbol in sorted(self.transitions[state]):
                next_states = ", ".join(sorted(self.transitions[state][symbol]))
                print(f"  δ({state}, {symbol}) → {next_states}")

    def print_grammar(self, grammar):
        print("\n" + "=" * 40)
        print("Regular Grammar")
        print("=" * 40)

        for non_terminal in sorted(grammar):
            productions = " | ".join(grammar[non_terminal])
            print(f"{non_terminal} → {productions}")


fa = FiniteAutomaton()

fa.states.update(["q0", "q1", "q2"])
fa.alphabet.update(["a", "b", "c"])
fa.start_state = "q0"
fa.final_states.add("q2")

fa.add_transition("q0", "a", "q0")
fa.add_transition("q0", "b", "q1")
fa.add_transition("q1", "c", "q1")
fa.add_transition("q1", "c", "q2")
fa.add_transition("q2", "a", "q0")
fa.add_transition("q1", "a", "q1")


fa.print_automaton("Original Finite Automaton")

print("\nIs deterministic?", fa.is_deterministic())


# NDFA to DFA
dfa = fa.convert_to_dfa()
dfa.print_automaton("Converted DFA")


# FA to Regular Grammar
grammar = fa.to_regular_grammar()
fa.print_grammar(grammar)
