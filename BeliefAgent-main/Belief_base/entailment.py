from typing import List, Set, Tuple
from Belief_base.formula import Formula, And, Or, Not, Atom
# from Belief_base.belief_base import BeliefBase
from itertools import combinations

# Literal is for (atom name, is_positive) example: ("p", False) means ¬p
Literal = Tuple[str, bool]
# Clause is the frozenset of literals
Clause  = frozenset[Literal]

# We need this tautology check because if not, our resolution algorithm will treat every tautology as a contradiction, which is wrong
# So we need this method to filter out tautologies from the clauses
def is_tautology(clause: Clause) -> bool:
    # clause is a frozenset of (symbol, is_positive) pairs
    syms = {}
    for sym, pos in clause:
        if sym in syms and syms[sym] != pos:
            # we’ve seen the same symbol with the opposite polarity
            return True
        syms[sym] = pos
    return False

""" 
Something like this:

And(
  Or(Atom("p"), Not(Atom("q"))),   # clause 1: p ∨ ¬q
  Atom("r")                        # clause 2: r
)

Will give 

[
  frozenset({("p", True),  ("q", False)}),
  frozenset({("r", True)})
]

via extract_clauses()

"""
def extract_clauses(formula: Formula) -> List[Clause]:
    # print("Extraction started for formula:", formula)
    # Double check if the formula is in CNF
    cnf = formula.to_cnf()
    # print("CNF form:", cnf)
    
    # If the formula has ∧, break up the conjunction into separate clauses
    if isinstance(cnf, And):
        # Example: And(Or(p,q), Or(r,s)) becomes [Or(p,q), Or(r,s)]
        subformulas = list(cnf.formulas)
    else:
        # If there is no ∧, treat the whole formula as a single clause
        subformulas = [cnf]
        
    # Create empty formula list 
    clauses: List[Clause] = []
    
    # Now we split up the subformulas based on the ∨ operator
    for sub in subformulas:
        # If there is an or operator, that means we have a clause with multiple literals like Or(p, Not(q)) has p and ¬q, 2 literals
        # Example: Or(p, Not(q)) becomes [p, ¬q]
        if isinstance(sub, Or):
            disjunctions = list(sub.formulas)
        else:
            # If there is no or operator, then we have a unit clause like Atom("p") or Not(Atom("q")) which is a single literal
            disjunctions = [sub]
            
        # set of literals to turn each disjunction into a (atom, is_positive) tuple
        lits: Set[Literal] = set()
        
        # Loop through each literal in the disjunctions list
        for lit in disjunctions:
            # Check if the literal is true
            if isinstance(lit, Atom):
                lits.add((lit.name, True))  # Positive literal
            # Check if the literal is a negation (false) and that it is an atom
            elif isinstance(lit, Not) and isinstance(lit.formula, Atom):
                lits.add((lit.formula.name, False))
            else:
                # In every proper CNF, every literal must be either an Atom or Not(Atom)
                raise ValueError(f"Non literal in clause: {lit}")
            
        # Finally add the set of literals to the clauses list as a frozenset
        clauses.append(frozenset(lits)) 
    
    return clauses

"""
beliefs = [
    Or(Not(Atom("p")), Atom("q")),  # represents (¬p ∨ q)
    Atom("p")                        # represents (p)
]
"""

# Query the clauses where we 
def cnf_clauses_for_query(kb, query) -> List[Clause]:
    from Belief_base.belief_base import BeliefBase
    all_clauses: List[Clause] = []
    
    # Iterate through each belief in the belief base
    # 1st iteration example: belief = Or(Not(Atom("p")), Atom("q"))
    # Extract_clauses recognizes the OR and builds set frozenset({ ("p", False), ("q", True) })
    # 2nd iteration example: belief = Atom("p")
    # Extract_clauses recognizes the single atom and builds set frozenset({ ("p", True) })
    for belief in kb.get_beliefs():
        # For each belief formula, get each 
        all_clauses.extend(extract_clauses(belief))
    
    # Negate the φ and convert to cnf
    neg_query = Not(query).to_cnf()
    
    # Add the negated φ to the clauses list (because resolution works by proof of contradition), so the final all_clauses in our example becomes: 
    all_clauses.extend(extract_clauses(neg_query))
    
    """ 
    [
            frozenset({ ("p", False), ("q", True) }),   # (¬p ∨ q)   from Implies(p, q)
            frozenset({ ("p", True) }),                 # (p)        from Atom(p)
            frozenset({ ("q", False) })                  # (¬q)       from ¬query
        ] 
        
        """
        
    # DROP ALL CLAUSES THAT ARE TAUTOLOGIES OR ELSE THE CONSISTENCY POSTULATE WILL FAIL
    return [c for c in all_clauses if not is_tautology(c)]

# Method that takes in the belief base, query (phi) to check if the belief base entails the query kb ⊨ query?
def resolution_entails(kb, query) -> bool:
    from Belief_base.belief_base import BeliefBase
    # Turn everything into clauses and cnf_clauses_for_query will also negate the query and return frozensets of literals
    clauses = set(cnf_clauses_for_query(kb, query))

    # new_clauses to store any new clauses generated during resolution
    new_clauses = set()
    while True:
        # Loop over all pairs of existing clauses
        # We try to resolve each pair -- that is, find complementary pairs like p and ¬p so that they cancel out
        for C1, C2 in combinations(clauses, 2):
            # For each literal (symbol, is_positive) in C1, check if the opposite literal exists in C2
            # Example: C1 = [("p", False), ("q", True)] and C2 = [("p", True)]
            for (sym, pos) in C1:
                # We take the first element ("p", False) and define pair comp as ("p", True)
                comp = (sym, not pos)
                # If ("p", True) is in C2 (in our example it is), we can resolve C1 and C2
                if comp in C2:
                    # C1 | C2 is the set union between C1 and C2 combining all literals
                    # So in our example, that would be {("p", False), ("q", True), ("p", True)} and we take
                    # this and remove the complementary pair in our case ("p", True) and ("p", False)
                    # and we are left with only ("q", True)
                    R = frozenset((C1 | C2) - {(sym,pos), comp})
                    # If the set is empty, that means we have derived the empty clause, which means we have a contradiction
                    # and therefore the original query is entailed by the belief base
                    if len(R) == 0:
                        return True
                    # If the set is not empty, we add it to the new_clauses set
                    new_clauses.add(R)
                    
        # Below we add new_clauses to clauses and so if new_clauses is a subset of clauses, that means we have not made any new unique pair
        # and so KB ⊭ query
        if new_clauses.issubset(clauses):
            return False
        
        # Add new_clauses to clauses
        clauses |= new_clauses
