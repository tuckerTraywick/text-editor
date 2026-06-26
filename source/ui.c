#include <stdbool.h>
#include <unistd.h>
#include <termios.h>
#include "ui.h"

bool window_initialize(struct window *window) {
	*window = (struct window){0};
	if (tcgetattr(STDIN_FILENO, &window->stdin_terminal)) {
		goto error1;
	}
	if (tcgetattr(STDOUT_FILENO, &window->stdout_terminal)) {
		goto error1;
	}
	window->original_stdout_terminal = window->stdout_terminal;
	return true;

error1:
	*window = (struct window){0};
	return false;
}

void window_destroy(struct window *window) {
	*window = (struct window){0};
}
