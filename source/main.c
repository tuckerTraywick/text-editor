#include <stdio.h>
#include <ctype.h>
#include "ui.h"

int main(void) {
	struct window window = {0};
	if (!window_initialize(&window)) {
		fprintf(stderr, "Error initializing window.");
		goto error1;
	}

	while (true) {
		char ch = '\0';
		fread(&ch, 1, 1, stdin);
		if (ch == 'q') {
			break;
		} else if (iscntrl(ch)) {
			printf("char = %d\r\n", ch);
		} else {
			printf("char = `%c` (%d)\r\n", ch, ch);
		}
	}

	window_destroy(&window);
	return 0;

error1:
	return 1;
}
