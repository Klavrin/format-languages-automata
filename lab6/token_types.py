from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    """Possible types of tokens recognized by the lexer."""

    # Literals
    INTEGER = auto()  # 42
    FLOAT = auto()  # 3.14
    IDENTIFIER = auto()  # variable names: x, foo, bar

    # Operators
    PLUS = auto()  # +
    MINUS = auto()  # -
    MULTIPLY = auto()  # *
    DIVIDE = auto()  # /
    POWER = auto()  # ^
    MODULO = auto()  # %
    ASSIGN = auto()  # =

    # Delimiters
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    COMMA = auto()  # ,
    SEMICOLON = auto()  # ;

    # Keywords (functions)
    FUNCTION = auto()  # sin, cos, sqrt, log, etc.

    # Special tokens
    EOF = auto()  # end of input
    WHITESPACE = auto()  # space/tab — discarded by lexer


@dataclass
class Token:
    """A token produced by the lexer.

    Attributes:
        type: the TokenType category.
        value: the original lexeme (string).
        position: byte offset in the source where this token starts.
    """

    type: TokenType
    value: str
    position: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, pos={self.position})"
