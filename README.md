# The title of the work

### Course: Formal Languages & Finite Automata
### Author: Sergiu Gherasim

----

## Theory
A finite automata is a machine that accepts something as input, using that, it outputs something out.
In our case, we have a automaton that accepts a string. The main purpose of our automaton is to check if the string belongs to our language.
Our language is defined by the grammar. The grammar is created using the alphabet. The alphabet is a set of characters that are being accepted by the automaton. We also have states, in our case there are 3 states: S, B and D. After some research, I found out that I need to add another state, which is F. F acts as the final step. For instance, when we are in the following state: B → d, we can no longer go anywhere. Therefore, this acts as our final stop in the automaton, for which we are using the state F. Let's also mention transitions. I like to think of transitions as rules (i.e. if I am here (state A), and I do this (char b), then I go here (state B)). Finally, we also have a start state, which is simply the state we start from. 


## Objectives:

* Define the Grammar.
* Create the Finite Automata.
* Create some tests


## Implementation description

### The "Grammar" class
The Grammar class accepts in four params: Vn - the states, Vt - the chars/alphabet, P - the transitions and S - the starting state. The class has two methods. The first one is `generateString`, which will generate a random string using our alphabet. The second one is `toFiniteAutomaton`, which is a method that converts, or kind of "normalizes", our transitions to have transitions that also lead to the final state (F). If the length of the rule is 2, then it means that we have a state we can go to, otherwise it means we don't have a state to go to, which means this is the end, so we add F. Then we return an instance of the `FiniteAutomaton` class.

```py
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
```

### The "FiniteAutomaton" class
The "FiniteAutomaton" class is where we use our grammar to check if strings belong to our language. We pass in 5 params (very self-explanatory) to the constructor of the class. The class has only one method: `stringBelongToLanguage`. This method accepts in an `inputString`, sets the `current_state` variable to the starting state, and then loops through each character in the `inputString` to find if there are any matching transitions. If we find a matching transition, we change the state. We repeat this until we either finish looping through the string, or stumble upon a character that, for this state, doesn't have a matching transition. 

```py
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
```
```

```

### The main block
In the main block all I am doing is defining variables with the states, alphabet, the transitions and the starting state. Then, I create an instance of the `Grammar` class, passing in all of them as params to the class constructor. Then, I generate a few strings using the `Grammar` class instance in order to showcase that it actually works. Finally, I use the `toFiniteAutomaton` method from the `Grammar` class to store an instance of the `FiniteAutomaton` class in the `fa` variable, create a list with valid and invalid strings, and then loop through the tests list to show that the `stringBelongToLanguage` method works.

```py
if __name__ == "__main__":
    Vn = {"S", "B", "D"}
    Vt = {"a", "b", "c", "d"}
    P = {"S": ["aS", "bB"], "B": ["cB", "d", "aD"], "D": ["aB", "b"]}
    S = "S"

    my_grammar = Grammar(Vn, Vt, P, S)

    print("Generated Strings:")
    for _ in range(5):
        generated_string = my_grammar.generateString()
        print(generated_string)

    fa = my_grammar.toFiniteAutomaton()

    tests = [
        # valid strings
        "bd",
        "abcab",
        "abb",
        "aaabccccd",
        "bacab",
        # invalid strings
        "a",
        "abc",
        "ba",
        "ac",
        "dd",
        "xyz",
    ]

    for str in tests:
        print(f"\nChecking '{str}': {fa.stringBelongToLanguage(str)}")
```


## Conclusions / Screenshots / Results
In conclusion, I can definitely say that I learned more about Finite Automata doing this, then watching videos on YouTube or reading the presentation slides. Learning by doing always wins! To summarize, we have created two classes: `Grammar` and `FiniteAutomaton`. The `Grammar` class is used to: (1) generate random strings and (2) "normalize" a dictionary of transitions. While the `FiniteAutomaton` class, is used to check if a string belongs to a language or not. Then, using all of this, we loop through a list of test strings and then validate (or not) them.

### The output of the program:
```

```
Generated Strings:
aabd
bcaacccd
bcaaab
bcaaaaab
bab

Checking 'bd': True

Checking 'abcab': True

Checking 'abb': False

Checking 'aaabccccd': True

Checking 'bacab': False

Checking 'a': False

Checking 'abc': False

Checking 'ba': False

Checking 'ac': False

Checking 'dd': False

Checking 'xyz': False
```

## References
- https://www.youtube.com/watch?v=PK3wL7DXuuw&t=27s
- https://else.fcim.utm.md/pluginfile.php/110457/mod_resource/content/0/Theme_1.pdf
