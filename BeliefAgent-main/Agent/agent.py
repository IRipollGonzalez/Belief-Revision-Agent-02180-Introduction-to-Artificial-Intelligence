from Belief_base.belief_base import BeliefBase, select_remainders, intersect_selected
from Belief_base.formula import Formula, Atom, Not, Or, And
from Belief_base.entailment import resolution_entails

class BeliefRevisionAgent:
    def __init__(self):
        self.base = BeliefBase()
        
    # Method to ask AI agent if a given belief base entails a query φ
    def ask(self,query: Formula) -> bool:
        return resolution_entails(self.base, query)
    
    # Method to add beliefs to the belief base with a given priority
    
    # Contract partial meet is a method that removves a belief from the belief base whilst still keeping the belief base consistent
    def contract_partial_meet(self, formula: Formula):
        
        # Vacuity check: if the belief base doesn't entail the formula, no need to contract
        if not resolution_entails(self.base, formula):
            return
        
        # Compute all maximal subsets of the belief base that do not entail the formula
        remainders = self.base.compute_remainders(formula)
        
        # --- guard against empty remainders ---
        if not remainders:
            # no way to remove formula; clear the base entirely
            self.base.clear()
            return
        
        # Get the priority values in the same order as belief indices
        priorities = [pri for _, pri in self.base.get_prioritized_beliefs()]
        
        # Select the remainders with the highest total priority
        # If we have remainders = [{0, 1}, {0, 3}] and priorities = [1, 2, 3, 4]
        # We compute the scores for each remainder: {0, 1} = 1 + 2 = 3 and {0, 3} = 1 + 4 = 5, we return the set with the highest score so {0, 3}
        # If we have several sets with the same highest score, we return all of them
        selected = select_remainders(remainders, priorities)
        
        # Intersect the slected remanders. If selected is [{0, 2}, {1, 2}], then the intersection is {2}
        # If we only have one selected remainder, like {0, 2}, we return {0, 2}
        keep_indexes = intersect_selected(selected)
        
        # Then rebuild KB in place: Keep only the beliefs in the intersection of all remainders
        all_beliefs = self.base.get_prioritized_beliefs()
        
        # Filter the beliefs to keep only those indexes that were found in the intersection
        new_beliefs = [all_beliefs[i] for i in sorted(keep_indexes)]
        
        # Clear the belief base because we want to add the new beliefs that were filtered by the intersection
        self.base.clear()
        
        # Add the new beliefs to the belief base and its priorities
        for belief, priority in new_beliefs:
            self.base.add(belief, priority)
            
    def expand(self, formula: Formula, priority: int = 0):
        # Fairly simple, we simply add φ (in CNF form) with the given priority.
        # Note: this can introduce inconsistency, but expansion
        # by definition does not restore consistency.
        self.base.add(formula, priority)

    def revise(self, formula: Formula):
        # K * φ = (K - ¬φ) ∪ {φ} THIS IS CALLED THE LEVI IDENTITY
        self.contract_partial_meet(Not(formula))
        self.expand(formula)
        
if __name__ == "__main__":
    import os
    from Belief_base.parser import parse_file

    # locate the test file next to your Tests folder
    txt_path = os.path.join(os.path.dirname(__file__), "..", "Tests", "test_parser.txt")
    formulas = parse_file(txt_path)

    agent = BeliefRevisionAgent()
    for f in formulas:
        print(f"> Revising by: {f}")
        agent.revise(f)

    print("\n🧠 Final belief base after all revisions:")
    print(agent.base)