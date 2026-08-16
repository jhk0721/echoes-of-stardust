cmake_minimum_required(VERSION 3.15)
project(rhythm_core LANGUAGES CXX)

add_library(rhythm_core SHARED rhythm_core.cpp)
target_compile_features(rhythm_core PRIVATE cxx_std_17)

if(MSVC)
  target_compile_options(rhythm_core PRIVATE /W4 /O2)
else()
  target_compile_options(rhythm_core PRIVATE -Wall -O2)
endif()
