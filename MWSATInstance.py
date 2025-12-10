import os
import numpy as np
import math

from collections import defaultdict

class MWSATInstance:
    def __init__(self, filepath,penalty_violation_factor = 2):
        self.filepath = filepath
        self.num_vars = 0
        self.num_clauses = 0
        self.weights = [] # Index 0 = Variable 1, Index 1 = Variable 2...
        self.clauses = [] # List of lists, e.g., [[4, -18, 19], ...]
        self.clause_lookup = defaultdict(list) # list of clauses for each variabli in which the variable is

        self.num_clauses = len(self.clauses)
        
        self._load_instance()

        self._init_clause_lookup()

        self.max_weight = sum(self.weights)

        self.clause_violation_penalty = self.max_weight * penalty_violation_factor

    def _load_instance(self):
        with open(self.filepath, 'r') as f:
            counter_clause_idx = 0
            for line in f:
                line = line.strip()
                # skip comment
                if not line or line.startswith('c') or line.startswith('%'):
                    continue
                
                parts = line.split()
                
                # Parse Header
                if line.startswith('p'):
                    self.num_vars = int(parts[2])
                    self.num_clauses = int(parts[3])
                
                # Parse Weights
                elif line.startswith('w'):
                    # Skip w and filter out the trailing 0
                    w_values = [int(x) for x in parts[1:] if x != '0']
                    self.weights.extend(w_values)
                
                # Parse Clauses: 4 -18 19 0
                else:
                    # ignore trailing 0
                    literals = [int(x) for x in parts if x != '0']
                    if literals:
                        self.clauses.append(tuple(literals)) # tuple is immutable


    def _init_clause_lookup(self):
        for var_idx in range(self.num_vars):
            for clause in self.clauses:
                for lit in clause:
                    if abs(lit) == var_idx + 1:
                        self.clause_lookup[var_idx].append(clause)

        
    def get_clauses_for_var(self, var):
        var_idx = abs(var) - 1 
        return self.clause_lookup[var_idx]

    def get_max_possible_weight(self):
        return self.max_weight

    def evaluate(self, solution):
        """
        Vypočítá fitness řešení.
        
        Logika:
        1. Zkontroluj Hard Constraints (všechny klauzule musí platit).
        2. Pokud platí, spočítej váhu proměnných (nebo počet jedniček).
        3. Pokud neplatí, vrať záporné skóre (penalizaci).
        
        Returns:
            fitness (float/int): Vyšší je lepší.
            is_valid (bool): True, pokud jsou všechny klauzule splněny.
        """
        
        # 1. Spočítat počet nesplněných klauzulí
        violated_count = 0
        
        for clause in self.clauses:
            is_satisfied = False
            for lit in clause:
                var_idx = abs(lit) - 1
                val = solution[var_idx]
                
                # Pokud se znaménko literálu shoduje s hodnotou (lit>0 a True, lit<0 a False)
                if (lit > 0) == val:
                    is_satisfied = True
                    break # Stačí jeden literál pro splnění klauzule
            
            if not is_satisfied:
                violated_count += 1

        # 2. Spočítat zisk z proměnných (Objective Function)
        # Suma vah proměnných, které jsou True
        variable_score = 0
        for i in range(self.num_vars):
            if solution[i]: # Pokud je proměnná nastavena na 1
                variable_score += self.weights[i]

        # 3. Finální Fitness
        # Fitness = Zisk - (Penalizace * Počet chyb)
        # fitness = variable_score - (violated_count * self.clause_violation_penalty)
        fitness = variable_score
        
        is_valid = (violated_count == 0)
        
        return fitness, is_valid
    

    def get_clauses_for_variable(self, var):
        """
        Accepts var in format same as mwsat - that means 1 is first, not 0
        """
        return self.clause_lookup[abs(var) - 1]
    
    def get_weight_for_variable(self,variable):
        """Variable indexed from 1"""
        return self.weights[abs(variable) - 1]
    
    def get_satisfied_vars_in_clause_count(self, clause, variables):
            """Return number of satisfied literals in clause"""
            count = 0
            
            for lit in clause:
                var_idx = abs(lit) - 1
                val = variables[var_idx] # True or false
                
                if (lit > 0) == val:
                    count += 1
                    
            return count

    def is_satisfied_in_clause(self, clause, variable_name, variable_value):
        """Fist is 1 not 0"""
        for x in clause:
            if abs(x) == variable_name:
                variable_target = x
        variable_target = variable_target > 0
        return variable_target == variable_value

    def get_satisfied_clauses_count(self, variables):
        total = 0
        for clause in self.clauses:
            satisfied_count = self.get_satisfied_vars_in_clause_count(clause,variables)
            if satisfied_count > 0:
                total += 1

        return total
    
    def calculate_variable_score(self,variables):
        total = 0 
        for i, x in enumerate(variables):
            if x == 1:
                total += self.weights[i]

        return total
