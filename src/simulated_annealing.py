import math
import random
import numpy as np
from MWSATInstance import MWSATInstance
from MWSATSolution import MWSATSolution

def compare_metrics(current_sat, current_score, old_sat, old_score):
    """
    Same as compare states, only different input params, it could have been merged to one function
    """
    if current_sat > old_sat:
        return True
    if old_sat > current_sat:
        return False
    return current_score > old_score

def compare_states(lhs: MWSATSolution, rhs: MWSATSolution):
    """Compare if one state is suporior to other based on number of satisfied clauses and then on current score"""
    if lhs.clauses_satisfied > rhs.clauses_satisfied:
        return True
    if rhs.clauses_satisfied > lhs.clauses_satisfied:
        return False
    return lhs.current_score > rhs.current_score

def simulated_annealing(instance: MWSATInstance, 
                        P0: float, 
                        cooling_coefficient: float, 
                        equilibrium_steps: int, 
                        max_steps_without_improvement: float,
                        fitness_coefficient: float,
                        random_flip = False):
    
    current_state = MWSATSolution(instance)
    best_state = current_state.copy()

    # Pre-calculate initial fitness - if neighbor is not accepted it will be flipped back - no copying needed
    sat_unsat = len(current_state.unsatisfied_clauses) / instance.num_clauses
    current_fitness = current_state.current_score_norm - (fitness_coefficient * sat_unsat * instance.num_vars)

    # Initial temperature setup
    delta_avg = set_delta(instance, 1e6, cooling_coefficient=1, equilibrium_steps=100, 
                          steps=3000, fitness_coefficient=fitness_coefficient, random_flip=random_flip)
    
    
    #edge case
    if delta_avg == 0: delta_avg = 1.0
    temperature = abs(delta_avg) / abs(np.log(P0))
    
    history = []
    steps_without_improvement = 0
    total_steps = 0
    max_steps = max_steps_without_improvement * instance.num_clauses

    while steps_without_improvement < max_steps:    
        for _ in range(equilibrium_steps * instance.num_clauses):
            steps_without_improvement += 1
            total_steps += 1
            
            #  PICK VARIABLE - total random, or from unsat clauses
            if random_flip:
                var_to_flip = random.randint(1, instance.num_vars)
            elif current_state.unsatisfied_clauses:
                clause = random.choice(list(current_state.unsatisfied_clauses))
                var_to_flip = abs(random.choice(clause))
            else:
                var_to_flip = random.randint(1, instance.num_vars)

            # SAVE OLD METRICS
            old_sat = current_state.clauses_satisfied
            old_score = current_state.current_score
            
            # FLIP IN PLACE
            current_state.update_variable_and_score(var_to_flip)

            # CALCULATE NEW FITNESS
            # Now 'current_state' IS the neighbor. 
            sat_unsat = len(current_state.unsatisfied_clauses) / instance.num_clauses
            neighbor_fitness = current_state.current_score_norm - (fitness_coefficient * sat_unsat * instance.num_vars)
            
            delta = neighbor_fitness - current_fitness
            
            # ACCEPT OR REVERT
            accept_move = False
            
            # A. Check if strictly better (Greedy) using stored metrics
            if compare_metrics(current_state.clauses_satisfied, current_state.current_score, old_sat, old_score):
                accept_move = True
                # Check Global Best
                if compare_states(current_state, best_state):
                    steps_without_improvement = 0
                    best_state = current_state.copy() # Copy to avoid rewriting
            
            # B. not scritly better - random acceptance of worse
            elif delta > 0:
                accept_move = True
            else:
                exponent = delta / temperature
                if exponent > -100:
                    if random.random() < math.exp(exponent):
                        accept_move = True
            
            if accept_move:
                # Keep the change, update fitness baseline
                current_fitness = neighbor_fitness
            else:
                # REVERT: Flip the same variable again to undo
                current_state.update_variable_and_score(var_to_flip)
                # No need to revert current_fitness, it stays as is
            
            history.append(current_state.current_score)

        temperature *= cooling_coefficient
        if temperature < 1e-5: break
        
    return best_state, history

def set_delta(instance: MWSATInstance, 
              initial_temperature: float, 
              cooling_coefficient: float, 
              equilibrium_steps: int, 
              steps: int,
              fitness_coefficient: float = None,
              random_flip=False):
    """calculates average fitness difference when performing random walk in space"""
              
    current_state = MWSATSolution(instance)
    best_state = current_state.copy()

    sat_unsat = len(current_state.unsatisfied_clauses) / instance.num_clauses
    current_fitness = current_state.current_score_norm - (fitness_coefficient * instance. num_vars * sat_unsat)
    temperature = initial_temperature

    deltas = []
    step_counter = 0
    
    while step_counter < steps:
        for _ in range(equilibrium_steps * instance.num_clauses):
            step_counter += 1
            
            if random_flip:
                var_to_flip = random.randint(1, instance.num_vars)
            elif current_state.unsatisfied_clauses:
                clause = random.choice(list(current_state.unsatisfied_clauses))
                var_to_flip = abs(random.choice(clause))
            else:
                var_to_flip = random.randint(1, instance.num_vars)

            old_sat = current_state.clauses_satisfied
            old_score = current_state.current_score

            current_state.update_variable_and_score(var_to_flip)
            
            sat_unsat = len(current_state.unsatisfied_clauses) / instance.num_clauses
            neighbor_fitness = current_state.current_score_norm - (fitness_coefficient * instance.num_vars * sat_unsat)
            delta = neighbor_fitness - current_fitness

            accept_move = False
            
            if compare_metrics(current_state.clauses_satisfied, current_state.current_score, old_sat, old_score):
                accept_move = True
                if compare_states(current_state, best_state):
                    best_state = current_state.copy()
            else:
                exponent = delta / temperature
                if exponent > -100:
                    if random.random() < math.exp(exponent):
                        deltas.append(abs(delta))
                        accept_move = True
            
            if accept_move:
                current_fitness = neighbor_fitness
            else:
                current_state.update_variable_and_score(var_to_flip)

        temperature *= cooling_coefficient
        
    return np.mean(deltas) if deltas else 1.0