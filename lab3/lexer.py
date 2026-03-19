from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterator, List, Optional


class TokenType(Enum):
    # Literals
    INTEGER     = auto()
    FLOAT       = auto()
    STRING      = auto()
    BOOLEAN     = auto()
    NULL        = auto()

    # Identifiers & keywords
    IDENTIFIER  = auto()
    KEYWORD     = auto()

    # Arithmetic operators
    PLUS        = auto()
    MINUS       = auto()
    STAR        = auto()
    SLASH       = auto()
    PERCENT     = auto()
    POWER       = auto()

    # Comparison operators
    EQ          = auto()   # ==
    NEQ         = auto()   # !=
    LT          = auto()   # <
    GT          = auto()   # >
    LTE         = auto()   # <=
    GTE         = auto()   # >=

    # Logical operators
    AND         = auto()   # &&
    OR          = auto()   # ||
    NOT         = auto()   # !

    # Assignment
    ASSIGN      = auto()   # =
    PLUS_ASSIGN = auto()   # +=
    MINUS_ASSIGN= auto()   # -=
    STAR_ASSIGN = auto()   # *=
    SLASH_ASSIGN= auto()   # /=

    # Punctuation
    LPAREN      = auto()   # (
    RPAREN      = auto()   # )
    LBRACE      = auto()   # {
    RBRACE      = auto()   # }
    LBRACKET    = auto()   # [
    RBRACKET    = auto()   # ]
    COMMA       = auto()   # ,
    SEMICOLON   = auto()   # ;
    DOT         = auto()   # .

    # Special
    COMMENT     = auto()
    NEWLINE     = auto()
    EOF         = auto()
    UNKNOWN     = auto()


KEYWORDS = frozenset({
    "if", "else", "while", "for", "func",
    "return", "let", "print", "import",
    "break", "continue", "in",
})


@dataclass(frozen=True)
class Token:
    type:    TokenType
    value:   str
    line:    int
    column:  int

    def __repr__(self) -> str:
        return (
            f"Token({self.type.name:<15} | "
            f"value={self.value!r:<20} | "
            f"line={self.line}, col={self.column})"
        )


class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int) -> None:
        super().__init__(f"[Line {line}, Col {column}] LexerError: {message}")
        self.line   = line
        self.column = column


