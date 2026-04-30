from collections import deque
from grammar import Grammar


class CNFConverter:
    def __init__(self):
        self.fresh_counter = 0

    def to_cnf(self, g):
        print("ORIGINAL GRAMMAR")
        print(g)

        s1 = self.eliminate_epsilon_productions(g)
        print("STEP 1: Eliminate epsilon-productions")
        print(s1)

        s2 = self.eliminate_renaming_rules(s1)
        print("STEP 2: Eliminate renaming (unit) rules")
        print(s2)

        s3 = self.eliminate_inaccessible_symbols(s2)
        print("STEP 3: Eliminate inaccessible symbols")
        print(s3)

        s4 = self.eliminate_non_productive_symbols(s3)
        print("STEP 4: Eliminate non-productive symbols")
        print(s4)

        s5 = self.to_proper_cnf(s4)
        print("STEP 5: Chomsky Normal Form")
        print(s5)

        return s5

    # ---------------- STEP 1: epsilon ----------------
    def eliminate_epsilon_productions(self, g):
        nullable = self._find_nullable(g)
        new_prods = {}

        for lhs, rules in g.get_productions().items():
            expanded = []
            seen = set()
            for rhs in rules:
                for variant in self._expand_nullable(rhs, nullable):
                    key = tuple(variant)
                    if key not in seen:
                        seen.add(key)
                        expanded.append(variant)
            # remove empty production
            expanded = [r for r in expanded if r]
            if expanded:
                new_prods[lhs] = expanded

        if g.get_start_symbol() in nullable:
            new_prods.setdefault(g.get_start_symbol(), []).append([])

        return Grammar(
            g.get_non_terminals(), g.get_terminals(), new_prods, g.get_start_symbol()
        )

    def _find_nullable(self, g):
        nullable = set()
        for lhs, rules in g.get_productions().items():
            for rhs in rules:
                if not rhs:
                    nullable.add(lhs)
        changed = True
        while changed:
            changed = False
            for lhs, rules in g.get_productions().items():
                if lhs in nullable:
                    continue
                for rhs in rules:
                    if rhs and all(sym in nullable for sym in rhs):
                        if lhs not in nullable:
                            nullable.add(lhs)
                            changed = True
                        break
        return nullable

    def _expand_nullable(self, rhs, nullable):
        # Produce all variants where each nullable symbol is optionally omitted
        result = [list(rhs)]
        for i in range(len(rhs)):
            if rhs[i] in nullable:
                next_result = []
                seen = set()
                for existing in result:
                    key = tuple(existing)
                    if key not in seen:
                        seen.add(key)
                        next_result.append(existing)
                    if i < len(existing):
                        omitted = existing[:i] + existing[i + 1 :]
                        # Note: original Java code removes by index i; we mimic that semantics
                        # by reconstructing without the i-th position when within bounds.
                        key2 = tuple(omitted)
                        if key2 not in seen:
                            seen.add(key2)
                            next_result.append(omitted)
                result = next_result
        return result

    # ---------------- STEP 2: unit rules ----------------
    def eliminate_renaming_rules(self, g):
        new_prods = {}
        non_terminals = set(g.get_non_terminals())
        for nt in g.get_non_terminals():
            expanded = []
            seen = set()
            for reachable in self._unit_closure(nt, g):
                for rhs in g.get_productions().get(reachable, []):
                    # skip unit rules (single nonterminal RHS)
                    if len(rhs) == 1 and rhs[0] in non_terminals:
                        continue
                    key = tuple(rhs)
                    if key not in seen:
                        seen.add(key)
                        expanded.append(list(rhs))
            if expanded:
                new_prods[nt] = expanded
        return Grammar(
            g.get_non_terminals(), g.get_terminals(), new_prods, g.get_start_symbol()
        )

    def _unit_closure(self, start, g):
        non_terminals = set(g.get_non_terminals())
        visited = []
        visited_set = set()
        queue = deque([start])
        while queue:
            cur = queue.popleft()
            if cur in visited_set:
                continue
            visited_set.add(cur)
            visited.append(cur)
            for rhs in g.get_productions().get(cur, []):
                if len(rhs) == 1 and rhs[0] in non_terminals:
                    queue.append(rhs[0])
        return visited

    # ---------------- STEP 3: inaccessible ----------------
    def eliminate_inaccessible_symbols(self, g):
        non_terminals = set(g.get_non_terminals())
        accessible = []
        accessible_set = set()
        queue = deque([g.get_start_symbol()])
        while queue:
            cur = queue.popleft()
            if cur in accessible_set:
                continue
            accessible_set.add(cur)
            accessible.append(cur)
            for rhs in g.get_productions().get(cur, []):
                for sym in rhs:
                    if sym in non_terminals:
                        queue.append(sym)

        new_nts = [nt for nt in g.get_non_terminals() if nt in accessible_set]
        new_prods = {}
        for nt in new_nts:
            if nt in g.get_productions():
                new_prods[nt] = [list(r) for r in g.get_productions()[nt]]
        return Grammar(new_nts, g.get_terminals(), new_prods, g.get_start_symbol())

    # ---------------- STEP 4: non-productive ----------------
    def eliminate_non_productive_symbols(self, g):
        terminals_set = set(g.get_terminals())
        productive = set(terminals_set)
        changed = True
        while changed:
            changed = False
            for lhs, rules in g.get_productions().items():
                if lhs in productive:
                    continue
                for rhs in rules:
                    if not rhs or all(sym in productive for sym in rhs):
                        if lhs not in productive:
                            productive.add(lhs)
                            changed = True
                            break

        new_nts = [nt for nt in g.get_non_terminals() if nt in productive]
        new_prods = {}
        for nt in new_nts:
            filtered = []
            for rhs in g.get_productions().get(nt, []):
                if all(sym in terminals_set or sym in productive for sym in rhs):
                    filtered.append(list(rhs))
            if filtered:
                new_prods[nt] = filtered
        return Grammar(new_nts, g.get_terminals(), new_prods, g.get_start_symbol())

    # ---------------- STEP 5: proper CNF ----------------
    def to_proper_cnf(self, g):
        nts = list(g.get_non_terminals())
        nts_set = set(nts)
        ts = list(g.get_terminals())
        ts_set = set(ts)
        prods = {k: [list(rhs) for rhs in v] for k, v in g.get_productions().items()}
        start = g.get_start_symbol()
        new_start = start

        # START: only if start appears on some RHS, introduce S0 and retire old S
        start_on_rhs = any(start in rhs for rules in prods.values() for rhs in rules)
        if start_on_rhs:
            new_start = self._fresh_symbol("S0", nts_set)
            nts.append(new_start)
            nts_set.add(new_start)

            # S0 gets exactly S's rules
            copied_rules = [list(rhs) for rhs in prods.get(start, [])]
            prods[new_start] = copied_rules

            # Replace S with S0 everywhere on RHS
            for rules in prods.values():
                for rhs in rules:
                    for i in range(len(rhs)):
                        if rhs[i] == start:
                            rhs[i] = new_start

            # Remove old S
            if start in prods:
                del prods[start]
            if start in nts_set:
                nts.remove(start)
                nts_set.remove(start)

        # TERM: replace terminals in mixed rules with wrapper nonterminals
        term_map = {}
        for lhs in list(prods.keys()):
            new_rules = []
            for rhs in prods[lhs]:
                if len(rhs) <= 1:
                    new_rules.append(rhs)
                    continue
                new_rhs = []
                for sym in rhs:
                    if sym in ts_set:
                        if sym not in term_map:
                            name = self._fresh_symbol("T_" + sym.upper(), nts_set)
                            nts.append(name)
                            nts_set.add(name)
                            term_map[sym] = name
                        new_rhs.append(term_map[sym])
                    else:
                        new_rhs.append(sym)
                new_rules.append(new_rhs)
            prods[lhs] = new_rules

        for term, wrapper in term_map.items():
            prods[wrapper] = [[term]]

        # BIN: binarize, sharing intermediate nonterminals for identical suffixes
        suffix_cache = {}
        bin_prods = {}
        for lhs in list(prods.keys()):
            for rhs in prods[lhs]:
                if len(rhs) <= 2:
                    bin_prods.setdefault(lhs, []).append(list(rhs))
                else:
                    self._binarize(
                        lhs, list(rhs), nts, nts_set, bin_prods, suffix_cache
                    )

        return Grammar(nts, ts, bin_prods, new_start)

    def _binarize(self, lhs, symbols, nts, nts_set, prods, suffix_cache):
        if len(symbols) <= 2:
            prods.setdefault(lhs, []).append(list(symbols))
            return
        suffix = tuple(symbols[1:])
        if suffix not in suffix_cache:
            name = self._fresh_symbol(lhs + "1", nts_set)
            nts.append(name)
            nts_set.add(name)
            suffix_cache[suffix] = name
        fresh = suffix_cache[suffix]
        prods.setdefault(lhs, []).append([symbols[0], fresh])
        if fresh not in prods:
            self._binarize(fresh, list(suffix), nts, nts_set, prods, suffix_cache)

    def _fresh_symbol(self, base, existing):
        candidate = base
        while candidate in existing:
            self.fresh_counter += 1
            candidate = base + str(self.fresh_counter)
        return candidate
