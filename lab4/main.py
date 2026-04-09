import random

MAX_REPEAT = 5
RNG = random.Random()


class NodeType:
    LITERAL = "LITERAL"
    CONCAT = "CONCAT"
    ALTERNATION = "ALTERNATION"
    REPEAT = "REPEAT"


class RegexNode:
    def __init__(self, type_, literal=None, children=None, min_rep=0, max_rep=0):
        self.type = type_
        self.literal = literal
        self.children = children or []
        self.min_rep = min_rep
        self.max_rep = max_rep

    @staticmethod
    def literal_node(s):
        return RegexNode(NodeType.LITERAL, literal=s)

    @staticmethod
    def concat(children):
        return RegexNode(NodeType.CONCAT, children=children)

    @staticmethod
    def alt(children):
        return RegexNode(NodeType.ALTERNATION, children=children)

    @staticmethod
    def repeat(child, min_rep, max_rep):
        return RegexNode(
            NodeType.REPEAT, children=[child], min_rep=min_rep, max_rep=max_rep
        )

    def __repr__(self):
        if self.type == NodeType.LITERAL:
            return f'Literal("{self.literal}")'
        elif self.type == NodeType.CONCAT:
            return f"Concat({self.children})"
        elif self.type == NodeType.ALTERNATION:
            return f"Alt({self.children})"
        elif self.type == NodeType.REPEAT:
            return f"Repeat({self.children[0]}, {self.min_rep}..{self.max_rep})"


class Parser:
    def __init__(self, regex, log):
        self.src = list(regex)
        self.pos = 0
        self.log = log

    def parse_expr(self):
        self._log("parseExpr: looking for alternatives separated by '|'")
        alts = [self.parse_concat()]
        while self.pos < len(self.src) and self.src[self.pos] == "|":
            self.pos += 1
            self._log(f"  found '|' at pos {self.pos - 1}, parsing next alternative")
            alts.append(self.parse_concat())

        if len(alts) == 1:
            return alts[0]

        node = RegexNode.alt(alts)
        self._log(f"  => built ALTERNATION with {len(alts)} branches")
        return node

    def parse_concat(self):
        self._log("  parseConcat: collecting atoms until ')' or '|'")
        seq = []
        while self.pos < len(self.src) and self.src[self.pos] not in [")", "|"]:
            seq.append(self.parse_quantified())

        if not seq:
            return RegexNode.literal_node("")
        if len(seq) == 1:
            return seq[0]
        return RegexNode.concat(seq)

    def parse_quantified(self):
        atom = self.parse_atom()

        if self.pos < len(self.src):
            q = self.src[self.pos]

            if q == "*":
                self.pos += 1
                self._log(f"    quantifier '*' on {atom} -> repeat 0..{MAX_REPEAT}")
                return RegexNode.repeat(atom, 0, MAX_REPEAT)

            if q == "+":
                self.pos += 1
                self._log(f"    quantifier '+' on {atom} -> repeat 1..{MAX_REPEAT}")
                return RegexNode.repeat(atom, 1, MAX_REPEAT)

            exact = self.superscript_value(q)
            if exact > 0:
                self.pos += 1
                self._log(f"    superscript '{q}' on {atom} -> repeat exactly {exact}")
                return RegexNode.repeat(atom, exact, exact)

        return atom

    def parse_atom(self):
        if self.pos >= len(self.src):
            return RegexNode.literal_node("")

        c = self.src[self.pos]

        if c == "(":
            self.pos += 1
            self._log(f"    '(' at pos {self.pos - 1} -> entering group")
            inner = self.parse_expr()
            if self.pos < len(self.src) and self.src[self.pos] == ")":
                self.pos += 1
                self._log("    ')' -> closing group")
            return inner

        self.pos += 1
        self._log(f"    literal '{c}' at pos {self.pos - 1}")
        return RegexNode.literal_node(c)

    def superscript_value(self, c):
        return {"\u00b9": 1, "\u00b2": 2, "\u00b3": 3}.get(c, 0)

    def _log(self, msg):
        self.log.append(msg)


def generate(node):
    if node.type == NodeType.LITERAL:
        return node.literal

    elif node.type == NodeType.CONCAT:
        return "".join(generate(child) for child in node.children)

    elif node.type == NodeType.ALTERNATION:
        return generate(RNG.choice(node.children))

    elif node.type == NodeType.REPEAT:
        if node.min_rep == node.max_rep:
            times = node.min_rep
        else:
            times = RNG.randint(node.min_rep, node.max_rep)

        return "".join(generate(node.children[0]) for _ in range(times))


def generate_samples(regex, count):
    log = []
    root = Parser(regex, log).parse_expr()

    seen = set()
    tries = 0

    while len(seen) < count and tries < count * 50:
        seen.add(generate(root))
        tries += 1

    return list(seen)


if __name__ == "__main__":
    regexes = ["(S|T)(U|V)W*Y+24", "L(M|N)O\u00b3P*Q(2|3)", "R*S(T|U|V)W(X|Y|Z)\u00b2"]

    print("Variant 4\n")

    for i, regex in enumerate(regexes):
        print(f"Regex {i+1} : {regex}\n")

        steps = []
        root = Parser(regex, steps).parse_expr()

        print("Processing sequence:")
        for step in steps:
            print("   ", step)

        print("\nSample generated strings:")
        seen = set()
        tries = 0

        while len(seen) < 10 and tries < 500:
            seen.add(generate(root))
            tries += 1

        for s in seen:
            print("   ", s)

        print()
