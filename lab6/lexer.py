import re
from typing import List

from token_types import Token, TokenType


# List of (TokenType, regex pattern) pairs.
# Order matters — longer / more specific patterns must come first.
# For example, FLOAT must be tried before INTEGER, otherwise "3.14" would be
# read as INTEGER 3 followed by something starting with ".14".
TOKEN_SPEC = [
    (TokenType.WHITESPACE, r"[ \t\n\r]+"),
    (TokenType.FLOAT, r"\d+\.\d+"),
    (TokenType.INTEGER, r"\d+"),
    # Functions are recognized by matching a fixed set of names; the parser
    # will treat IDENTIFIER followed by '(' specially anyway, but giving
    # well-known math functions their own type makes diagnostics clearer.
    (TokenType.FUNCTION, r"\b(?:sin|cos|tan|sqrt|log|ln|exp|abs)\b"),
    (TokenType.IDENTIFIER, r"[A-Za-z_][A-Za-z_0-9]*"),
    (TokenType.PLUS, r"\+"),
    (TokenType.MINUS, r"-"),
    (TokenType.MULTIPLY, r"\*"),
    (TokenType.DIVIDE, r"/"),
    (TokenType.POWER, r"\^"),
    (TokenType.MODULO, r"%"),
    (TokenType.ASSIGN, r"="),
    (TokenType.LPAREN, r"\("),
    (TokenType.RPAREN, r"\)"),
    (TokenType.COMMA, r","),
    (TokenType.SEMICOLON, r";"),
]

# Compile one master regex with named groups — this is fast and lets us
# identify the matched alternative in one go.
_MASTER_PATTERN = re.compile(
    "|".join(f"(?P<{tt.name}>{pat})" for tt, pat in TOKEN_SPEC)
)


class LexerError(Exception):
    """Raised when the lexer encounters a character it cannot tokenize."""


class Lexer:
    """Convert source text into a list of Tokens."""

    def __init__(self, source: str) -> None:
        self.source = source

    def tokenize(self) -> List[Token]:
        """Run the lexer over the full source string.

        Returns a list of Tokens ending with an EOF token. WHITESPACE tokens
        are discarded — they are recognized only so we can advance past them.
        """
        tokens: List[Token] = []
        pos = 0
        n = len(self.source)

        while pos < n:
            m = _MASTER_PATTERN.match(self.source, pos)
            if not m:
                raise LexerError(
                    f"Unexpected character {self.source[pos]!r} at position {pos}"
                )

            kind_name = m.lastgroup  # name of the matched alternative
            value = m.group()  # the matched lexeme
            kind = TokenType[kind_name]  # convert back to enum

            if kind is not TokenType.WHITESPACE:
                tokens.append(Token(kind, value, pos))

            pos = m.end()

        tokens.append(Token(TokenType.EOF, "", pos))
        return tokens
