from dataclasses import dataclass, field
from typing import List, Union


# -- Base classes ---------------------------------------------------------- #


class ASTNode:
    """Common base class for everything in the tree."""


class Expression(ASTNode):
    """Base for nodes that produce a value."""


class Statement(ASTNode):
    """Base for nodes that perform an action."""


# -- Expression nodes ------------------------------------------------------ #


@dataclass
class NumberLiteral(Expression):
    """A numeric literal — int or float."""

    value: Union[int, float]


@dataclass
class Identifier(Expression):
    """A variable reference, e.g. `x`."""

    name: str


@dataclass
class BinaryOp(Expression):
    """A binary operation, e.g. `a + b`."""

    operator: str  # "+", "-", "*", "/", "^", "%"
    left: Expression
    right: Expression


@dataclass
class UnaryOp(Expression):
    """A unary prefix operation, e.g. `-a`."""

    operator: str  # "+" or "-"
    operand: Expression


@dataclass
class FunctionCall(Expression):
    """A function call, e.g. `sin(x)` or `log(x, 2)`."""

    name: str
    arguments: List[Expression] = field(default_factory=list)


# -- Statement nodes ------------------------------------------------------- #


@dataclass
class Assignment(Statement):
    """A variable assignment, e.g. `x = 1 + 2`."""

    target: Identifier
    value: Expression


@dataclass
class ExpressionStatement(Statement):
    """An expression evaluated for its value, e.g. `1 + 2;`."""

    expression: Expression


# -- Root ------------------------------------------------------------------ #


@dataclass
class Program(ASTNode):
    """The root of the AST — a sequence of statements."""

    statements: List[Statement] = field(default_factory=list)


# -- Pretty-printer -------------------------------------------------------- #


def print_ast(node: ASTNode, indent: int = 0) -> None:
    """Print the AST in an indented, human-readable form.

    This is intentionally simple — it walks the tree, prints the class name
    of each node, then descends into children. Lists are expanded inline.
    """
    pad = "  " * indent
    cls = type(node).__name__

    if isinstance(node, Program):
        print(f"{pad}{cls}")
        for s in node.statements:
            print_ast(s, indent + 1)

    elif isinstance(node, Assignment):
        print(f"{pad}{cls}")
        print(f"{pad}  target:")
        print_ast(node.target, indent + 2)
        print(f"{pad}  value:")
        print_ast(node.value, indent + 2)

    elif isinstance(node, ExpressionStatement):
        print(f"{pad}{cls}")
        print_ast(node.expression, indent + 1)

    elif isinstance(node, BinaryOp):
        print(f"{pad}{cls}(op='{node.operator}')")
        print(f"{pad}  left:")
        print_ast(node.left, indent + 2)
        print(f"{pad}  right:")
        print_ast(node.right, indent + 2)

    elif isinstance(node, UnaryOp):
        print(f"{pad}{cls}(op='{node.operator}')")
        print_ast(node.operand, indent + 1)

    elif isinstance(node, FunctionCall):
        print(f"{pad}{cls}(name='{node.name}')")
        for i, arg in enumerate(node.arguments):
            print(f"{pad}  arg{i}:")
            print_ast(arg, indent + 2)

    elif isinstance(node, NumberLiteral):
        print(f"{pad}{cls}({node.value})")

    elif isinstance(node, Identifier):
        print(f"{pad}{cls}('{node.name}')")

    else:
        print(f"{pad}<unknown node {cls}>")
