#include <stddef.h>
#include <string.h>
#include <stdio.h>
#include "test.h"
#include "buffer.h"
#include "list.h"

struct buffer buffer;

void test_buffer_create(void) {
	assert(buffer_initialize(&buffer, 1, 1));
}

void test_buffer_destroy(void) {
	buffer_destroy(&buffer);
}



int main(void) {
	begin_testing();
		run_test(test_buffer_create);



		run_test(test_buffer_destroy);
	return end_testing();
}
