#include <stdio.h>
#include "test.h"
#include "editor.h"

static struct buffer buffer;

void setup(void) {
	buffer_initialize(&buffer, 1, 1);
}

void teardown(void) {
	buffer_destroy(&buffer);
}

int main(void) {
	setup();
	begin_testing();

	teardown();
	return end_testing();
}
