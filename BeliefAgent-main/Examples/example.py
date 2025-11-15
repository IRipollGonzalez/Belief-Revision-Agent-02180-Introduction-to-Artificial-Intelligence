from Belief_base.belief_base import BeliefBase
from Belief_base.formula import Implies, Or, Not, Atom
from Belief_base.entailment import cnf_clauses_for_query
from Belief_base.entailment import resolution_entails
from Agent.agent import BeliefRevisionAgent
from Belief_base.parser import parse_file

def test_contraction():
    agent = BeliefRevisionAgent()
    p, q, r = Atom("p"), Atom("q"), Atom("r")

    agent.base.add(Implies(p, q), priority=2)   # ¬p ∨ q
    agent.base.add(p, priority=1)               # p
    agent.base.add(Or(Not(q), r), priority=3)   # ¬q ∨ r

    print("Before contraction:")
    print(agent.base)

    agent.contract_partial_meet(q)

    print("\nAfter contraction by q:")
    print(agent.base)

def test_resolution():
    KB = BeliefBase()
    p, q = Atom("p"), Atom("q")
    
    KB.add(Implies(p, q), priority=1)
    KB.add(p, priority=0)
    
    query = q  # test if KB ⊨ q
    
    result = resolution_entails(KB, query)
    
    print("Does KB entail q?", result)  # Expected: True

def tryClauses():
    # Create the belief base
    KB = BeliefBase()
    # Define the variables
    p, q = Atom("p"), Atom("q")
    
    KB.add(Implies(p, q), priority=1)  # (¬p ∨ q)
    KB.add(p, priority=0)              # (p)
    
    # Query: q and method to get CNF clauses 
    clauses = cnf_clauses_for_query(KB, q)
    for c in clauses:
        print(c)
        
    # You should see:
    #  frozenset({('p', False), ('q', True)})   # from ¬p ∨ q
    #  frozenset({('p', True)})                 # from p
    #  frozenset({('q', False)})                # from ¬q (the negated query)

# Example usage
def example():
    # Create a belief base
    belief_base = BeliefBase()
    
    # Define some propositional symbols
    p = Atom("p")
    q = Atom("q")
    r = Atom("r")
    
    # Add beliefs with priorities
    belief_base.add(Implies(p, q), priority=2)  # p → q with priority 2
    belief_base.add(p, priority=1)              # p with priority 1
    belief_base.add(Or(Not(q), r), priority=3)  # ¬q ∨ r with priority 3
    
    print("Belief Base:")
    print(belief_base)
    
    # Show how to retrieve beliefs
    print("\nAll beliefs:")
    for formula in belief_base.get_beliefs():
        print(formula)
    
    # Example of removing a belief
    print("\nAfter removing p → q:")
    belief_base.remove(Implies(p, q).to_cnf())
    print(belief_base)
    
if __name__ == "__main__":
    import os

    txt_path = os.path.join(os.path.dirname(__file__), "..", "Tests", "test_parser.txt")
    entries = parse_file(txt_path)

    agent = BeliefRevisionAgent()

    # Test EXPAND
    print("\n📌 EXPANDING with parsed formulas...")
    for f, pri in entries:
        print(f"Adding: {f} with priority {pri}")
        agent.expand(f, pri)

    print("\n🧠 Belief base after expansion:")
    print(agent.base)

    # Test ASK
    print("\n🔍 ASKING: does belief base entail q?")
    q = Atom("q")
    print("Answer:", agent.ask(q))

    # Test CONTRACT
    print("\n🧹 CONTRACTING q...")
    agent.contract_partial_meet(q)

    print("\n🧠 Belief base after contraction of q:")
    print(agent.base)

    # Test REVISE
    print("\n🔁 REVISING with ¬p...")
    not_p = Not(Atom("p"))
    agent.revise(not_p)

    print("\n🧠 Final belief base after revision:")
    print(agent.base)
    # tryClauses()
    # example()
    # test_resolution()