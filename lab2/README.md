# Determinism in Finite Automata. Conversion from NDFA 2 DFA. Chomsky Hierarchy.

## Overview

Finite automata are mathematical models used to describe systems that operate through a limited number of states. They are commonly applied in areas such as pattern matching, lexical analysis in compilers, and the study of formal languages. A finite automaton is defined by several components: a set of states, an input alphabet, a transition function, a starting state, and a collection of accepting states.

Automata can be divided into two main categories depending on the behavior of their transitions. In a deterministic automaton, every pair of state and input symbol produces exactly one next state. In contrast, a non-deterministic automaton may allow several possible next states for the same state and input symbol. Even though non-deterministic automata appear more flexible, there are well-known algorithms that transform them into equivalent deterministic automata.

This laboratory assignment continues the exploration of grammars and automata by focusing on classification, transformation, and analysis of finite automata.

## Objectives

The purpose of this laboratory is to deepen the understanding of theoretical concepts related to automata and grammars through practical implementation. The project requires implementing functionality that can classify grammars based on the Chomsky hierarchy, analyze whether a finite automaton is deterministic, convert an automaton into a regular grammar, and transform a non-deterministic finite automaton into a deterministic one.

Through these tasks, the laboratory demonstrates the relationship between formal grammars and finite automata, as well as the algorithms used to manipulate these structures.

## Variant Definition
states => Q = {q0, q1, q2}
Alphabet => Σ = {a, b}
starting state => q0
final state => F = {q2}

Transitions:
δ(q0, a) = q0
δ(q0, b) = q1
δ(q1, a) = q0
δ(q1, b) = q1
δ(q1, b) = q2
δ(q2, b) = q1

## Implementation Approach
The implementation follows an object-oriented approach. A dedicated class called FiniteAutomaton stores the essential components of the automaton, including the set of states, the alphabet, the transition function, the start state, and the final states.

Transitions are represented using a mapping structure that associates a state and an input symbol with a set of possible destination states. This design allows the automaton to naturally represent non-deterministic behavior.

The program provides several operations, including:
- adding transitions
- checking whether the automaton is deterministic
- converting an NDFA into a DFA
- generating an equivalent regular grammar

A separate client or main class initializes the automaton and demonstrates the functionality of the implemented algorithms.

## Determinism Detection
To determine whether the automaton is deterministic, the program inspects each transition entry. If any state and input symbol pair leads to more than one possible next state, the automaton is classified as non-deterministic.

```py
def is_deterministic(self):
    for state in self.transitions:
        for symbol in self.transitions[state]:
            if len(self.transitions[state][symbol]) > 1:
                return False
    return True
}
```
```
```

For the defined automaton, the method returns false because the transition (q1, b) leads to both q1 and q2.

### NDFA to DFA Conversion

To obtain a deterministic automaton, the program applies the subset construction method. In this process, each state in the resulting DFA represents a set of states from the original NDFA.

The procedure begins with the start state of the NDFA and gradually constructs new DFA states by combining reachable states under each input symbol. This process continues until no additional state sets can be produced.

The final deterministic automaton accepts the same language as the original non-deterministic automaton while ensuring that every transition leads to a single well-defined state.

### Conclusion
This laboratory demonstrates the fundamental concepts behind finite automata and their relationship with formal grammars. By implementing a finite automaton structure and related algorithms, the project provides practical insight into how theoretical models from formal language theory can be represented and manipulated programmatically.

Through the determinism detection mechanism, it becomes possible to identify whether an automaton behaves deterministically or allows multiple transitions for the same state and input symbol. The NDFA to DFA conversion further illustrates that non-deterministic automata do not possess greater computational power than deterministic ones, since an equivalent deterministic automaton can always be constructed using the subset construction method.

Additionally, exploring the connection between automata and regular grammars highlights the equivalence between different representations of regular languages within the Chomsky hierarchy. This reinforces the theoretical understanding that regular grammars, deterministic finite automata, and non-deterministic finite automata describe the same class of languages.

Overall, the implementation bridges theory and practice by translating formal definitions into working algorithms, strengthening both conceptual understanding and programming skills related to automata and language processing.
