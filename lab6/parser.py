from typing import List

from token_types import Token, TokenType
from ast_nodes import (
    ASTNode,
    Program,
    Statement,
    Expression,
    Assignment,
    ExpressionStatement,
    BinaryOp,
    UnaryOp,
    FunctionCall,
    NumberLiteral,
    Identifier,
)


class ParserError(Exception):
    """Raised when the token stream does not match the grammar."""


class Parser:
    """Recursive-descent parser over a list of Tokens."""

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.pos = 0  # index of the current (unconsumed) token

    # -- Token-stream helpers --------------------------------------------- #

    def _peek(self, offset: int = 0) -> Token:
        """Look at a token without consuming it."""
        return self.tokens[self.pos + offset]

    def _advance(self) -> Token:
        """Consume and return the current token."""
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _check(self, *types: TokenType) -> bool:
        """True if the current token is one of `types`."""
        return self._peek().type in types

    def _match(self, *types: TokenType) -> bool:
        """If the current token matches, consume it and return True."""
        if self._check(*types):
            self._advance()
            return True
        return False

    def _expect(self, type_: TokenType) -> Token:
        """Consume the current token if it matches `type_`, else error."""
        if self._check(type_):
            return self._advance()
        cur = self._peek()
        raise ParserError(
            f"Expected {type_.name} but got {cur.type.name} "
            f"({cur.value!r}) at position {cur.position}"
        )

    # -- Entry point ------------------------------------------------------ #

    def parse(self) -> Program:
        """Parse the whole token stream into a Program."""
        statements: List[Statement] = []
        while not self._check(TokenType.EOF):
            statements.append(self._parse_statement())
        return Program(statements=statements)

    # -- Statements ------------------------------------------------------- #

    def _parse_statement(self) -> Statement:
        """statement := assignment | expr_stmt

        We use a one-token look-ahead: if we see IDENT followed by '=',
        it's an assignment; otherwise it's a plain expression statement.
        """
        if (
            self._peek().type is TokenType.IDENTIFIER
            and self._peek(1).type is TokenType.ASSIGN
        ):
            return self._parse_assignment()
        return self._parse_expression_statement()

    def _parse_assignment(self) -> Assignment:
        name_tok = self._expect(TokenType.IDENTIFIER)
        self._expect(TokenType.ASSIGN)
        value = self._parse_expression()
        self._match(TokenType.SEMICOLON)  # optional terminator
        return Assignment(target=Identifier(name=name_tok.value), value=value)

    def _parse_expression_statement(self) -> ExpressionStatement:
        expr = self._parse_expression()
        self._match(TokenType.SEMICOLON)
        return ExpressionStatement(expression=expr)

    # -- Expressions (precedence climbing) -------------------------------- #

    def _parse_expression(self) -> Expression:
        """expression := term (('+'|'-') term)*"""
        node = self._parse_term()
        while self._check(TokenType.PLUS, TokenType.MINUS):
            op = self._advance().value
            right = self._parse_term()
            node = BinaryOp(operator=op, left=node, right=right)
        return node

    def _parse_term(self) -> Expression:
        """term := factor (('*'|'/'|'%') factor)*"""
        node = self._parse_factor()
        while self._check(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op = self._advance().value
            right = self._parse_factor()
            node = BinaryOp(operator=op, left=node, right=right)
        return node

    def _parse_factor(self) -> Expression:
        """factor := unary ('^' factor)?

        '^' is right-associative, so we recurse into _parse_factor on the
        right-hand side instead of looping.
        """
        node = self._parse_unary()
        if self._check(TokenType.POWER):
            op = self._advance().value
            right = self._parse_factor()  # right-associative
            node = BinaryOp(operator=op, left=node, right=right)
        return node

    def _parse_unary(self) -> Expression:
        """unary := ('+'|'-') unary | primary"""
        if self._check(TokenType.PLUS, TokenType.MINUS):
            op = self._advance().value
            operand = self._parse_unary()
            return UnaryOp(operator=op, operand=operand)
        return self._parse_primary()

    def _parse_primary(self) -> Expression:
        """primary := NUMBER | IDENT | call | '(' expression ')'"""
        tok = self._peek()

        # Numeric literal
        if tok.type is TokenType.INTEGER:
            self._advance()
            return NumberLiteral(value=int(tok.value))
        if tok.type is TokenType.FLOAT:
            self._advance()
            return NumberLiteral(value=float(tok.value))

        # Function call (recognized FUNCTION keyword) — must be followed by '('
        if tok.type is TokenType.FUNCTION:
            self._advance()
            self._expect(TokenType.LPAREN)
            args = self._parse_argument_list()
            self._expect(TokenType.RPAREN)
            return FunctionCall(name=tok.value, arguments=args)

        # Identifier — could be a plain variable or a user-named call
        if tok.type is TokenType.IDENTIFIER:
            self._advance()
            if self._check(TokenType.LPAREN):
                self._advance()  # consume '('
                args = self._parse_argument_list()
                self._expect(TokenType.RPAREN)
                return FunctionCall(name=tok.value, arguments=args)
            return Identifier(name=tok.value)

        # Parenthesized sub-expression
        if tok.type is TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN)
            return expr

        raise ParserError(
            f"Unexpected token {tok.type.name} ({tok.value!r}) "
            f"at position {tok.position}"
        )

    def _parse_argument_list(self) -> List[Expression]:
        """arg_list := (expression (',' expression)*)?

        Returns [] if the next token is ')' (empty arg list).
        """
        args: List[Expression] = []
        if self._check(TokenType.RPAREN):
            return args
        args.append(self._parse_expression())
        while self._match(TokenType.COMMA):
            args.append(self._parse_expression())
        return args
