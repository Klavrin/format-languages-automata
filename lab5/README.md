# Laboratory Work 5 - Chomsky Normal Form

### Course: Formal Languages & Finite Automata
### Author: Sergiu Gherasim
### Group: FAF-242


## Theory

A Context-Free Grammar (CFG) is in **Chomsky Normal Form (CNF)** when every production
rule looks like one of these:

- `A -> BC` - a nonterminal produces exactly two nonterminals
- `A -> a` - a nonterminal produces a single terminal
- `S -> ε` - only allowed for the start symbol, and only if the language contains the empty string

CNF matters mostly because algorithms like **CYK (Cocke-Younger-Kasami)** require it.
Any context-free grammar can be converted into an equivalent CNF one - same language,
different shape. The conversion goes through five steps applied in a fixed order,
because doing them in the wrong order can quietly break what a previous step already fixed.


## Objectives

1. Learn about Chomsky Normal Form (CNF).
2. Get familiar with the approaches of normalizing a context-free grammar.
3. Implement a method for normalizing an input grammar according to the rules of CNF:
    1. The implementation must be encapsulated in a method/class with an appropriate signature.
    2. The implemented functionality must be executed and tested.
    3. **Bonus:** The function accepts any grammar, not only the one from the student's variant.


## Variant 8 - Input Grammar

```
G = (V_N, V_T, P, S)
V_N = {S, A, B, C}
V_T = {a, d}

P:
  1.  S -> dB
  2.  S -> A
  3.  A -> d
  4.  A -> dS
  5.  A -> aAdAB
  6.  B -> a
  7.  B -> aS
  8.  B -> A
  9.  B -> ε
  10. C -> Aa
```


## Implementation Description

### Grammar

The `Grammar` class just holds the four parts of a CFG: nonterminals, terminals,
productions, and the start symbol. Productions are a `dict` mapping each nonterminal
to a list of right-hand sides, where each right-hand side is a list of symbol strings.
An empty list means ε. Since Python's built-in `set` is unordered, `dict.fromkeys(...)`
is used to preserve insertion order for V_N and V_T, mirroring the behavior of Java's
`LinkedHashSet`. There is also a `__str__` method so the grammar prints nicely after
each step.

```python
class Grammar:
    def __init__(self, non_terminals, terminals, productions, start_symbol):
        self.non_terminals = dict.fromkeys(non_terminals)
        self.terminals = dict.fromkeys(terminals)
        self.productions = {k: [list(rhs) for rhs in v] for k, v in productions.items()}
        self.start_symbol = start_symbol
    # ...
```

### CNFConverter

`CNFConverter` has one main method `to_cnf(g)` that runs all five steps and prints
the grammar after each one. Every step is also its own method so they can be called
and tested separately. New nonterminal names are generated using a `fresh_counter`
to avoid collisions.

```python
class CNFConverter:
    def __init__(self):
        self.fresh_counter = 0

    def to_cnf(self, g): ...

    def eliminate_epsilon_productions(self, g):     ...
    def eliminate_renaming_rules(self, g):          ...
    def eliminate_inaccessible_symbols(self, g):    ...
    def eliminate_non_productive_symbols(self, g):  ...
    def to_proper_cnf(self, g):                     ...
```

### Step 1 - Eliminate ε-productions

The first thing to do is find all *nullable* nonterminals - those that can eventually
derive ε, either directly or through other nullable symbols. Once that set is built,
every rule containing a nullable symbol gets duplicated: one version keeps it, one
drops it. Then the original ε-rules are deleted.

The tricky part here was the combination logic. For a rule like `A -> aAdAB` where
multiple symbols could be nullable, you need all subsets, not just one omission at a
time. Getting that expansion right without accidentally producing duplicates or missing
cases took a few tries - iterating over positions and rebuilding the set at each step
ended up being the cleanest approach.

For Variant 8, `B -> ε` is the only direct ε-rule, making B nullable. That causes
`S -> dB` to also produce `S -> d`, and `A -> aAdAB` to also produce `A -> aAdA`.

```python
def _find_nullable(self, g):
    nullable = set()
    for lhs, rules in g.get_productions().items():
        for rhs in rules:
            if not rhs:
                nullable.add(lhs)
    changed = True
    while changed:
        changed = False
        for lhs, rules in g.get_productions().items():
            if lhs in nullable:
                continue
            for rhs in rules:
                if rhs and all(sym in nullable for sym in rhs):
                    if lhs not in nullable:
                        nullable.add(lhs)
                        changed = True
                    break
    return nullable
```

