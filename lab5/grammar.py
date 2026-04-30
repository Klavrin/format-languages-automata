class Grammar:
    def __init__(self, non_terminals, terminals, productions, start_symbol):
        # Preserve insertion order via dict.fromkeys / dict copies
        self.non_terminals = dict.fromkeys(non_terminals)
        self.terminals = dict.fromkeys(terminals)
        # productions: dict mapping str -> list of list of str
        self.productions = {k: [list(rhs) for rhs in v] for k, v in productions.items()}
        self.start_symbol = start_symbol

    def get_non_terminals(self):
        return list(self.non_terminals.keys())

    def get_terminals(self):
        return list(self.terminals.keys())

    def get_productions(self):
        return self.productions

    def get_start_symbol(self):
        return self.start_symbol

    def __str__(self):
        lines = []
        lines.append(f"V_N = [{', '.join(self.get_non_terminals())}]")
        lines.append(f"V_T = [{', '.join(self.get_terminals())}]")
        lines.append(f"S   = {self.start_symbol}")
        lines.append("P:")
        for lhs, rules in self.productions.items():
            for rhs in rules:
                rhs_str = "ε" if not rhs else " ".join(rhs)
                lines.append(f"  {lhs} -> {rhs_str}")
        return "\n".join(lines) + "\n"
