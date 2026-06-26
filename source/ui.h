#ifndef UI_H
#define UI_H

#include <stdint.h>
#include <stdbool.h>
#include <termios.h>

#define vec(x, y) ((struct vector){.x=(x), .y=(y)})

typedef uint8_t char8;

typedef uint64_t char64;

struct vector {
	uint32_t x;
	uint32_t y;
};

struct window {
	struct termios stdin_terminal;
	struct termios stdout_terminal;
	struct termios original_stdout_terminal; // Used to switch back to the terminal's previous mode when closing a window.
};

// struct view;

// You may only have one active window at a time. Returns true if terminal was setup successfully.
bool window_initialize(struct window *window);

// Must be called before you create another window.
void window_destroy(struct window *window);

// A rectangular section of a window. You can have multiple views active at once.
// struct view *view_create(struct window *window, struct vector position, struct vector size);

// void view_destroy(struct view *view);

// void view_draw_text(struct view *view, struct vector position, char *text);

// void view_draw_line_horizontal(struct view *view, struct vector start, size_t length, char fill, );

// void view_draw_line_vertical(struct view *view, struct vector start, size_t length);

// void view_draw_widgets(struct view *view);

// void window_update(struct window *window);

// widget_handle window_add_widget_impl(struct window *window, void *widget, size_t widget_size, size_t widget_alignment);

// widget_handle window_add_button(struct window *window, char *label);

#endif // UI_H
