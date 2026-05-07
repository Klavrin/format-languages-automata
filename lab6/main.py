import sys

from lexer import Lexer, LexerError
from parser import Parser, ParserError
from ast_nodes import print_ast


# A few inputs that exercise different parts of the grammar.
DEMO_INPUTS = [
    "1 + 2 * 3",  # precedence: should give 1 + (2*3)
    "(1 + 2) * 3",  # parentheses override precedence
    "2 ^ 3 ^ 2",  # right-associative power: 2^(3^2)
    "-x + 4",  # unary minus
    "x = 3.14 * radius ^ 2",  # assignment with float and ident
    "result = sin(x) + cos(y) * 2",  # function calls
    "log(x, 2) + sqrt(16)",  # multi-arg function
    "a = 1; b = 2; a + b",  # multiple statements
]


def run(source: str) -> None:
    """Lex, parse, and pretty-print one input."""
    print("=" * 70)
    print(f"Input: {source}")
    print("-" * 70)

    # -- Lex --
    try:
        tokens = Lexer(source).tokenize()
    except LexerError as e:
        print(f"Lexer error: {e}")
        return

    print("Tokens:")
    for t in tokens:
        print(f"  {t}")

    # -- Parse --
    try:
        ast = Parser(tokens).parse()
    except ParserError as e:
        print(f"Parser error: {e}")
        return

    print("\nAST:")
    print_ast(ast)
    print()


def main() -> None:
    if len(sys.argv) > 1:
        # Use command-line argument as a single input
        run(" ".join(sys.argv[1:]))
    else:
        # Run the built-in demo set
        for src in DEMO_INPUTS:
            run(src)


if __name__ == "__main__":
    main()
