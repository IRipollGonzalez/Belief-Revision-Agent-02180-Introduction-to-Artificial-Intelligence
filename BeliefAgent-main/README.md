# Belief Revision Agent – DTU 02180 Intro to AI

This repository implements a belief revision agent based on AGM theory using propositional logic. The agent supports expansion, contraction, and entailment operations over a belief base and is designed to demonstrate rational belief change in accordance with the AGM postulates.

## 📚 Project Overview

- **Belief Base**: Stores propositional formulas, each with an integer priority. Higher priority beliefs are preserved when contractions are required.
- **Entailment**: Resolution-based checker for logical entailment (implemented from scratch).
- **Contraction**: Implements partial meet contraction using a priority-based selection function.
- **Expansion**: Adds new formulas to the base (possibly introducing inconsistency).
- **Revision**: Implements the Levi identity: contraction followed by expansion.

This implementation is intended as part of the Belief Revision assignment for the DTU course *02180 - Introduction to Artificial Intelligence* (Spring 2025).

---

## 🔧 Project Structure

Belief_base/
│ ├── formula.py # Logical formula classes and CNF transformation
│ ├── belief_base.py # BeliefBase class with priority and remainders
│ ├── entailment.py # Resolution-based entailment checker
Agent/
│ └── agent.py # BeliefRevisionAgent with ask, expand, contract, revise
Examples/
│ └── example.py # Example driver script for running the agent
Tests/
│ ├── test_parser.py
│ ├── test_belief_base.py
│ └── test_AGM_postulates.py



---

## 🧠 How It Works

### Belief Representation

Each belief is a pair: `(<Formula>, priority)`  
Formulas are automatically converted to **CNF** for resolution-based reasoning.

### Entailment

The function `resolution_entails(kb, φ)` checks whether a belief base entails a query using the resolution principle:
- If the empty clause ⊥ is derived from `B ∪ {¬φ}`, then `B ⊨ φ`.

### Contraction

Partial meet contraction:
- Finds all maximal subsets of `B` that do not entail `φ`.
- Selects the ones with highest total priority.
- Contracts to the intersection of selected remainders.

### Expansion

Adds a formula `φ` with a priority. Follows:

B + φ = B ∪ {φ}

Does not ensure consistency.

### Revision

Defined by the Levi Identity:

B * φ = (B - ¬φ) + φ


---

## 🧪 Running the Code

### Requirements
- Python 3.8+
- No external libraries required.

### Running the Tests
Make sure that you are in the root directory.
Run the AGM postulate tests via:
```bash
python -m Tests.test_AGM_postulates
```
### Test with a Manual input
Insert the formulas that you want on `test_parser.txt`
Make sure the format is correct { "formula" ; "priority_number" } For example: (p → q);5
Run the belief revision (Make sure you are in the root directory) with input formulas:
```bash
python -m Examples.example
```
This should output new beliefs where we test all the methods of the agent!
