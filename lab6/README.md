# Laboratory Work 6 - Parser & Building an Abstract Syntax Tree


### Course: Formal Languages & Finite Automata
### Author: Sergiu Gherasim
### Group: FAF-242


## Theory

**Parsing** is the process of analyzing a sequence of tokens to determine its
grammatical structure with respect to a given formal grammar. It is the stage that
sits between lexical analysis (which only knows about tokens) and semantic analysis
(which only knows about meaning), and its job is to confirm that the input matches
the grammar and to record *how* it matches.

The output of parsing is usually a **parse tree** or, more commonly in real
compilers, an **Abstract Syntax Tree (AST)**. The difference matters: a parse tree
preserves every grammar production, including the boring ones (`expr -> term`,
parentheses, semicolons), while an AST throws away anything that is purely syntactic
clutter and keeps only what represents actual structure. `(1 + 2)` and `1 + 2`
produce different parse trees but the same AST, because the parentheses were only
there to guide the parser, not to carry meaning.

There are several parsing strategies - LL, LR, recursive descent, Pratt parsing,
parser combinators - but for hand-written parsers over small grammars,
**recursive-descent** is by far the most common. Each grammar rule maps to one
function, and the call stack mirrors the structure of the grammar itself. The main
thing to get right is **operator precedence and associativity**, since those decide
the *shape* of the resulting tree, not just whether the input is accepted.


## Objectives

1. Get familiar with parsing, what it is, and how it can be programmed.
2. Get familiar with the concept of AST.
3. In addition to what was done in the 3rd lab work:
    1. Have a `TokenType` enum that can be used in the lexical analysis to
       categorize tokens, identified using regular expressions.
    2. Implement the necessary data structures for an AST that could be used for
       the text processed in the 3rd lab work.
    3. Implement a simple parser that extracts the syntactic information from
       the input text.


## Implementation Description

The domain chosen is **mathematical expressions** with variables, function calls,
and assignments - the same domain extended from Lab 3. The grammar handled is:

```
program     := statement*
statement   := assignment | expr_stmt
assignment  := IDENT '=' expression ';'?
expr_stmt   := expression ';'?

expression  := term (('+' | '-') term)*
term        := factor (('*' | '/' | '%') factor)*
factor      := unary ('^' factor)?          # right-associative
unary       := ('+' | '-') unary | primary
primary     := NUMBER | IDENT | call | '(' expression ')'
call        := (FUNCTION | IDENT) '(' arg_list? ')'
arg_list    := expression (',' expression)*
```

The implementation is split across five files: `token_types.py`, `lexer.py`,
`ast_nodes.py`, `parser.py`, and `main.py`.

### TokenType and Token

The `TokenType` enum lists every category of token the lexer can produce - literals,
operators, delimiters, function keywords, and `EOF`. Using an enum (rather than raw
strings) means the parser can compare token kinds without typos and the IDE catches
mistakes early. `Token` itself is a small dataclass that bundles the type with the
original lexeme and its position in the source string, so error messages can point
at exactly where things went wrong.

```python
class TokenType(Enum):
    INTEGER = auto(); FLOAT = auto(); IDENTIFIER = auto()
    PLUS = auto(); MINUS = auto(); MULTIPLY = auto(); DIVIDE = auto()
    POWER = auto(); MODULO = auto(); ASSIGN = auto()
    LPAREN = auto(); RPAREN = auto(); COMMA = auto(); SEMICOLON = auto()
    FUNCTION = auto(); EOF = auto(); WHITESPACE = auto()

@dataclass
class Token:
    type: TokenType
    value: str
    position: int
```

### Lexer

The lexer uses regular expressions to identify tokens, as required. Rather than
calling `re.match` once per token type in a loop, all patterns are combined into
one master regex with named groups - one alternative per token type. Each match
then directly tells you which type was found via `m.lastgroup`.

The order of patterns inside the master regex matters: longer / more specific
patterns must come first. `FLOAT` (`\d+\.\d+`) has to be tried before `INTEGER`
(`\d+`), otherwise `3.14` would be lexed as `INTEGER 3` followed by `.14`. Same
reasoning for `FUNCTION` before `IDENTIFIER` - the function names `sin`, `cos`,
`sqrt`, etc. would otherwise be swallowed as plain identifiers.

```python
TOKEN_SPEC = [
    (TokenType.WHITESPACE, r"[ \t\n\r]+"),
    (TokenType.FLOAT,      r"\d+\.\d+"),
    (TokenType.INTEGER,    r"\d+"),
    (TokenType.FUNCTION,   r"\b(?:sin|cos|tan|sqrt|log|ln|exp|abs)\b"),
    (TokenType.IDENTIFIER, r"[A-Za-z_][A-Za-z_0-9]*"),
    # ... operators, delimiters
]

_MASTER_PATTERN = re.compile(
    "|".join(f"(?P<{tt.name}>{pat})" for tt, pat in TOKEN_SPEC)
)
```

WHITESPACE is recognized so the lexer can advance past it, but the tokens
themselves are dropped. At the end of input an `EOF` token is appended - this lets
the parser check `_check(EOF)` instead of having to handle index-out-of-range
separately.

### AST nodes

The AST is a small class hierarchy of dataclasses. There are two abstract bases -
`Expression` for things that produce a value, and `Statement` for things that
perform an action - and a `Program` root that holds the list of statements.
Splitting the hierarchy this way means the parser can return the right "shape"
from each rule and Python's type hints stay meaningful.

