#include "MWSAT.h"
#include <iostream>

// Constructor
MWSAT::MWSAT(int number_of_variables, std::vector<Clause> &input_clauses) {
    this->number_of_variables = number_of_variables;

    this->clauses = input_clauses;

    // Build the lookup map
    for (const auto &clause : this->clauses) {
        
        const std::vector<int> &vars = clause.get_variables();
        for (int var_abs : vars) {
            this->variable_to_clause[var_abs].push_back(clause);
        }
    }
}

// Calculates the "Cost" or "Energy" of the solution
// Returns: Sum of weights of UNSATISFIED clauses.
// 0 means perfect solution (all satisfied).
int MWSAT::is_solved(const std::vector<int> &variable_values) const {
    int penalty_cost = 0;

    for (const auto &clause : clauses) {
        // If the clause is NOT satisfied, we add its weight to the penalty
        if (!clause.satisfied(variable_values)) {
            penalty_cost += clause.get_weight();
        }
    }

    return penalty_cost;
}

// Returns a reference to the list of clauses containing specific variable
const std::vector<Clause> &MWSAT::get_clauses_for_variable(int variable) const {
    return variable_to_clause.at(variable);
}

MWSAT &MWSAT::operator=(const MWSAT &other) {
    if (this == &other) {
        return *this; // Handle self-assignment (a = a)
    }

    this->number_of_variables = other.number_of_variables;

    this->clauses = other.clauses;
    this->variable_to_clause = other.variable_to_clause;

    return *this; 
}