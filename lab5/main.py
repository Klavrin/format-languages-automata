from grammar import Grammar
from cnf_converter import CNFConverter


def build_variant_8():
    vn = ["S", "A", "B", "C"]
    vt = ["a", "d"]
    p = {
        "S": [
            ["d", "B"],
            ["A"],
        ],
        "A": [
            ["d"],
            ["d", "S"],
            ["a", "A", "d", "A", "B"],
        ],
        "B": [
            ["a"],
            ["a", "S"],
            ["A"],
            [],  # ε
        ],
        "C": [
            ["A", "a"],
        ],
    }
    return Grammar(vn, vt, p, "S")


def build_variant_9():
    vn = ["S", "A", "B", "C", "D"]
    vt = ["a", "b"]
    p = {
        "S": [
            ["b", "A"],
            ["B", "C"],
        ],
        "A": [
            ["a"],
            ["a", "S"],
            ["b", "A", "a", "A", "b"],
        ],
        "B": [
            ["A"],
            ["b", "S"],
            ["a", "A", "a"],
        ],
        "C": [
            [],  # ε
            ["A", "B"],
        ],
        "D": [
            ["A", "B"],
        ],
    }
    return Grammar(vn, vt, p, "S")


if __name__ == "__main__":
    g = build_variant_8()
    CNFConverter().to_cnf(g)
