import re
from Belief_base.formula import Implies, Or, Not, Atom, Formula, And, Equiv

TOKENS = {
    "NOT": "¬",
    "AND": "∧",
    "OR": "∨",
    "IMP": "→",
    "EQU": "↔",
    "LPAREN": "(",
    "RPAREN": ")"
}

def _tokenize(expr: str):
    """Split input into tokens: parentheses, connectives, atoms."""
    # match any of →, ↔, ¬, ∧, ∨, parentheses or alphanumeric names
    pattern = r"\s*(→|↔|¬|∧|∨|\(|\)|[A-Za-z0-9]+)\s*"
    tokens = re.findall(pattern, expr)
    return tokens

def parse_formula(s: str) -> Formula:
    """Recursive-descent parser handling parentheses depth and edge cases."""
    tokens = _tokenize(s)
    # We'll parse equivalences → implications → OR → AND → NOT → atoms

    def parse_equiv(index=0):
        node, index = parse_imp(index)
        while index < len(tokens) and tokens[index] == TOKENS["EQU"]:
            index += 1
            right_node, index = parse_imp(index)
            node = Equiv(node, right_node)
        return node, index

    def parse_imp(index=0):
        node, index = parse_or(index)
        while index < len(tokens) and tokens[index] == TOKENS["IMP"]:
            index += 1
            right_node, index = parse_or(index)
            node = Implies(node, right_node)
        return node, index

    def parse_or(index=0):
        node, index = parse_and(index)
        while index < len(tokens) and tokens[index] == TOKENS["OR"]:
            index += 1
            right_node, index = parse_and(index)
            node = Or(node, right_node)
        return node, index

    def parse_and(index=0):
        node, index = parse_not(index)
        while index < len(tokens) and tokens[index] == TOKENS["AND"]:
            index += 1
            right_node, index = parse_not(index)
            node = And(node, right_node)
        return node, index

    def parse_not(index=0):
        while index < len(tokens) and tokens[index] == TOKENS["NOT"]:
            index += 1
            sub_node, index = parse_not(index)
            return Not(sub_node), index
        return parse_atom(index)

    def parse_atom(index=0):
        if index >= len(tokens):
            raise ValueError("Unexpected end of tokens.")
        t = tokens[index]
        if t == TOKENS["LPAREN"]:
            node, new_idx = parse_equiv(index+1)
            if new_idx >= len(tokens) or tokens[new_idx] != TOKENS["RPAREN"]:
                raise ValueError("Missing closing parenthesis.")
            return node, new_idx+1
        elif re.fullmatch(r"[a-zA-Z0-9]+", t):
            return Atom(t), index+1
        else:
            raise ValueError(f"Unexpected token: {t}")

    root, next_pos = parse_equiv()
    if next_pos != len(tokens):
        raise ValueError(f"Extra tokens after parsing: {tokens[next_pos:]}")
    
    # remove or comment out the debug print below
    # print(f"Parsed formula: {root}")
    
    return root


def parse_file(file_path: str) -> list[tuple[Formula, int]]:
    """
    Parses a file with each line formatted as: formula ; priority
    Returns a list of (Formula, priority) tuples.
    """
    results = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                if ";" in line:
                    formula_str, priority_str = line.split(";")
                    formula = parse_formula(formula_str.strip())
                    priority = int(priority_str.strip())
                    results.append((formula, priority))
                else:
                    # default priority 0 if missing
                    formula = parse_formula(line)
                    results.append((formula, 0))
            except Exception as e:
                print(f"Error parsing '{line}': {e}")
                continue
    return results
