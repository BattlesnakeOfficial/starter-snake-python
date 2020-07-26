cmake_minimum_required(VERSION 2.8)
project(gymbattlesnake)

set(CMAKE_CXX_STANDARD 14)
set(PROJECT_DIR "${CMAKE_SOURCE_DIR}/gym_battlesnake")
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${PROJECT_DIR}/cmake/Modules")

find_package(Threads REQUIRED)

file(GLOB SOURCES "${PROJECT_DIR}/src/*.cpp")

add_library(gymbattlesnake SHARED ${SOURCES})
target_include_directories(gymbattlesnake PRIVATE "${PROJECT_DIR}/include")
target_link_libraries(gymbattlesnake Threads::Threads)
target_compile_options(gymbattlesnake PRIVATE -Wall -fPIC -pthread)