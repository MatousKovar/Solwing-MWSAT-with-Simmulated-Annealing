cmake_minimum_required(VERSION 4.0)
project(02)

set(CMAKE_CXX_STANDARD 14)

add_executable(02
        main.cpp
        MWSAT.cpp
        MWSAT.h
        Clause.cpp
        Clause.h
)
