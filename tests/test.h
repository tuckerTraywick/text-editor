#ifndef TEST_H
#define TEST_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

// Runs a test and updates the numbers.
#define run_test(test) (run_test_impl((test), __FILE__, __LINE__, #test))

// Runs a condition and updates the numbers.
#define assert(condition) (assert_impl((condition), __FILE__, __LINE__, (char*)__func__, #condition))

// Runs a condition and updates the numbers. Prints `format` with `__VA_ARGS__` if the condition is false.
#define assert_else(condition, format, ...) if (!assert(condition)) {printf(format, ##__VA_ARGS__);}

// Tests if `a` == `b` and prints `a` and `b` using `a_format` and `b_format` if the test fails.
#define assert_eq(a, b, a_format, b_format) if (!assert((a) == (b))) {printf("%s == " a_format "\n%s == " b_format "\n", #a, (a), #b, (b));}

// Tests if `a` != `b` and prints `a` and `b` using `a_format` and `b_format` if the test fails.
#define assert_ne(a, b, a_format, b_format) if (!assert((a) != (b))) {printf("%s == " a_format "\n%s == " b_format "\n", #a, (a), #b, (b));}

// The function signature for a test case.
typedef void (*test_case)(void);

// Setup the numbers tracked by test cases.
void begin_testing(void);

// Prints the results of testing. Returns an exit code for `main()`.
int end_testing(void);

void run_test_impl(test_case test, char *file_name, unsigned int line_number, char *test_name);

bool assert_impl(bool success, char *file_name, unsigned int line_number, char *test_name, char *expression);

#endif // TEST_H
