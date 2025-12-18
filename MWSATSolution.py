from MWSATInstance import MWSATInstance
import random

class MWSATSolution:
    def __init__(self, mwsat: MWSATInstance):
        self.instance = mwsat
        self.variable_values = [random.choice([0, 1]) for _ in range(mwsat.num_vars)]
        
        self.satisfied_in_clause = {} 
        self.unsatisfied_clauses = set()
        
        # Calculate initial scores (Both Raw and Normalized)
        raw, norm, _ = mwsat.evaluate(self.variable_values)
        self.current_score = raw
        self.current_score_norm = norm
        
        self.clauses_satisfied = 0 

        for clause in self.instance.clauses:
            sat_count = self.instance.get_satisfied_vars_in_clause_count(clause, self.variable_values)
            self.satisfied_in_clause[clause] = sat_count
            if sat_count > 0:
                self.clauses_satisfied += 1
            else:
                self.unsatisfied_clauses.add(clause)

    def copy(self):
        new_sol = MWSATSolution.__new__(MWSATSolution)
        new_sol.instance = self.instance
        new_sol.variable_values = self.variable_values[:]
        new_sol.satisfied_in_clause = self.satisfied_in_clause.copy()
        new_sol.unsatisfied_clauses = self.unsatisfied_clauses.copy()
        
        new_sol.current_score = self.current_score
        new_sol.current_score_norm = self.current_score_norm
        new_sol.clauses_satisfied = self.clauses_satisfied
        return new_sol

    def update_variable_and_score(self, variable):
        variable_value_before = self.variable_values[variable - 1]
        
        # Fetch weights
        raw_w = self.instance.get_weight_for_variable(variable)
        norm_w = self.instance.get_normalized_weight_for_variable(variable) # <--- Fetch normalized

        # 1. Update Scores
        if variable_value_before == 1:
            # Flipping 1 -> 0 (Loss)
            self.current_score -= raw_w
            self.current_score_norm -= norm_w
        else:
            # Flipping 0 -> 1 (Gain)
            self.current_score += raw_w
            self.current_score_norm += norm_w

        # 2. Update Clauses (Logic remains same)
        for clause in self.instance.get_clauses_for_var(variable):
            number_of_satisfied_in_clause = self.satisfied_in_clause[clause]
            is_var_satisfied_in_clause_before = self.instance.is_satisfied_in_clause(clause, variable, variable_value_before)

            if is_var_satisfied_in_clause_before:
                self.satisfied_in_clause[clause] -= 1
                if number_of_satisfied_in_clause == 1:
                    self.clauses_satisfied -= 1
                    self.unsatisfied_clauses.add(clause)
            else:
                self.satisfied_in_clause[clause] += 1
                if number_of_satisfied_in_clause == 0:
                    self.clauses_satisfied += 1
                    self.unsatisfied_clauses.remove(clause)

        self.variable_values[variable - 1] = 1 - self.variable_values[variable - 1]


    def pick_variable_to_flip(self, random_flip=False):
        if random_flip:
            return random.randint(1, self.instance.num_vars)
        
        # Heuristic: Prioritize variables in unsatisfied clauses
        if self.unsatisfied_clauses:
            clause = random.choice(list(self.unsatisfied_clauses))
            # Pick a random literal from that clause
            literal = random.choice(clause) 
            return abs(literal)
        else:
            # If valid (SAT), pick any random variable to explore weights
            return random.randint(1, self.instance.num_vars)


    def generate_neighbor(self, random_flip=False):
        new_solution = self.copy()
        
        if random_flip:
            var_to_flip = random.randint(1, self.instance.num_vars)
        elif len(new_solution.unsatisfied_clauses) > 0:
            random_unsat_clause = random.choice(list(new_solution.unsatisfied_clauses))
            random_literal = random.choice(random_unsat_clause)
            var_to_flip = abs(random_literal)
        else:
            var_to_flip = random.randint(1, self.instance.num_vars)

        new_solution.update_variable_and_score(var_to_flip)
        return new_solution
    
