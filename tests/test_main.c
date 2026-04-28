#include <stddef.h>
#include <string.h>
#include <stdio.h>
#include "test.h"
#include "buffer.h"
#include "list.h"

struct buffer buffer;

void test_buffer_create_and_destroy(void) {
	assert(buffer_initialize(&buffer, 1, 1));

	buffer_destroy(&buffer);
}

int main(void) {
	begin_testing();
		run_test(test_buffer_create_and_destroy);
	return end_testing();
}
