//
// Created by Matouš Kovář on 08.12.2025.
//

#ifndef INC_02_CLAUSE_H
#define INC_02_CLAUSE_H
#include <vector>
#include <set>
#include <cmath>


class Clause {
public:
    explicit Clause(const std::vector<int> & literals, int weight = 1); // gets
    bool satisfied(const std::vector<int> & variable_values) const; // gets input of value of all variables and checks if this clause is satisfied
    int get_weight() const;
    const std::vector<int> &get_variables() const;
private:
    std::vector<int>  clause_variables;  // stores absolute values of literals - indexes of variables in clause
    int weight;
    std::vector<int> literals; // literals store target values for variables for example [13, 14, -15]  - x13 true, x14 true, x15 false
};


#endif //INC_02_CLAUSE_H