cmake_minimum_required(VERSION 3.15)
project(language LANGUAGES C)
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_EXTENSIONS ON)
set(CMAKE_C_STANDARD_REQUIRED True)
set(CMAKE_CXX_FLAGS "-Wall -Wpedantic -g3 -o")

add_executable(run
	source/list.c
	source/main.c
)
target_include_directories(run PUBLIC include)
