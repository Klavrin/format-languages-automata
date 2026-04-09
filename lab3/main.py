from lexer import Lexer, TokenType

# let x = 42 * 3.14;
# func add(a, b) { return a + b; }
# if (x > 0 && x <= 100) { print("in range"); }

SAMPLES: dict[str, str] = {
    "Variables & Arithmetic": """\
let x = 42;
let pi = 3.14159;
let result = x * pi + 2 ** 8;
""",
    "Strings & Booleans": """\
let greeting = "Hello, World!";
let flag = true;
let nothing = null;
let escaped = 'it\\'s fine';
""",
    "Control Flow": """\
if (x > 0) {
    print("positive");
} else {
    print("non-positive");
}

while (x > 0) {
    x -= 1;
}
""",
    "Functions": """\
func greet(name) {
    let msg = "Hi, " + name + "!";
    return msg;
}

let out = greet("Alice");
print(out);
""",
    "Comments": """\
// This is a single-line comment
let a = 1; // inline comment

/*
  Multi-line comment:
  Everything here is ignored.
*/
let b = 2;
""",
    "Operators Showcase": """\
let a = 10 % 3;
let b = a ** 2;
let c = (a == b) || (a != 0);
let d = !(a >= b) && (b <= 100);
a += 5;
b -= 1;
""",
    "Unknown / Edge Characters": """\
let x = @unknown;
let y = 1 + #2;
""",
}


def run_sample(title: str, source: str, include_comments: bool = True) -> None:
    print(f"\n{'═' * 60}")
    print(f"  SAMPLE: {title}")
    print(f"{'═' * 60}")
    print("SOURCE:\n")
    for i, line in enumerate(source.splitlines(), start=1):
        print(f"  {i:3}  {line}")
    print()

    lexer = Lexer(source, include_comments=include_comments)
    tokens = lexer.tokenize()
    Lexer.pretty_print(tokens)

    # Stats
    types_found = {t.type for t in tokens if t.type not in (TokenType.EOF,)}
    print(f"\n  Total tokens : {len(tokens)}")
    print(f"  Token types  : {len(types_found)}")


def main() -> None:
    print("\n" + "█" * 60)
    print("  TinyScript Lexer — Laboratory Work Demo")
    print("  Formal Languages & Finite Automata")
    print("█" * 60)

    for title, source in SAMPLES.items():
        run_sample(title, source)

    print("\n" + "═" * 60)
    print("  INTERACTIVE MODE  (type 'quit' to exit)")
    print("  Enter TinyScript code line by line.")
    print("  Type an empty line to submit.")
    print("═" * 60)

    while True:
        lines: list[str] = []
        try:
            while True:
                prompt = ">>> " if not lines else "... "
                line = input(prompt)
                if line.lower() == "quit":
                    print("Goodbye!")
                    return
                if line == "" and lines:
                    break
                lines.append(line)
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return

        source = "\n".join(lines)
        if source.strip():
            lexer = Lexer(source, include_comments=True)
            tokens = lexer.tokenize()
            Lexer.pretty_print(tokens)


if __name__ == "__main__":
    main()