### Step 2 - Eliminate renaming (unit) rules

A unit rule is `A -> B` where both symbols are nonterminals. The fix is to compute the
*unit closure* of each nonterminal - every nonterminal reachable from it through a
chain of unit rules - and then copy all non-unit productions from those reachable
nonterminals directly into the original one.

One thing that caught me off guard: if you have a chain like `S -> A -> B`, you need
to follow it all the way, not just one step. BFS handles that naturally once you think
of it that way.

For Variant 8, `S -> A` and `B -> A` are both unit rules. After this step, S and B
each get A's productions added directly to them.

```python
def _unit_closure(self, start, g):
    non_terminals = set(g.get_non_terminals())
    visited = []
    visited_set = set()
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        if cur in visited_set:
            continue
        visited_set.add(cur)
        visited.append(cur)
        for rhs in g.get_productions().get(cur, []):
            if len(rhs) == 1 and rhs[0] in non_terminals:
                queue.append(rhs[0])
    return visited
```

### Step 3 - Eliminate inaccessible symbols

A symbol is inaccessible if no derivation starting from S can ever reach it. This is
just a reachability problem - BFS from the start symbol, following every nonterminal
that shows up on a right-hand side. Whatever is never visited gets removed along with
its rules.

For Variant 8, `C` is never referenced in any rule reachable from S, so it is dropped.

```python
def eliminate_inaccessible_symbols(self, g):
    non_terminals = set(g.get_non_terminals())
    accessible_set = set()
    queue = deque([g.get_start_symbol()])
    while queue:
        cur = queue.popleft()
        if cur in accessible_set:
            continue
        accessible_set.add(cur)
        for rhs in g.get_productions().get(cur, []):
            for sym in rhs:
                if sym in non_terminals:
                    queue.append(sym)
    # keep only accessible nonterminals and their rules
    # ...
```

### Step 4 - Eliminate non-productive symbols

A nonterminal is productive if it can eventually produce a string of terminals.
Terminals themselves are always productive. For nonterminals, you check iteratively:
if every symbol on the right-hand side of some rule is productive, then the left-hand
side is productive too. Repeat until nothing changes, then remove whatever never
became productive.

For Variant 8 all remaining symbols are already productive after Step 3, so this step
changes nothing. It is still important to have it in case the input grammar is different.

### Step 5 - Obtain proper CNF (START + TERM + BIN)

This step is split into three smaller transformations:

**START** - If the start symbol appears on any right-hand side, a new start symbol S0
is introduced. Instead of writing `S0 -> S` (which would just create another unit rule
to clean up), the productions of S are copied directly into S0, and S is removed
entirely from the grammar.

**TERM** - Terminals that appear alongside other symbols in a rule get wrapped in a
fresh nonterminal. So `d` in `S -> dB` becomes `T_D`, and `T_D -> d` is added. This
was straightforward but easy to forget - mixing terminals and nonterminals in a binary
rule is still not valid CNF.

**BIN** - Rules with more than two symbols on the right are broken into a chain of
binary rules. The recursive approach worked well here: peel off the first symbol, pair
it with a fresh nonterminal, then recurse on the rest.

The initial implementation created independent intermediate nonterminals for every rule separately.
For example, S -> a A d A B, A -> a A d A B, and B -> a A d A B all binarize the same suffix [A, d, A, B],
but the old code created S1/S11/S111, A1/A11/A111, and B1/B11/B111 as three separate sets of nodes for identical structure.
This produced 26 nonterminals in the final grammar. The fix was to introduce a suffix cache, a dict from a suffix tuple to
the intermediate nonterminal that represents it. When two rules share the same suffix, they reuse the same node instead of
creating a duplicate. This brought the final nonterminal count down to 10.

```python
def _binarize(self, lhs, symbols, nts, nts_set, prods, suffix_cache):
    if len(symbols) <= 2:
        prods.setdefault(lhs, []).append(list(symbols))
        return
    suffix = tuple(symbols[1:])
    if suffix not in suffix_cache:
        name = self._fresh_symbol(lhs + "1", nts_set)
        nts.append(name)
        nts_set.add(name)
        suffix_cache[suffix] = name
    fresh = suffix_cache[suffix]
    prods.setdefault(lhs, []).append([symbols[0], fresh])
    if fresh not in prods:
        self._binarize(fresh, list(suffix), nts, nts_set, prods, suffix_cache)
```


