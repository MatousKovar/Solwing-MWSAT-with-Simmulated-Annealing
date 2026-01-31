from MWSATInstance import MWSATInstance
import random

class MWSATSolution:
    """For tracking current state of solution, effective - flipping automatically recalculates weight price"""
    def __init__(self, mwsat: MWSATInstance):
        self.instance = mwsat
        self.variable_values = [random.choice([0, 1]) for _ in range(mwsat.num_vars)]
        
        self.satisfied_in_clause = {} # satisfied literals in clauses
        self.unsatisfied_clauses = set() # unsatisfied clauses for efficient getting of literals to flip
        
        
        raw, norm, _ = mwsat.evaluate(self.variable_values) # get initial scores

        self.current_score = raw # for plotting and results
        self.current_score_norm = norm # for inside algorithm
        
        self.clauses_satisfied = 0 

        #init clauses satisfied
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
        """Updates variable and score, if new clause satisfied then updated clauses_satisfied, if new is broken, it is removed so it is as efficient as possible"""
        variable_value_before = self.variable_values[variable - 1]
        
        raw_w = self.instance.get_weight_for_variable(variable)
        norm_w = self.instance.get_normalized_weight_for_variable(variable) # <--- Fetch normalized

        # Update Scores - new variable 1 means new score increase
        if variable_value_before == 1:
            # Flipping 1 -> 0 (Loss)
            self.current_score -= raw_w
            self.current_score_norm -= norm_w
        else:
            # Flipping 0 -> 1 (Gain)
            self.current_score += raw_w
            self.current_score_norm += norm_w

        # Update Clauses - if new clause is satisfied or broken
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

        self.variable_values[variable - 1] = 1 - self.variable_values[variable - 1] # flip


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
            # fallback when all clauses are satisfied
            return random.randint(1, self.instance.num_vars)


    def generate_neighbor(self, random_flip=False):
        """Legacy, uneffective - copying itself is unnecessary, this logic is now done in simulated_annealing function"""
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
    
