#include <stdbool.h>
#include <ctype.h>
#include <string.h>
#include <stdio.h>
#include <string.h>
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

static bool vectors_equal(struct vector a, struct vector b) {
	return a.x == b.x && a.y == b.y;
}

static bool styles_equal(struct style *a, struct style *b) {
	return memcmp(a, b, sizeof *a);
}

static bool cells_equal(struct cell *a, struct cell *b) {
	return memcmp(a, b, sizeof *a);
}

// Prints the minimum number of control characters to change the terminal's style from `current` to
// `next`.
static void print_style_changes(struct style *current, struct style *next) {
	if (memcmp(&current->color, &next->color, sizeof current->color)) {
		// Print new color.
	}
	if (current->is_bold != next->is_bold) {
		// Print bold.
	}
	if (current->is_faint != next->is_faint) {
		// Print faint.
	}
	if (current->is_italic != next->is_italic) {
		// Print italic.
	}
	if (current->is_underline != next->is_underline) {
		// Print underline.
	}
	if (current->is_blink != next->is_blink) {
		// Print blink.
	}
	if (current->is_invert) {
		// Print invert.
	}
	if (current->is_strikethrough != next->is_strikethrough) {
		// Print strikethrough.
	}
}

// Prints the minimum number of control characters to move the cursor from `current` to `next`.
static void print_position_changes(struct vector current, struct vector next) {
	if (current.x != next.x) {
		printf("\x1b[%dG", next.x);
	}
	if (current.y != next.y) {
		printf("\x1b[%dd", next.y);
	}
}

// Marks every single cell as dirty to trigger a full redraw next frame.
static void window_mark_dirty(struct window *window) {
	for (uint32_t i = 0; i < list_get_count(&window->screen); ++i) {
		window->screen[i].is_dirty = true;
	}
}

// Prints the minimum number of characters to draw the changed cells.
static void window_flush(struct window *window) {
	struct vector current_position = {0};
	struct style current_style = {0};
	for (uint32_t y = 0; y < window->size.y; ++y) {
		for (uint32_t x = 0; x < window->size.x; ++x) {
			struct cell *cell = window_get_cell(window, vec(x, y));
			if (!cell->is_dirty) {
				current_position = vec(x, y);
				continue;
			}

			// If the style has changed, print the control characters to change it.
			if (!styles_equal(&current_style, &cell->style)) {
				print_style_changes(&current_style, &cell->style);
				current_style = cell->style;
			}

			// If the position of the cell is not 1 character to the right of the current position,
			// print the characters to move the cursor.
			if (y != current_position.y || x != current_position.x + 1) {
				print_position_changes(current_position, vec(x, y));
			}
			printf("%c", cell->character);
			current_position = vec(x, y);
		}
	}
}

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
	window->size = vec(size.ws_col, size.ws_row);

	window->screen = list_create(window->size.x*window->size.y, sizeof *window->screen);
	if (!window->screen) {
		goto error1;
	}
	if (!list_set_count(&window->screen, window->size.x*window->size.y)) {
		goto error2;
	}
	window_mark_dirty(window);

	cfmakeraw(&window->stdin_terminal); // Enter raw mode.
	window->stdin_terminal.c_iflag |= ICRNL; // Make Return emit a '\n'.
	window->stdin_terminal.c_cc[VMIN] = 0; // Read stdin one byte at a time.
	window->stdin_terminal.c_cc[VTIME] = 1; // 100 milisecond key press time out.
	tcsetattr(STDIN_FILENO, TCSANOW | TCSAFLUSH, &window->stdin_terminal); // Make these changes happen now.
	return true;

error2:
	list_destroy(&window->screen);
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

struct cell *window_get_cell(struct window *window, struct vector position) {
	return window->screen + position.y*window->size.x + position.x;
}

void window_set_cell(struct window *window, struct vector position, struct cell *source) {
	struct cell *destination = window_get_cell(window, position);
	if (cells_equal(destination, source)) {
		return;
	}
	*destination = *source;
	destination->is_dirty = true;
}

void window_update(struct window *window) {
	window_flush(window);
}