## Conclusions / Results

The program correctly converts the Variant 8 grammar into CNF across all five steps.
The full output is:

```
ORIGINAL GRAMMAR
V_N = [S, A, B, C]
V_T = [a, d]
S   = S
P:
  S -> d B
  S -> A
  A -> d
  A -> d S
  A -> a A d A B
  B -> a
  B -> a S
  B -> A
  B -> ε
  C -> A a

STEP 1: Eliminate ε-productions
V_N = [S, A, B, C]
V_T = [a, d]
S   = S
P:
  S -> d B
  S -> d
  S -> A
  A -> d
  A -> d S
  A -> a A d A B
  A -> a A d A
  B -> a
  B -> a S
  B -> A
  C -> A a

STEP 2: Eliminate renaming (unit) rules
V_N = [S, A, B, C]
V_T = [a, d]
S   = S
P:
  S -> d B
  S -> d
  S -> d S
  S -> a A d A B
  S -> a A d A
  A -> d
  A -> d S
  A -> a A d A B
  A -> a A d A
  B -> a
  B -> a S
  B -> d
  B -> d S
  B -> a A d A B
  B -> a A d A
  C -> A a

STEP 3: Eliminate inaccessible symbols
V_N = [S, A, B]
V_T = [a, d]
S   = S
P:
  S -> d B
  S -> d
  S -> d S
  S -> a A d A B
  S -> a A d A
  A -> d
  A -> d S
  A -> a A d A B
  A -> a A d A
  B -> a
  B -> a S
  B -> d
  B -> d S
  B -> a A d A B
  B -> a A d A

STEP 4: Eliminate non-productive symbols
V_N = [S, A, B]
V_T = [a, d]
S   = S
P:
  S -> d B
  S -> d
  S -> d S
  S -> a A d A B
  S -> a A d A
  A -> d
  A -> d S
  A -> a A d A B
  A -> a A d A
  B -> a
  B -> a S
  B -> d
  B -> d S
  B -> a A d A B
  B -> a A d A

STEP 5: Chomsky Normal Form (IMPROVED)
V_N = [A, B, S0, T_D, T_A, A1, A11, A111, A12, A121]
V_T = [a, d]
S   = S0
P:
  A -> d
  A -> T_D S0
  A -> T_A A1
  A -> T_A A12
  A1 -> A A11
  A11 -> T_D A111
  A111 -> A B
  A12 -> A A121
  A121 -> T_D A
  B -> a
  B -> T_A S0
  B -> d
  B -> T_D S0
  B -> T_A A1
  B -> T_A A12
  S0 -> T_D B
  S0 -> d
  S0 -> T_D S0
  S0 -> T_A A1
  S0 -> T_A A12
  T_D -> d
  T_A -> a

STEP 5: Chomsky Normal Form (BEFORE)
V_N = [S, A, B, S0, T_D, T_A, S1, S11, S111, S12, S121, A1, A11, A111, A13, A131, B1, B11, B111, B14, B141, S01, S011, S0111, S015, S0151]
V_T = [a, d]
S   = S0
P:
  S -> T_D B
  S -> d
  S -> T_D S
  S -> T_A S1
  S -> T_A S12
  S1 -> A S11
  S11 -> T_D S111
  S111 -> A B
  S12 -> A S121
  S121 -> T_D A
  A -> d
  A -> T_D S
  A -> T_A A1
  A -> T_A A13
  A1 -> A A11
  A11 -> T_D A111
  A111 -> A B
  A13 -> A A131
  A131 -> T_D A
  B -> a
  B -> T_A S
  B -> d
  B -> T_D S
  B -> T_A B1
  B -> T_A B14
  B1 -> A B11
  B11 -> T_D B111
  B111 -> A B
  B14 -> A B141
  B141 -> T_D A
  S0 -> T_D B
  S0 -> d
  S0 -> T_D S
  S0 -> T_A S01
  S0 -> T_A S015
  S01 -> A S011
  S011 -> T_D S0111
  S0111 -> A B
  S015 -> A S0151
  S0151 -> T_D A
  T_D -> d
  T_A -> a

```

Every rule in the final grammar is either `A -> BC` or `A -> a`, so the result is
valid CNF. The biggest lesson from this lab is that the order of the steps genuinely
matters - running UNIT before DEL for example would mean unit rules introduced by
epsilon elimination never get cleaned up. Getting the combination logic in Step 1 right
was probably the most time-consuming part of the implementation.
