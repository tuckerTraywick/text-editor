#include <stdbool.h>
#include <ctype.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <termios.h>
#include <sys/ioctl.h>
#include "ui.h"
#include "list.h"

static const char *const special_key_names[] = {
	[ASCII_ESC] = "esc",
	['2'] = "ins",
	['3'] = "del",
	['A'] = "up",
	['B'] = "down",
	['C'] = "right",
	['D'] = "left",
};

void keypress_print(struct keypress key) {
	if (key.is_ctrl) {
		printf("ctrl + ");
	}
	if (key.is_alt) {
		printf("alt + ");
	}

	if (key.is_fn) {
		printf("f%d", key.base_key);
	} else if (key.is_special) {
		printf("%s", special_key_names[(size_t)key.base_key]);
	} else if (key.base_key == ' ') {
		printf("space");
	} else if (key.base_key == '\t') {
		printf("tab");
	} else if (key.base_key == '\n') {
		printf("ret");
	} else if (key.base_key == ASCII_DEL) {
		printf("bkspc");
	} else {
		printf("%c", key.base_key);
	}
}

bool window_initialize(struct window *window) {
	*window = (struct window){0};
	// Setup termios.
	if (tcgetattr(STDIN_FILENO, &window->stdin_terminal)) {
		goto error1;
	}
	if (tcgetattr(STDOUT_FILENO, &window->stdout_terminal)) {
		goto error1;
	}
	window->original_stdin_terminal = window->stdout_terminal;

	struct winsize size = {0};
	// Get the dimensions of the terminal.
	if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &size)) {
		goto error1;
	}
	window->screen_width = size.ws_col;
	window->screen_height = size.ws_row;

	window->screen = list_create(window->screen_width*window->screen_height, sizeof *window->screen);
	if (!window->screen) {
		goto error1;
	}

	cfmakeraw(&window->stdin_terminal); // Enter raw mode.
	window->stdin_terminal.c_iflag |= ICRNL; // Make Return emit a '\n'.
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
	list_destroy(&window->screen);
	*window = (struct window){0};
}

struct keypress window_read_character(struct window *window) {
	struct keypress key = {0};
	if (!read(STDIN_FILENO, &key.base_key, 1)) {
		return (struct keypress){0};
	}

	// Detect esc or alt combo.
	if (key.base_key == ASCII_ESC) {
		if (read(STDIN_FILENO, &key.base_key, 1)) {
			// Detect special keys.
			if (key.base_key == '[' && read(STDIN_FILENO, &key.base_key, 1)) {
				key.is_special = true;
				// Arrow keys.
				if (strchr("ABCD", key.base_key)) {
					return key;
				}
				char scratch;
				// ins and del keys.
				if (strchr("23", key.base_key) && read(STDIN_FILENO, &scratch, 1)) {
					return key;
				}
				return (struct keypress){0}; // Invalid control sequence.
			} else {
				key.is_alt = true;
				if (key.base_key == ASCII_ESC) {
					key.is_special = true;
				}
			}
		} else {
			// esc key.
			key.is_special = true;
			return key;
		}
	}

	// Detect ctrl combo.
	if (key.base_key != '\n' && key.base_key != '\t' && key.base_key != ASCII_ESC && key.base_key != ASCII_DEL && iscntrl(key.base_key)) {
		key.base_key += ASCII_CTRL_START;
		key.is_ctrl = true;
	}
	return key;
}