```
ASTNode (abstract base)
  ├── Expression
  │     ├── NumberLiteral, Identifier
  │     ├── BinaryOp, UnaryOp
  │     └── FunctionCall
  └── Statement
        ├── Assignment
        └── ExpressionStatement
```

Using `@dataclass` for every node was a deliberate choice - the alternative would
have been `__init__` methods on each class, but that adds a lot of boilerplate
when you have eight node types and `@dataclass` already gives you a free
`__repr__` for debugging.

The module also includes a `print_ast` helper that walks the tree recursively and
prints it indented. This is what produces the human-readable output shown in the
results section.

### Parser

The parser is a hand-written **recursive-descent** parser. Each grammar rule maps
to one method, and they call each other to reflect the grammar's structure.
Internally the parser keeps a `pos` index into the token list and exposes four
small helpers: `_peek`, `_advance`, `_check`, `_match`, plus `_expect` which
raises a `ParserError` if the current token isn't what the grammar requires.

The trickiest part was getting **operator precedence and associativity** right.
The standard trick is to layer the rules so each level of the grammar handles one
precedence tier: `expression` handles `+ -` (lowest), `term` handles `* / %`,
`factor` handles `^`, and `unary` handles prefix `+ -`. Each level builds left-leaning
trees by looping (`while self._check(...)`), which gives left-associativity for
free.

```python
def _parse_expression(self):
    node = self._parse_term()
    while self._check(TokenType.PLUS, TokenType.MINUS):
        op = self._advance().value
        right = self._parse_term()
        node = BinaryOp(operator=op, left=node, right=right)
    return node
```

`^` is the exception - it is right-associative, which means `2^3^2` should parse
as `2^(3^2)`, not `(2^3)^2`. Instead of looping, `_parse_factor` recurses into
itself on the right-hand side. That single change flips the associativity:

```python
def _parse_factor(self):
    node = self._parse_unary()
    if self._check(TokenType.POWER):
        op = self._advance().value
        right = self._parse_factor()        # recursion -> right-associative
        node = BinaryOp(operator=op, left=node, right=right)
    return node
```

For statement parsing, the parser uses a **one-token look-ahead** to distinguish
assignments from plain expression statements. If the current token is `IDENTIFIER`
and the next one is `=`, it's an assignment; otherwise it's an expression. Without
look-ahead the parser would have to backtrack, which recursive-descent doesn't do
gracefully.

```python
def _parse_statement(self):
    if (self._peek().type is TokenType.IDENTIFIER
            and self._peek(1).type is TokenType.ASSIGN):
        return self._parse_assignment()
    return self._parse_expression_statement()
```

Function calls have a subtle case worth mentioning: both `FUNCTION` tokens (built-in
names like `sin`, `log`) and `IDENTIFIER` tokens can be followed by `(` to start a
call. The `_parse_primary` method handles both - if it sees an identifier followed
by `(`, it treats it as a call instead of a bare variable reference.


## Conclusions / Results

The program correctly tokenizes and parses every input from the demo set, producing
the expected AST shape in each case. Selected outputs:

**Precedence (`1 + 2 * 3` parses as `1 + (2*3)`):**
```
BinaryOp(op='+')
  left:  NumberLiteral(1)
  right:
    BinaryOp(op='*')
      left:  NumberLiteral(2)
      right: NumberLiteral(3)
```

**Right-associative power (`2 ^ 3 ^ 2` parses as `2 ^ (3 ^ 2)`):**
```
BinaryOp(op='^')
  left:  NumberLiteral(2)
  right:
    BinaryOp(op='^')
      left:  NumberLiteral(3)
      right: NumberLiteral(2)
```

**Assignment with mixed expression (`x = 3.14 * radius ^ 2`):**
```
Assignment
  target: Identifier('x')
  value:
    BinaryOp(op='*')
      left:  NumberLiteral(3.14)
      right:
        BinaryOp(op='^')
          left:  Identifier('radius')
          right: NumberLiteral(2)
```

**Function call with multiple arguments (`log(x, 2) + sqrt(16)`):**
```
BinaryOp(op='+')
  left:
    FunctionCall(name='log')
      arg0: Identifier('x')
      arg1: NumberLiteral(2)
  right:
    FunctionCall(name='sqrt')
      arg0: NumberLiteral(16)
```

The biggest lesson from this lab is that the *shape* of the AST is determined
almost entirely by the structure of the grammar rules in the parser, not by some
separate "precedence table". Once the grammar is layered correctly, precedence and
associativity fall out automatically - and that is exactly why the layered grammar
shown at the top exists in the first place.

The other thing worth noting is how much cleaner the parser became after
introducing the `TokenType` enum. The Lab 3 lexer worked with raw strings, which
meant the parser would have had to compare against string literals everywhere -
fragile and easy to misspell. Switching to enum comparisons made the parser code
read almost like the grammar itself.


## References

1. [Parsing - Wikipedia](https://en.wikipedia.org/wiki/Parsing)
2. [Abstract Syntax Tree - Wikipedia](https://en.wikipedia.org/wiki/Abstract_syntax_tree)
3. [Recursive descent parser - Wikipedia](https://en.wikipedia.org/wiki/Recursive_descent_parser)
