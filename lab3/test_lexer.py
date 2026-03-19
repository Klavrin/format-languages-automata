import pytest
from lexer import Lexer, Token, TokenType, LexerError


def lex(src: str, include_comments: bool = False) -> list[Token]:
    tokens = Lexer(src, include_comments=include_comments).tokenize()
    return [t for t in tokens if t.type != TokenType.EOF]


def types(src: str, **kw) -> list[TokenType]:
    return [t.type for t in lex(src, **kw)]


def values(src: str, **kw) -> list[str]:
    return [t.value for t in lex(src, **kw)]


class TestLiterals:
    def test_integer(self):
        assert types("42") == [TokenType.INTEGER]
        assert values("42") == ["42"]

    def test_float(self):
        assert types("3.14") == [TokenType.FLOAT]
        assert values("3.14") == ["3.14"]

    def test_float_scientific(self):
        assert types("1.5e10") == [TokenType.FLOAT]

    def test_string_double_quote(self):
        assert types('"hello"') == [TokenType.STRING]
        assert values('"hello"') == ['"hello"']

    def test_string_single_quote(self):
        assert types("'world'") == [TokenType.STRING]

    def test_string_escaped(self):
        assert types(r'"say \"hi\""') == [TokenType.STRING]

    def test_boolean_true(self):
        assert types("true") == [TokenType.BOOLEAN]

    def test_boolean_false(self):
        assert types("false") == [TokenType.BOOLEAN]

    def test_null(self):
        assert types("null") == [TokenType.NULL]


class TestIdentifiersAndKeywords:
    def test_identifier(self):
        assert types("myVar") == [TokenType.IDENTIFIER]

    def test_underscore_identifier(self):
        assert types("_private") == [TokenType.IDENTIFIER]

    def test_keyword_let(self):
        assert types("let") == [TokenType.KEYWORD]

    def test_keyword_if(self):
        assert types("if") == [TokenType.KEYWORD]

    def test_keyword_func(self):
        assert types("func") == [TokenType.KEYWORD]

    def test_identifier_not_keyword(self):
        # "letter" starts with "let" but is not a keyword
        assert types("letter") == [TokenType.IDENTIFIER]
        assert values("letter") == ["letter"]


class TestOperators:
    def test_arithmetic(self):
        result = types("+ - * / % **")
        assert result == [
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.STAR,
            TokenType.SLASH,
            TokenType.PERCENT,
            TokenType.POWER,
        ]

    def test_comparison(self):
        result = types("== != < > <= >=")
        assert result == [
            TokenType.EQ,
            TokenType.NEQ,
            TokenType.LT,
            TokenType.GT,
            TokenType.LTE,
            TokenType.GTE,
        ]

    def test_logical(self):
        result = types("&& || !")
        assert result == [TokenType.AND, TokenType.OR, TokenType.NOT]

    def test_assignment(self):
        result = types("= += -= *= /=")
        assert result == [
            TokenType.ASSIGN,
            TokenType.PLUS_ASSIGN,
            TokenType.MINUS_ASSIGN,
            TokenType.STAR_ASSIGN,
            TokenType.SLASH_ASSIGN,
        ]

    def test_power_before_star(self):
        result = types("2**3")
        assert result == [TokenType.INTEGER, TokenType.POWER, TokenType.INTEGER]


class TestPunctuation:
    def test_all_punct(self):
        result = types("( ) { } [ ] , ; .")
        assert result == [
            TokenType.LPAREN,
            TokenType.RPAREN,
            TokenType.LBRACE,
            TokenType.RBRACE,
            TokenType.LBRACKET,
            TokenType.RBRACKET,
            TokenType.COMMA,
            TokenType.SEMICOLON,
            TokenType.DOT,
        ]


class TestComments:
    def test_single_line_comment_excluded(self):
        result = types("let x = 1; // comment")
        assert TokenType.COMMENT not in result

    def test_single_line_comment_included(self):
        result = types("let x = 1; // comment", include_comments=True)
        assert TokenType.COMMENT in result

    def test_multiline_comment(self):
        src = "let a = /* ignored */ 5;"
        result = types(src)
        assert TokenType.COMMENT not in result
        assert TokenType.INTEGER in result

    def test_multiline_comment_included(self):
        src = "/* block */"
        result = types(src, include_comments=True)
        assert result == [TokenType.COMMENT]


class TestPositionTracking:
    def test_line_tracking(self):
        tokens = Lexer("a\nb\nc").tokenize()
        lines = [t.line for t in tokens if t.type == TokenType.IDENTIFIER]
        assert lines == [1, 2, 3]

    def test_column_tracking(self):
        tokens = Lexer("let x = 1;").tokenize()
        by_type = {t.type: t for t in tokens}
        assert by_type[TokenType.KEYWORD].column == 1
        assert by_type[TokenType.IDENTIFIER].column == 5


class TestUnknown:
    def test_unknown_char(self):
        result = types("@")
        assert result == [TokenType.UNKNOWN]

    def test_unknown_does_not_stop_lexer(self):
        result = types("1 @ 2")
        assert TokenType.INTEGER in result
        assert TokenType.UNKNOWN in result


class TestIntegration:
    def test_variable_declaration(self):
        result = types("let count = 0;")
        assert result == [
            TokenType.KEYWORD,
            TokenType.IDENTIFIER,
            TokenType.ASSIGN,
            TokenType.INTEGER,
            TokenType.SEMICOLON,
        ]

    def test_function_call(self):
        result = types("print(x);")
        assert result == [
            TokenType.KEYWORD,  # 'print' is a keyword
            TokenType.LPAREN,
            TokenType.IDENTIFIER,
            TokenType.RPAREN,
            TokenType.SEMICOLON,
        ]

    def test_if_else(self):
        src = "if (x > 0) { return true; } else { return false; }"
        toks = lex(src)
        keywords = [t.value for t in toks if t.type == TokenType.KEYWORD]
        assert "if" in keywords
        assert "else" in keywords
        assert "return" in keywords

    def test_eof_always_present(self):
        tokens = Lexer("").tokenize()
        assert tokens[-1].type == TokenType.EOF

    def test_empty_source(self):
        tokens = Lexer("").tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF
