//
// Created by Matouš Kovář on 08.12.2025.
//

#ifndef INC_02_MWSAT_H
#define INC_02_MWSAT_H

#include <vector>
#include <map>
#include "Clause.h"

class MWSAT {
public:
    MWSAT( int number_of_variables, std::vector<Clause> & clauses);
    int is_solved(const std::vector<int> &variable_values) const;
    const std::vector<Clause> & get_clauses_for_variable(int variable) const;
    MWSAT &operator=(const MWSAT & other);
private:
    int number_of_variables;
    std::vector<Clause> clauses;
    std::map<int,std::vector<Clause>> variable_to_clause; // lookup map - for each variable
};



#endif //INC_02_MWSAT_H