#include <stdbool.h>
#include <stdio.h>
#include "test.h"

static unsigned int tests_run;
static unsigned int tests_passed;
static unsigned int tests_failed;
static unsigned int assertions_run;
static unsigned int assertions_passed;
static unsigned int assertions_failed;

void begin_testing(void) {
	tests_run = 0;
	tests_passed = 0;
	tests_failed = 0;
	assertions_run = 0;
	assertions_passed = 0;
	assertions_failed = 0;
}

int end_testing(void) {
	if (!tests_failed) {
		printf("\n");
	}
	printf("---- TEST SUMMARY ----\n");
	printf(
		"%u tests run.\n%u tests passed.\n%u tests failed.\n%u assertions run.\n%u assertions passed.\n%u assertions failed.\n",
		tests_run, tests_passed, tests_failed, assertions_run, assertions_passed, assertions_failed
	);
	if (assertions_failed) {
		return 1;
	}
	return 0;
}

void run_test_impl(test_case test, char *file_name, unsigned int line_number, char *test_name) {
	unsigned int assertions_failed_before_test = assertions_failed;
	test();
	++tests_run;
	if (assertions_failed > assertions_failed_before_test) {
		++tests_failed;
		printf("[%s:%u:%s] Test failed.\n\n", file_name, line_number, test_name);
		return;
	}
	++tests_passed;
}

bool assert_impl(bool success, char *file_name, unsigned int line_number, char *test_name, char *expression) {
	++assertions_run;
	if (success) {
		++assertions_passed;
	} else {
		++assertions_failed;
		printf("[%s:%u:%s] Assertion failed: `%s`.\n", file_name, line_number, test_name, expression);
	}
	return success;
}
