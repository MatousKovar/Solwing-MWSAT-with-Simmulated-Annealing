import os
from collections import defaultdict

class MWSATInstance:
    """Efficient implementation of MWSATInstance. Keeps track of which clauses variables occur in, stores weight info and clause to index conversion dict"""
    def __init__(self, filepath, penalty_violation_factor=2):
        self.filepath = filepath
        self.num_vars = 0
        self.num_clauses = 0
        self.weights = [] 
        self.normalized_weights = [] # weights in [0,1] range
        self.clauses = [] 
        self.clause_lookup = defaultdict(list) # which clauses variable is in

        self._load_instance()
        self._init_clause_lookup()

        self.total_raw_weight = sum(self.weights) # maximal possible weight
        self.max_single_weight = max(self.weights) if self.weights else 1

        # Normalize weights to range [0, 1]
        self.normalized_weights = [w / self.max_single_weight for w in self.weights]
        
        self.num_clauses = len(self.clauses)
        
        #legacy
        self.penalty_factor = penalty_violation_factor 


    def _load_instance(self):
        with open(self.filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('c') or line.startswith('%'):
                    continue
                parts = line.split()
                if line.startswith('p'):
                    self.num_vars = int(parts[2])
                    self.num_clauses = int(parts[3])
                elif line.startswith('w'):
                    w_values = [int(x) for x in parts[1:] if x != '0']
                    self.weights.extend(w_values)
                else:
                    literals = [int(x) for x in parts if x != '0']
                    if literals:
                        self.clauses.append(tuple(literals))

    def _init_clause_lookup(self):
        """fills self.clause_lookup:  variable -> clauses it is in"""
        for var_idx in range(self.num_vars):
            for clause in self.clauses:
                for lit in clause:
                    if abs(lit) == var_idx + 1:
                        self.clause_lookup[var_idx].append(clause)

    def get_clauses_for_var(self, var):
        return self.clause_lookup[abs(var) - 1]

    def get_weight_for_variable(self, variable):
        return self.weights[abs(variable) - 1]

    def get_normalized_weight_for_variable(self, variable):
        """Returns the 0-1 weight for calculation"""
        return self.normalized_weights[abs(variable) - 1]

    def get_satisfied_vars_in_clause_count(self, clause, variables):
        count = 0
        for lit in clause:
            var_idx = abs(lit) - 1
            val = variables[var_idx]
            if (lit > 0) == val:
                count += 1
        return count

    def is_satisfied_in_clause(self, clause, variable, variable_value):
        # Check if the specific literal in this clause matches the value
        target_lit = 0
        for x in clause:
            if abs(x) == variable:
                target_lit = x
                break
        return (target_lit > 0) == variable_value

    def evaluate(self, solution):
        """Returns RAW fitness and validity"""
        violated_count = 0
        for clause in self.clauses:
            if self.get_satisfied_vars_in_clause_count(clause, solution) == 0:
                violated_count += 1

        variable_score = 0
        variable_score_norm = 0.0

        for i in range(self.num_vars):
            if solution[i]:
                variable_score += self.weights[i]
                variable_score_norm += self.normalized_weights[i]

        is_valid = (violated_count == 0)
        return variable_score, variable_score_norm, is_valid