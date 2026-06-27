#ifndef UI_H
#define UI_H

#include <stdint.h>
#include <stdbool.h>
#include <termios.h>

#define ASCII_ESC 27

#define ASCII_DEL 127

#define ASCII_CTRL_START 64

#define vec(x, y) ((struct vector){.x=(x), .y=(y)})

struct vector {
	uint32_t x;
	uint32_t y;
};

struct keypress {
	char base_key;
	bool is_ctrl : 1;
	bool is_alt : 1;
	bool is_fn : 1;
	bool is_special : 1;
};

struct style {
	union {
		uint8_t color_index; // For 8/16/256-color mode.
		// For rgb colors.
		struct {
			uint8_t r;
			uint8_t g;
			uint8_t b;
		};
	};
	bool is_rgb : 1;
	bool is_bold : 1;
	bool is_faint : 1;
	bool is_italic : 1;
	bool is_underline : 1;
	bool is_blink : 1;
	bool is_invert : 1;
	bool is_strikethrough : 1;
};

struct cell {
	char character;
	bool has_changed;
	struct style style;
};

struct window {
	struct termios stdin_terminal;
	struct termios stdout_terminal;
	// Used to switch back to the terminal's previous mode when closing a window.
	struct termios original_stdin_terminal;
	struct termios original_stdout_terminal;
	uint32_t width;
	uint32_t height;
	struct cell *screen; // Points to a list. `width*height` elements.
};

void keypress_print(struct keypress keypress);

bool cells_equal(struct cell *a, struct cell *b);

// Returns true if terminal was setup successfully. You may only have one active window at a time.
bool window_initialize(struct window *window);

// Must be called before you create another window.
void window_destroy(struct window *window);

// Not blocking. Returns 0 if no key was pressed before the terminal's timeout.
struct keypress window_read_character(struct window *window);

struct cell *window_get_cell(struct window *window, struct vector position);

void window_set_cell(struct window *window, struct vector position, struct cell *source);

void window_print(struct window *window, struct vector position, char *text, struct style style);

#endif // UI_H
