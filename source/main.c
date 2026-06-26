#include <stdio.h>
#include "ui.h"

int main(void) {
	struct window window = {0};
	if (!window_initialize(&window)) {
		fprintf(stderr, "Error initializing window.");
		goto error1;
	}

	window_destroy(&window);
	return 0;

error1:
	return 1;
}
