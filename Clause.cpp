//
// Created by Matouš Kovář on 08.12.2025.
//

#include "Clause.h"

Clause::Clause(const std::vector<int> &literals, int weight) {
    this->literals = literals;
    this->weight = weight;
    this->clause_variables.reserve(literals.size());

    for (const int lit : literals) {
        this->clause_variables.push_back(std::abs(lit));
    }
}

bool Clause::satisfied(const std::vector<int> &variable_values) const{

    for (const int lit : literals) {
        const int index = std::abs(lit) - 1;
        const bool target_value = (lit > 0);

        const bool current_value = variable_values[index] > 0;
        if (current_value == target_value) {
            return true;
        }
    }
    return false;
}

int Clause::get_weight() const {
    return this->weight;
}

const std::vector<int> &Clause::get_variables() const {
    return this->clause_variables;
}
