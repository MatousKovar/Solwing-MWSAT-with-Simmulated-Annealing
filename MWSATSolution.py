import numpy as np
import os
from MWSATInstance import MWSATInstance
import random


class MWSATSolution:
    def __init__(self, mwsat: MWSATInstance):
        self.instance =  mwsat
        self.variable_values = [random.choice([0,1]) for x in range(mwsat.num_vars)] # initialize as random in the beginnign
        self.satisfied_in_clause = {}# number of satisfied literals in clause, clause order is same as in MWSATInstance
        self.current_score, self.is_satisfied = mwsat.evaluate(self.variable_values)
        self.clauses_satisfied = self.instance.get_satisfied_clauses_count(self.variable_values)

        self.instance_max_score = self.instance.get_max_possible_weight()
        self.clause_violation_penalty = self.instance.clause_violation_penalty

        for idx, clause in enumerate(self.instance.clauses):
            self.satisfied_in_clause[clause] = self.instance.get_satisfied_vars_in_clause_count(clause,self.variable_values)


    def copy(self):
        """
        Creates a fast deep copy of the solution. 
        deepcopy would create useless copies of MWSATInstance, which is static
        """
        
        new_sol = MWSATSolution.__new__(MWSATSolution)
        
        # Copy references for static data
        new_sol.instance = self.instance
        new_sol.clause_violation_penalty = self.clause_violation_penalty
        
        # Copy mutable data (Lists and Dicts need explicit copying)
        new_sol.variable_values = self.variable_values[:] 
        new_sol.satisfied_in_clause = self.satisfied_in_clause.copy()
        
        # Copy scalars
        new_sol.current_score = self.current_score
        new_sol.clauses_satisfied = self.clauses_satisfied
        
        return new_sol

    def update_variable_and_score(self,variable):
        """Variable is same as in clauses in input - indexed from 1"""
        variable_value_before = self.variable_values[variable - 1]
        

        # handle adding or subtracting weight after flipping variable
        if variable_value_before == 1:
            self.current_score -= self.instance.get_weight_for_variable(variable)

        else:
            self.current_score += self.instance.get_weight_for_variable(variable)


        # update score only based on clauses affected by variable
        for clause in self.instance.get_clauses_for_var(variable):
            number_of_satisfied_in_clause = self.satisfied_in_clause[clause] # to check if clause is satisfied 
            is_var_satisfied_in_clause_before = self.instance.is_satisfied_in_clause(clause,variable,variable_value_before)



            # handle if variable was satisfied in clause
            if is_var_satisfied_in_clause_before:
                self.satisfied_in_clause[clause] -= 1
                #clause is now unsatisfied
                if number_of_satisfied_in_clause == 1: # if it was only one - now unsat
                    # self.current_score -= self.clause_violation_penalty # penalise state, when boolean formula is not satisfied
                    self.clauses_satisfied -= 1
            
            else:
                self.satisfied_in_clause[clause] += 1

                if number_of_satisfied_in_clause == 0:
                    # self.current_score += self.clause_violation_penalty 
                    self.clauses_satisfied += 1
            

        #flip bit
        self.variable_values[variable-1] = 1 - self.variable_values[variable-1]

    def generate_neighbor(self):
        """
        Generates a neighbor by flipping one random variable.
        Returns a NEW solution object (does not modify self).
        """
        new_solution = self.copy()
        var_to_flip = random.randint(1, self.instance.num_vars)
        new_solution.update_variable_and_score(var_to_flip)

        return new_solution

    def get_raw_score(self):
        return self.instance.calculate_variable_score(self.variable_values)
        
                
