# Laboratory Work 3 — Lexer & Scanner

**Course:** Formal Languages & Finite Automata  
**Author:** *Sergiu Gherasim*  
**Date:** March 2026

---

## Theory

A **lexer** (also called *tokenizer* or *scanner*) is the first stage of a compiler or interpreter pipeline. It performs **lexical analysis**: transforming a raw stream of characters into a flat list of **tokens**, each carrying a *type* (category) and a *value* (the matched text). This process is sometimes split further into:

1. **Scanning** — identifying sequences of characters that belong together (e.g. a number, a string, a word).
2. **Evaluating** — classifying those sequences into typed tokens and optionally computing their semantic value (e.g. converting `"3.14"` to the float `3.14`).

A **lexeme** is the raw matched string, while a **token** bundles the lexeme with its category and source position. Position information (line, column) is essential for producing useful error messages in a real language toolchain.

Lexical rules are most naturally expressed with **regular expressions** or equivalent finite automata. Each rule captures one token type; the lexer tries every rule at the current position and advances past the longest match (the *maximal munch* principle).

---

## Objectives

1. Understand what lexical analysis is.
2. Learn the inner workings of a lexer / scanner / tokenizer.
3. Implement a sample lexer for a non-trivial language and demonstrate its operation.

---

## Language: TinyScript

Rather than the overused calculator example, this laboratory implements a lexer for **TinyScript**, a minimal general-purpose scripting language with:

| Feature | Example |
|---|---|
| Integer literals | `42`, `0` |
| Float literals | `3.14`, `1.5e10` |
| String literals | `"hello"`, `'it\'s fine'` |
| Boolean / null | `true`, `false`, `null` |
| Identifiers | `myVar`, `_count` |
| Keywords | `if else while for func return let print break continue in import null` |
| Arithmetic | `+ - * / % **` |
| Comparison | `== != < > <= >=` |
| Logical | `&& \|\| !` |
| Assignment | `= += -= *= /=` |
| Punctuation | `( ) { } [ ] , ; .` |
| Single-line comments | `// ...` |
| Multi-line comments | `/* ... */` |

### Sample TinyScript program

```
func factorial(n) {
    if (n <= 1) { return 1; }
    return n * factorial(n - 1);
}

let result = factorial(10);
print(result);   // prints 3628800
```

---

## Implementation

### File layout

```
lexer/
├── lexer.py        ← TokenType enum, Token dataclass, Lexer class
├── main.py         ← Demo runner + interactive REPL
└── test_lexer.py   ← pytest unit tests
```

### `TokenType` (enum)

Every possible category of token is a member of the `TokenType` enum (42 members). Using an enum rather than plain strings makes comparisons type-safe and IDE-friendly.

### `Token` (frozen dataclass)

```python
@dataclass(frozen=True)
class Token:
    type:   TokenType
    value:  str    # raw matched text
    line:   int
    column: int
```

Tokens are immutable value objects — no accidental mutation downstream.

### `Lexer` class

The core algorithm lives in `Lexer._stream()`:

```
pos = 0
while pos < len(source):
    for each (regex, token_type) in RULES:
        if regex.match(source, pos):
            emit token, advance pos
            break
    else:
        emit UNKNOWN, advance 1
emit EOF
```

Key design decisions:

- **Rule ordering** — longer / more specific patterns are listed first (e.g. `**` before `*`, `==` before `=`, `true`/`false` before the generic identifier pattern).
- **Maximal munch** — Python's `re.match` anchors at the current position and returns the longest match for the given pattern, so the first matching rule wins without backtracking.
- **Line tracking** — after every match the newline count inside the matched string is used to update `self._line` and `self._col`.
- **Comment filtering** — comments are lexed as real tokens but dropped from output by default; passing `include_comments=True` retains them (useful for syntax-highlighting tools).
- **Keyword promotion** — identifiers are emitted first, then a dictionary lookup promotes them to `KEYWORD` if the value is in the `KEYWORDS` frozenset. This avoids duplicating patterns.

---

## Results

Running `python main.py` produces token tables for six built-in samples:

```
════════════════════════════════════════════════════════════
  SAMPLE: Variables & Arithmetic
════════════════════════════════════════════════════════════
SOURCE:

    1  let x = 42;
    2  let pi = 3.14159;
    3  let result = x * pi + 2 ** 8;

------------------------------------------------------------
#     TYPE               VALUE                      LINE   COL
------------------------------------------------------------
0     KEYWORD            'let'                          1     1
1     IDENTIFIER         'x'                            1     5
2     ASSIGN             '='                            1     7
3     INTEGER            '42'                           1     9
4     SEMICOLON          ';'                            1    11
...
```

All 40+ unit tests in `test_lexer.py` pass:

```
pytest test_lexer.py -v
...
PASSED test_lexer.py::TestLiterals::test_integer
PASSED test_lexer.py::TestLiterals::test_float_scientific
PASSED test_lexer.py::TestOperators::test_power_before_star
PASSED test_lexer.py::TestIntegration::test_eof_always_present
... (all pass)
```

---

## Conclusions

Building this lexer reinforced several key insights:

1. **Regular expressions are sufficient for tokenization** — every token type in TinyScript is describable by a finite automaton (regular language), confirming the theoretical result that lexical structure needs no more than regular power.
2. **Rule ordering is critical** — placing `**` before `*` and `==` before `=` is the practical expression of maximal munch; getting this wrong silently produces wrong token streams.
3. **Position tracking is non-negotiable** in a real tool — every token carrying its `(line, column)` makes error messages actionable instead of cryptic.
4. **Separation of concerns** — splitting lexing from parsing (and later semantic analysis) keeps each phase small and testable in isolation, exactly as the compiler literature recommends.

---

## References

1. LLVM Tutorial — *My First Language Frontend* https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl01.html  
2. Wikipedia — *Lexical analysis* https://en.wikipedia.org/wiki/Lexical_analysis  
3. Python `re` module documentation https://docs.python.org/3/library/re.html
