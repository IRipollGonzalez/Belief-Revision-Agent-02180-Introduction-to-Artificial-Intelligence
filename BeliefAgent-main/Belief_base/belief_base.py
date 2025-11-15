from Belief_base.formula import Formula
from itertools import combinations
from Belief_base.entailment import resolution_entails
from functools import reduce
from operator import and_

class BeliefBase:
    """
    A belief base that stores propositional formulas with priorities.
    Higher priority values mean the belief is more important.
    """
    def __init__(self):
        # List of (formula, priority) pairs
        self.beliefs = []
    
    def add(self, formula, priority=0):
        """Add a belief with the given priority."""
        # Convert formula to CNF for more efficient entailment checking later
        cnf_formula = formula.to_cnf()
        # Add the cnf_formula and its priority to the belief base
        self.beliefs.append((cnf_formula, priority))
        # Sort beliefs by priority (descending)
        self.beliefs.sort(key=lambda x: x[1], reverse=True)
    
    def get_beliefs(self):
        """Get all beliefs in the belief base without priorities."""
        return [formula for formula, _ in self.beliefs]
    
    def get_prioritized_beliefs(self):
        """Get all beliefs with their priorities."""
        return self.beliefs
    
    # Uses each Formula object's __str__ method to print the belief base, for example the Not class prints: print(Not(Atom("p")))  # Output: ¬(p)
    def __str__(self):
        return "\n".join([f"{priority}: {formula}" for formula, priority in self.beliefs])
    
    # Update the beliefs list by removing any entry where the stored formula f in the existing list is equal to formula passed as an argument
    # f != formula calls f.__eq__(formula) from the relevant formula class Atom, Not, Or etc
    def remove(self, formula):
        """Remove a belief from the belief base."""
        self.beliefs = [(f, p) for f, p in self.beliefs if f != formula]
    
    def clear(self):
        """Remove all beliefs from the belief base."""
        self.beliefs = []
        
    # Computes all maximal subsets of the current belief base that do not entail formula phi
    # These subsets are the remainders and we need these for the partial meet contraction
    def compute_remainders(self, phi: Formula):
        # Retrieve the belief base and its priorities in each element
        beliefs = self.get_prioritized_beliefs()
        # Get the number of beliefs in the belief base
        n = len(beliefs)
        # Initialize empty remainders list
        remainders = []
        
        # Start with the biggest possible subset and go down to the smallest
        # For each size k, we try all k element subsets 
        for k in range(n, 0, -1): # k = n, n-1, ..., 1
            # Each subset is represented by "indexes", a tuple of indexes so (0, 2, 3) means we select beliefs 0, 2 and 3
            for indexes in combinations(range(n), k):
                # Skip subsets already covered by a larger subset
                # THIS AVOIDS DUPLICATE REMAINDERS
                # Example: If {0,1,2} already is a remainder, so we don't need to bother testing {0,1} or {1,2}
                if any(set(indexes).issubset(rem) for rem in remainders):
                    continue
                
                # Create a temporary belief base from the subset
                temp = BeliefBase()
                # Add the beliefs in the current subset to the temporary belief base
                for i in indexes:
                    belief, pri = beliefs[i]
                    temp.add(belief, priority=pri)

                # Check if the temporary belief base entails phi
                if not resolution_entails(temp, phi):
                    remainders.append(set(indexes))
            # If we found at least one remainder of size k, we can stop looking for smaller subsets
            if remainders:
                break

        return remainders

# We take the remainders and sum up the priority values and return the set with the highest score
# If we have several sets with the same highest score, we return all of them
def select_remainders(remainders: list[set[int]], priorities: list[int]) -> list[set[int]]:
    # If we for example have remainders = [{0, 1}, {0, 3}] and priorities = [1, 2, 3, 4]
    # We compute the scores for each remainder: {0, 1} = 1 + 2 = 3 and {0, 3} = 1 + 4 = 5
    scores = [sum(priorities[i] for i in rem) for rem in remainders]
    # Return the max score
    max_score = max(scores)
    # Return the remainder sets with the max score
    return [R for R, s in zip(remainders, scores) if s == max_score]

# If selected is [{0, 2}, {1, 2}], then the intersection is {2}
def intersect_selected(selected: list[set[int]]) -> set[int]:
    # If selected is empty, return an empty set
    if not selected:
        return set()
    return reduce(and_, selected)