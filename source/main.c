#include <ctype.h>
#include <stdio.h>
#include <unistd.h>
#include "ui.h"

int main(void) {
	struct window window = {0};
	if (!window_initialize(&window)) {
		fprintf(stderr, "Error initializing window.");
		goto error1;
	}

	while (true) {
		struct keypress key = window_read_character(&window);
		if (!key.base_key) {
			continue;
		}
		keypress_print(key);
		printf("\r\n");

		if (key.base_key == 'q' && !key.is_ctrl && !key.is_alt) {
			break;
		}
	}

	window_destroy(&window);
	return 0;

error1:
	return 1;
}
