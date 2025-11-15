# Belief-Revision-Agent-02180

Implementation of a Belief Revision Agent for propositional logic, developed for the DTU course **02180 – Introduction to Artificial Intelligence**.  
The project implements the AGM framework, including CNF transformation, resolution-based entailment checking, partial meet contraction with priorities, and expansion.  
The agent operates fully on symbolic logic formulas parsed into Abstract Syntax Trees (ASTs) and stored internally in CNF form.

---

## Project Context

**Course:** 02180 – Introduction to Artificial Intelligence  
**Institution:** Technical University of Denmark (DTU)  
**Academic Period:** Spring 2025  

The goal of the assignment is to implement a complete belief revision engine capable of:

1. Representing propositional formulas and belief bases  
2. Checking logical entailment using resolution (implemented from scratch)  
3. Performing contraction based on partial meet contraction with priorities  
4. Executing expansion operations  
5. Combining them into revision operators following the AGM postulates  

The implementation strictly follows the guidelines in the assignment:  
- No external propositional logic libraries are used  
- All CNF conversion, parsing, resolution, and contraction logic is implemented manually  
- The code is modular, tested, and mathematically aligned with the AGM theory  

---

## Features

### 🔹 1. Formula Parsing (`parser.py`, `formula.py`)
- Full propositional logic parser  
- Supports ¬, ∧, ∨, →, ↔ and parentheses  
- Builds an Abstract Syntax Tree (AST)  
- Converts formulas to CNF  
- Handles negation normal form, distributivity, and clause extraction  
- Includes extensive unit tests (`test_parser.py`, `test_parser.txt`)

### 🔹 2. Belief Base (`belief_base.py`)
- Stores formulas with associated integer priorities  
- All formulas converted to CNF on insertion  
- Beliefs kept sorted by priority  
- Supports:
  - `add(formula, priority)`
  - `remove(formula)`
  - `compute_remainders()`
  - `select_remainders()`
  - `intersect_selected()`
  - `contract(formula)`
  - `expand(formula, priority)`  

Implements **partial meet contraction** with priority-based selection.

### 🔹 3. Entailment (`entailment.py`)
Resolution-based entailment checker:
- Converts formulas to CNF  
- Extracts clauses  
- Applies binary resolution  
- Detects contradictions via empty clause  
- Filters tautological clauses  
- Fully sound and complete for propositional logic  

### 🔹 4. Belief Revision Agent (`agent.py`)
Implements the overall revision workflow:
- Expansion  
- Contraction  
- AGM-style revision via Levi identity  
- Pretty-printing and interaction utilities  

### 🔹 5. Examples (`example.py`)
Demonstrates:
- Creating a belief base  
- Adding formulas and priorities  
- Asking entailment queries  
- Contracting beliefs  
- Revising with new information  

Useful as a quickstart script.

### 🔹 6. Test Suite
Included tests ensure correctness of:
- Parser (`test_parser.py`) using `test_parser.txt`  
- Belief base operations (`test_belief_base.py`)  
- AGM postulate compliance (`test_AGM_postulates.py`)  
