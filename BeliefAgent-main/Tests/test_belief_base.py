from Belief_base.belief_base import BeliefBase
from Belief_base.formula import Implies, Or, Not, Atom
from Agent.agent import BeliefRevisionAgent
from Belief_base.entailment import resolution_entails

def test_entailment():
    KB = BeliefBase()
    p, q = Atom("p"), Atom("q")
    KB.add(Implies(p, q))
    KB.add(p)
    assert resolution_entails(KB, q)    # should be True
    assert not resolution_entails(KB, Not(q))  # KB ⊭ ¬q
    
def test_contraction():
    # Create your belief revision agent
    agent = BeliefRevisionAgent()

    # Define propositional symbols
    p = Atom("p")
    q = Atom("q")
    r = Atom("r")

    # Add beliefs to the agent's belief base
    agent.base.add(Implies(p, q), priority=2)      # φ₀: (¬p ∨ q)
    agent.base.add(p, priority=1)                  # φ₁: p
    agent.base.add(Or(Not(q), r), priority=3)      # φ₂: (¬q ∨ r)

    print("🧠 Belief base before contraction:")
    print(agent.base)

    # Ask: does the base entail q?
    print("\n❓ Does the base entail q?", agent.ask(q))  # Should be True

    # Contract the belief base by q
    agent.contract_partial_meet(q)

    print("\n🔧 Belief base after contraction by q:")
    print(agent.base)

    # Ask again
    print("\n❓ Does the base entail q now?", agent.ask(q))  # Should be False

if __name__ == "__main__":
    # test_entailment()
    test_contraction()
    # print("All tests passed ✅")