#include <ctype.h>
#include <stdio.h>
#include <unistd.h>
#include "ui.h"


#define KEY_ESC 27

int main(void) {
	struct window window = {0};
	if (!window_initialize(&window)) {
		fprintf(stderr, "Error initializing window.");
		goto error1;
	}

	while (true) {
		char ch = '\0';
		if (!read(STDIN_FILENO, &ch, 1)) {
			continue;
		} else if (ch == 'q') {
			break;
		} else if (ch == KEY_ESC) {
			// Detect alt + key.
			if (fread(&ch, 1, 1, stdin)) {
				printf("char = alt + `%c`\r\n", ch);
			} else {
				printf("char = esc\r\n");
			}
		} else if (iscntrl(ch)) {
			printf("char = %d\r\n", ch);
		} else if (ch) {
			printf("char = %d (`%c`)\r\n", ch, ch);
		}
	}

	window_destroy(&window);
	return 0;

error1:
	return 1;
}
