//
// Created by Matouš Kovář on 08.12.2025.
//
#include <stdlib.h>
#include <iostream>
#include <filesystem>
#include "Clause.h"


int simmulated_annealing(double initial_temperature, double decrease_factor, double stop_temperature )
{


    return 0;
}

int main()
{
    Clause clause({4, -3, -5}, 1);
    Clause clause1({1, 2, 3}, 1);
    Clause clause2({3, 4, -1}, 1);
    Clause clause3({-4, 3, -5}, 1);

    std::vector<Clause> clauses = {clause, clause1, clause2, clause3};


    std::cout << clause.satisfied({0,0,1,0,1}) <<std::endl;
    std::cout<<"hello world" <<std::endl;
}
