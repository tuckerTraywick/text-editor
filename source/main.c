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

	printf("\x1b[H");
	printf("\x1b[2J");
	struct style style = {0};
	window_draw_text(&window, vec(0, 0), "hello", style);
	window_update(&window);

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

		if (key.base_key == 'c') {
			printf("\x1b[H");
			printf("\x1b[2J");
			fflush(stdout);
		}
	}

	window_destroy(&window);
	return 0;

error1:
	return 1;	
}
