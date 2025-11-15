from Agent.agent import BeliefRevisionAgent
from Belief_base.formula import Atom, Not, Or, And

# B ∗ ϕ = Cn(B ∗ ϕ) so we can use the B ∗ ϕ := (B ÷ ¬ϕ) + ϕ Levi Identity for this
def test_success_postulate():
    print("Running test_success_postulate")
    agent = BeliefRevisionAgent()
    
    p = Atom("p")               # "Light is on"
    q = Atom("q")               # "Switch is broken"

    # Add: p and p → q   (which is ¬p ∨ q)
    agent.base.add(p)
    agent.base.add(Or(Not(p), q))

    print(" Belief base before revision:")
    print(agent.base)

    # Revise with ¬q — "Switch is NOT broken" 
    phi = Not(q)  # ¬q
    # In this case, φ=¬q and when we pass this into the revise method
    # we contract by ¬φ, which is ¬(¬q) = q.
    agent.revise(phi)

    # Because of modus ponens, we should now have ¬p in the belief base
    # But that contradicts the original belief base because p, p → q entails q
    print("\n Belief base after revise(¬q):")
    print(agent.base)

    # Assert expected outcomes
    assert not agent.ask(q), "Expected q not to be entailed after revising with ¬q"
    assert agent.ask(Not(q)), "Expected ¬q to be entailed after revising with ¬q"

    print("test_success_postulate (conflict case) passed\n")
    
# Contraction by q is supposed to remove just enough of your existing beliefs so that q is no longer a consequence of the belief base.
def test_contraction_success_postulate():
    print("Running test_contraction_success_postulate")
    agent = BeliefRevisionAgent()
    
    # Pick two atoms
    p = Atom("p")
    q = Atom("q")

    # Seed the base so that it entails q: modulus ponens
    #   1) p
    #   2) p → q  (¬p ∨ q)
    agent.base.add(p)
    agent.base.add(Or(Not(p), q))

    print(" Belief base before contraction by q:")
    print(agent.base)
    # sanity‐check: we must entail q right now
    assert agent.ask(q), "Setup failure: base should entail q before contraction"

    # NOW contract by q
    agent.contract_partial_meet(q)

    print("\n Belief base after contraction by q:")
    print(agent.base)
    # Success postulate demands that q is no longer entailed
    assert not agent.ask(q), \
        "Contraction success postulate failed: q is still entailed after contracting by q"

    print("test_contraction_success_postulate passed\n")

    
# After contracting the belief base by some formula φ, the resulting belief base should be a subset of the original belief base.
def test_inclusion_postulate():
    print("Running test_inclusion_postulate")
    agent = BeliefRevisionAgent()

    # Define atoms
    p, q, r = Atom("p"), Atom("q"), Atom("r")

    # Add beliefs: p and p → q (which is ¬p ∨ q)
    agent.base.add(p)
    agent.base.add(Or(p, r))
    agent.base.add(Or(Not(p), q))  # This implies q via modus ponens

    print(" Belief base before contraction with q:")
    print(agent.base)

    # Take a snapshot of current beliefs (CNF already applied)
    original_beliefs = set(agent.base.get_beliefs())

    # Now contract q
    agent.contract_partial_meet(q)

    # Based on our success postulate previously, both p and p → q gets removed, which leaves us with p ∨ r
    # Which is a subset
    print("\n Belief base after contraction:")
    print(agent.base)

    # Get the updated beliefs
    new_beliefs = set(agent.base.get_beliefs())

    # Check that nothing new was added — only removed or unchanged
    assert new_beliefs.issubset(original_beliefs), "Inclusion postulate failed: new base not a subset"

    print("test_inclusion_postulate passed\n")
    
# Revision inclusion essntially says that new beliefs must trace back to old beliefs or new info we explicitly added
def test_inclusion_postulate_revision():
    print("Running test_inclusion_postulate_revision")
    agent = BeliefRevisionAgent()

    # Seed the base so it contains p and (¬p ∨ q)
    p, q, r = Atom("p"), Atom("q"), Atom("r")
    agent.base.add(p)
    agent.base.add(Or(Not(p), q))

    print(" Belief base before revision:")
    print(agent.base)

    # Snapshot original beliefs (no r yet)
    original = set(agent.base.get_beliefs())

    # Revise by r
    agent.revise(r)

    print("\n Belief base after revising with r:")
    print(agent.base)

    # Everything in the new base must come from original ∪ {r}
    new_beliefs = set(agent.base.get_beliefs())
    allowed = original.union({r})
    assert new_beliefs.issubset(allowed), (
        "Inclusion postulate for revision failed: "
        f"new base {new_beliefs} not ⊆ original∪{{r}} = {allowed}"
    )

    print("test_inclusion_postulate_revision passed\n")


# If a formula ϕ is not entailed by the belief base, then contracting ϕ should not change anything.
# In short: you can't remove what you don't believe, so the base should stay the same.
def test_vacuity_postulate():
    print("Running test_vacuity_postulate")

    agent = BeliefRevisionAgent()
    
    p = Atom("p")  # "my car is red"
    r = Atom("r")  # "It's raining"
    s = Atom("s")  # "The sun is shining"

    # Add belief "raining" and "My car is red" ∧ "It's raining"
    agent.base.add(r)
    agent.base.add(And(p,r))

    # get original belifs
    original_beliefs = set(agent.base.get_beliefs())

    print(" Belief base before vacuous contraction with 's':")
    print(agent.base)

    # Try to contract "sun is shining" — which we don't believe
    agent.contract_partial_meet(s)

    print("\n Belief base after vacuous contraction:")
    print(agent.base)

    # Belief base should be unchanged
    new_beliefs = set(agent.base.get_beliefs())
    assert original_beliefs == new_beliefs, "Vacuity postulate failed: base changed even though formula not entailed"

    print("test_vacuity_postulate passed\n")

