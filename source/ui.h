#ifndef UI_H
#define UI_H

#include <stdint.h>
#include <stdbool.h>
#include <termios.h>

#define ASCII_ESC 27

#define ASCII_DEL 127

#define ASCII_CTRL_START 64

#define vec(x, y) ((struct vector){.x=(x), .y=(y)})

struct keypress {
	char base_key;
	bool is_ctrl : 1;
	bool is_alt : 1;
	bool is_fn : 1;
	bool is_special : 1;
};

struct vector {
	uint32_t x;
	uint32_t y;
};

struct window {
	struct termios stdin_terminal;
	struct termios stdout_terminal;
	struct termios original_stdin_terminal; // Used to switch back to the terminal's previous mode when closing a window.
};

// Returns true if terminal was setup successfully. You may only have one active window at a time.
bool window_initialize(struct window *window);

// Must be called before you create another window.
void window_destroy(struct window *window);

// Not blocking. Returns 0 if no key was pressed before the terminal's timeout.
struct keypress window_get_character(struct window *window);

#endif // UI_H
