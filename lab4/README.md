# Laboratory Work 4 – Regular Expressions

### Course: Formal Languages & Finite Automata  
### Author: Sergiu Gherasim  
### Group: FAF-242  


## Theory

They are built from literal characters and operators like alternation (`|`),  
Regular expressions are patterns used to describe sets of strings.  
repetition (`*`, `+`), and grouping (`()`). A regex engine reads these patterns  
and can either match them against existing text, or, as in this lab, generate  
valid strings that conform to the pattern.

Regular expressions are widely used in software development, including  
input validation, search engines, compilers, and text processing tools.  
They provide a concise and powerful way to define complex string patterns.


## Objectives

1. Explain what regular expressions are and their main use cases.  
2. Implement a program in Python that dynamically generates valid strings from given regular expressions.  
3. Limit unbounded repetitions (`*`, `+`) to a maximum of 5 to avoid excessively long outputs.  
4. **Bonus:** Implement a function that logs the step-by-step processing of the regex.  


## Variant 4 – Regular Expressions

```
(S|T)(U|V)W*Y+24
L(M|N)O³P*Q(2|3)
R*S(T|U|V)W(X|Y|Z)²
```


## Implementation Description

### RegexNode (AST)

The program represents a parsed regular expression as a tree of `RegexNode` objects  
(Abstract Syntax Tree – AST). Each node corresponds to a specific regex construct.

There are four node types:
- `LITERAL` – a single character  
- `CONCAT` – a sequence of expressions  
- `ALTERNATION` – a choice between multiple expressions (`|`)  
- `REPEAT` – repetition of a subexpression (`*`, `+`, `²`, `³`)  

This structure makes it easy to process each construct independently during generation.

```python
class NodeType:
    LITERAL = "LITERAL"
    CONCAT = "CONCAT"
    ALTERNATION = "ALTERNATION"
    REPEAT = "REPEAT"


class RegexNode:
    def __init__(self, type_, literal=None, children=None, min_rep=0, max_rep=0):
        self.type = type_
        self.literal = literal
        self.children = children or []
        self.min_rep = min_rep
        self.max_rep = max_rep
```


### Parser

The parser is implemented as a **recursive-descent parser**. It reads the regex  
character by character and builds the AST.

One of the main challenges was handling Unicode superscript characters (`²`, `³`),  
which are not standard ASCII. These were handled explicitly using their Unicode  
values (`\u00B2`, `\u00B3`).

Another important aspect was respecting operator precedence:
- Alternation (`|`) – lowest priority  
- Concatenation – medium priority  
- Quantifiers (`*`, `+`, superscripts) – highest priority  

```python
def parse_expr(self):
    alts = [self.parse_concat()]
    while self.pos < len(self.src) and self.src[self.pos] == '|':
        self.pos += 1
        alts.append(self.parse_concat())

    if len(alts) == 1:
        return alts[0]
    return RegexNode.alt(alts)


def parse_concat(self):
    seq = []
    while self.pos < len(self.src) and self.src[self.pos] not in [')', '|']:
        seq.append(self.parse_quantified())

    if len(seq) == 1:
        return seq[0]
    return RegexNode.concat(seq)


def parse_quantified(self):
    atom = self.parse_atom()

    if self.pos < len(self.src):
        q = self.src[self.pos]

        if q == '*':
            self.pos += 1
            return RegexNode.repeat(atom, 0, MAX_REPEAT)

        if q == '+':
            self.pos += 1
            return RegexNode.repeat(atom, 1, MAX_REPEAT)

        exact = self.superscript_value(q)
        if exact > 0:
            self.pos += 1
            return RegexNode.repeat(atom, exact, exact)

    return atom
```


### Generator

The generator traverses the AST recursively and builds valid strings.

- For `ALTERNATION`, it randomly selects one branch  
- For `REPEAT`, it generates a random number of repetitions within bounds  
- For `CONCAT`, it combines results from all children  

A key detail was handling cases where `min_rep == max_rep` (e.g., `O³`).  
In these cases, the repetition count must be fixed, avoiding invalid random calls.

```python
def generate(node):
    if node.type == NodeType.LITERAL:
        return node.literal

    elif node.type == NodeType.CONCAT:
        return ''.join(generate(child) for child in node.children)

    elif node.type == NodeType.ALTERNATION:
        return generate(random.choice(node.children))

    elif node.type == NodeType.REPEAT:
        if node.min_rep == node.max_rep:
            times = node.min_rep
        else:
            times = random.randint(node.min_rep, node.max_rep)

        return ''.join(generate(node.children[0]) for _ in range(times))
```


### Bonus – Processing Sequence Logger

The parser includes a logging mechanism that records each step of the parsing process.  
Each important action (such as detecting a literal, entering a group, or applying a quantifier)  
is added to a log list.

This feature helps visualize how the regex is interpreted and improves debugging.

```python
def _log(self, msg):
    self.log.append(msg)
```

Example log messages:
```
parseExpr: looking for alternatives separated by '|'
found '|' at pos 2
superscript '³' -> repeat exactly 3
```


## Conclusions / Results

The program successfully generates valid strings for all three regular expressions  
from Variant 4.

Example output:

```
Regex 1 : (S|T)(U|V)W*Y+24
    TVWWYYYY24
    SVWYYY24
    TUWYYYYY24
    SVWWY24
    TVY24

Regex 2 : L(M|N)O³P*Q(2|3)
    LNOOOPQ2
    LMOOOPPPQ3
    LNOOOPPPPPQ2
    LMOOOPQ2

Regex 3 : R*S(T|U|V)W(X|Y|Z)²
    STWXX
    RSUWYZ
    RRRSTWZZ
    RRSVWXY
```

This lab demonstrated that:
- Regular expressions can be naturally represented as tree structures (AST)  
- Recursive-descent parsing is well-suited for processing regex grammars  
- Separating parsing from generation simplifies both implementation and debugging  

Overall, the Python implementation proved to be concise and expressive, while still  
handling all required features, including logging and controlled randomness.