class Lexer:
    """
    Single-pass lexer for TinyScript.

    Usage:
        lexer  = Lexer(source_code)
        tokens = lexer.tokenize()
    """

    _RULES: list[tuple[re.Pattern, TokenType | None]] = [
        # Whitespace (ignored, but newlines counted in line tracking)
        (re.compile(r'\n'),                                None),          # handled separately
        (re.compile(r'[ \t\r]+'),                          None),          # skip spaces/tabs

        # Comments
        (re.compile(r'//[^\n]*'),                          TokenType.COMMENT),
        (re.compile(r'/\*.*?\*/', re.DOTALL),              TokenType.COMMENT),

        # Float before Integer to avoid partial matches
        (re.compile(r'\d+\.\d+([eE][+-]?\d+)?'),          TokenType.FLOAT),
        (re.compile(r'\d+'),                               TokenType.INTEGER),

        # String literals
        (re.compile(r'"(?:\\.|[^"\\])*"'),                 TokenType.STRING),
        (re.compile(r"'(?:\\.|[^'\\])*'"),                 TokenType.STRING),

        # Boolean / null (checked before identifier)
        (re.compile(r'\btrue\b'),                          TokenType.BOOLEAN),
        (re.compile(r'\bfalse\b'),                         TokenType.BOOLEAN),
        (re.compile(r'\bnull\b'),                          TokenType.NULL),

        # Identifiers & keywords
        (re.compile(r'[A-Za-z_]\w*'),                      TokenType.IDENTIFIER),

        # Compound assignment operators (before single-char ones)
        (re.compile(r'\+='),                               TokenType.PLUS_ASSIGN),
        (re.compile(r'-='),                                TokenType.MINUS_ASSIGN),
        (re.compile(r'\*='),                               TokenType.STAR_ASSIGN),
        (re.compile(r'/='),                                TokenType.SLASH_ASSIGN),

        # Comparison / logical operators
        (re.compile(r'=='),                                TokenType.EQ),
        (re.compile(r'!='),                                TokenType.NEQ),
        (re.compile(r'<='),                                TokenType.LTE),
        (re.compile(r'>='),                                TokenType.GTE),
        (re.compile(r'&&'),                                TokenType.AND),
        (re.compile(r'\|\|'),                              TokenType.OR),

        # Power (before single star)
        (re.compile(r'\*\*'),                              TokenType.POWER),

        # Single-character operators
        (re.compile(r'<'),                                 TokenType.LT),
        (re.compile(r'>'),                                 TokenType.GT),
        (re.compile(r'='),                                 TokenType.ASSIGN),
        (re.compile(r'!'),                                 TokenType.NOT),
        (re.compile(r'\+'),                                TokenType.PLUS),
        (re.compile(r'-'),                                 TokenType.MINUS),
        (re.compile(r'\*'),                                TokenType.STAR),
        (re.compile(r'/'),                                 TokenType.SLASH),
        (re.compile(r'%'),                                 TokenType.PERCENT),

        # Punctuation
        (re.compile(r'\('),                                TokenType.LPAREN),
        (re.compile(r'\)'),                                TokenType.RPAREN),
        (re.compile(r'\{'),                                TokenType.LBRACE),
        (re.compile(r'\}'),                                TokenType.RBRACE),
        (re.compile(r'\['),                                TokenType.LBRACKET),
        (re.compile(r'\]'),                                TokenType.RBRACKET),
        (re.compile(r','),                                 TokenType.COMMA),
        (re.compile(r';'),                                 TokenType.SEMICOLON),
        (re.compile(r'\.'),                                TokenType.DOT),
    ]

    def __init__(self, source: str, *, include_comments: bool = False) -> None:
        self._source          = source
        self._pos             = 0
        self._line            = 1
        self._col             = 1
        self._include_comments = include_comments


    def tokenize(self) -> List[Token]:
        """Return a complete list of tokens (including EOF)."""
        return list(self._stream())

    def token_stream(self) -> Iterator[Token]:
        """Lazy iterator over tokens."""
        yield from self._stream()

    # helpers
    def _stream(self) -> Iterator[Token]:
        src = self._source
        length = len(src)

        while self._pos < length:
            matched = False

            for pattern, tok_type in self._RULES:
                m = pattern.match(src, self._pos)
                if m is None:
                    continue

                matched  = True
                raw      = m.group(0)
                start_col = self._col

                newlines = raw.count('\n')
                if newlines:
                    self._line += newlines
                    self._col   = len(raw) - raw.rfind('\n')
                else:
                    self._col += len(raw)

                self._pos = m.end()

                if tok_type is None:
                    break  # skip whitespace / bare newlines

                if tok_type is TokenType.COMMENT and not self._include_comments:
                    break

                if tok_type is TokenType.IDENTIFIER and raw in KEYWORDS:
                    tok_type = TokenType.KEYWORD

                yield Token(tok_type, raw, self._line, start_col)
                break

            if not matched:
                char = src[self._pos]
                yield Token(TokenType.UNKNOWN, char, self._line, self._col)
                self._pos  += 1
                self._col  += 1

        yield Token(TokenType.EOF, "", self._line, self._col)

    @staticmethod
    def pretty_print(tokens: List[Token]) -> None:
        """Print a formatted table of tokens."""
        header = f"{'#':<5} {'TYPE':<18} {'VALUE':<25} {'LINE':>5} {'COL':>5}"
        sep    = "-" * len(header)
        print(sep)
        print(header)
        print(sep)
        for i, tok in enumerate(tokens):
            print(
                f"{i:<5} {tok.type.name:<18} {tok.value!r:<25} "
                f"{tok.line:>5} {tok.col:>5}"
                if hasattr(tok, "col") else
                f"{i:<5} {tok.type.name:<18} {tok.value!r:<25} "
                f"{tok.line:>5} {tok.column:>5}"
            )
        print(sep)
