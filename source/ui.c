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
	window->original_stdin_terminal = window->stdout_terminal;

	cfmakeraw(&window->stdin_terminal); // Enter raw mode.
	window->stdin_terminal.c_cc[VMIN] = 0; // Read stdin one byte at a time.
	window->stdin_terminal.c_cc[VTIME] = 1; // 100 milisecond key press time out.
	tcsetattr(STDIN_FILENO, TCSANOW | TCSAFLUSH, &window->stdin_terminal); // Make these changes happen now.
	return true;

error1:
	*window = (struct window){0};
	return false;
}

void window_destroy(struct window *window) {
	// Restore canonical mode.
	tcsetattr(STDIN_FILENO, TCSANOW, &window->original_stdin_terminal);
	*window = (struct window){0};
}