# Simply, if ¬φ is not entailed by the belief base, then revising by φ just becomes expansion by φ.
def test_vacuity_postulate_revision():
    print("Running test_vacuity_postulate_revision")
    agent = BeliefRevisionAgent()

    # Atoms
    p = Atom("p")
    q = Atom("q")
    s = Atom("s")  # "The sun is shining"

    # Seed base so that it does NOT entail ¬s
    #    We'll just add p and (p → q).  There's no mention of 's' or '¬s'.
    agent.base.add(p)
    agent.base.add(Or(Not(p), q))

    print(" Belief base before vacuous revision with 's':")
    print(agent.base)

    # Check we indeed do NOT entail ¬s
    assert not agent.ask(Not(s)), "Setup failure: base should not entail ¬s"

    # Snapshot original beliefs
    original = set(agent.base.get_beliefs())

    # Revise by s
    agent.revise(s)

    print("\n Belief base after vacuous revision with 's':")
    print(agent.base)

    # The new beliefs must be exactly original ∪ {s}
    new_beliefs = set(agent.base.get_beliefs())
    expected    = original.union({s})
    assert new_beliefs == expected, (
        f"Vacuity postulate for revision failed:\n"
        f" got    = {new_beliefs}\n"
        f" expect = {expected}"
    )

    print("test_vacuity_postulate_revision passed\n")


# In the slides in week 11, the consistency postulate is a part of the revision postulates
# With consistency postulate, we are saying that the belief base should not entail a contradiction after revision.
def test_consistency_postulate():
    print("Running test_consistency_postulate")
    agent = BeliefRevisionAgent()
    
    # Pick a simple atom and seeed base with somethig consistent
    p = Atom("p")
    q = Atom("q")
    agent.base.add(Or(p, q))      # p ∨ q
    agent.base.add(Or(Not(p), q)) # p → q (which is ¬p ∨ q)
    
    print(" Belief base before revision:")
    print(agent.base)
    
    # Revise by p (which is consistent)
    agent.revise(p)
    
    print("\n Belief base after revising with p:")
    print(agent.base)
    
    # Build an explicit contradiction: p ∧ ¬p
    contradiction = And(p, Not(p))
    
    # Test bug entailing contradiction
    print("Entails p ∧ ¬p?", agent.ask(contradiction))
    print("Entails p?", agent.ask(p))
    print("Entails ¬p?", agent.ask(Not(p)))
    
    # The base *should not* entail a contradiction
    # In other words, does our current belief base logically imply p ∧ ¬p?
    # If it does, then we have an inconsistency in our belief base
    assert not agent.ask(contradiction), \
        "Consistency postulate failed: belief base is inconsistent after revision"
    
    print("test_consistency_postulate passed\n")

# Extensionality postulates asks: If two formulas ϕ and ψ are logically equivalent, then revising the belief base
# with ϕ and ψ should yield the same result
def test_extensionality_postulate():
    print("Running test_extensionality_postulate")

    # Define two agents
    agent1 = BeliefRevisionAgent()
    agent2 = BeliefRevisionAgent()

    p, q = Atom("p"), Atom("q")

    # Give both agents the same initial belief base
    agent1.base.add(Or(Not(p), q))  # p → q
    agent2.base.add(Or(Not(p), q))  # p → q

    # Define logically equivalent formulas
    phi = Or(p, q)     # p ∨ q
    psi = Or(q, p)     # q ∨ p

    # Revise each agent with one of the formulas
    agent1.revise(phi)
    agent2.revise(psi)

    # Compare the resulting belief bases
    b1 = set(agent1.base.get_beliefs())
    b2 = set(agent2.base.get_beliefs())

    # Print for debugging
    print(" Agent 1 belief base after revising with p ∨ q:")
    print(agent1.base)
    print("\n Agent 2 belief base after revising with q ∨ p:")
    print(agent2.base)

    # Step 6: Check that belief bases are the same
    assert b1 == b2, "Extensionality postulate failed: logically equivalent formulas led to different bases"

    print("test_extensionality_postulate passed\n")

# The task doesn't specify extentionality for contraction for revision or contraction, but we'll try it both ways just in acse
def test_extensionality_contraction():
    print("Running test_extensionality_contraction")
    agent1 = BeliefRevisionAgent()
    agent2 = BeliefRevisionAgent()
    p, q = Atom("p"), Atom("q")

    # Give them the same starting beliefs
    agent1.base.add(p)                # just some seed belief
    agent1.base.add(Or(p, q))         # "p ∨ q"
    agent1.base.add(Or(Not(p), q))    # "p → q"
    # copy that exact same set over to agent2
    for f, pri in agent1.base.get_prioritized_beliefs():
        agent2.base.add(f, pri)

    # Define two equivalent sentences
    phi = Or(p, q)  # p ∨ q
    psi = Or(q, p)  # q ∨ p

    # Contract them
    agent1.contract_partial_meet(phi)
    agent2.contract_partial_meet(psi)

    # Compare
    b1 = set(agent1.base.get_beliefs())
    b2 = set(agent2.base.get_beliefs())
    print("Agent1 base after contracting p∨q:\n", agent1.base)
    print("Agent2 base after contracting q∨p:\n", agent2.base)
    assert b1 == b2, "Contraction extensionality failed"
    print("test_extensionality_contraction passed\n")

if __name__ == "__main__":
    test_success_postulate()
    test_contraction_success_postulate()
    test_inclusion_postulate()
    test_inclusion_postulate_revision()
    test_vacuity_postulate()
    test_vacuity_postulate_revision()
    test_consistency_postulate()
    test_extensionality_postulate()
    test_extensionality_contraction()