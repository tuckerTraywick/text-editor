#ifndef UI_H
#define UI_H

#include <stddef.h>

#define vec(x, y) ((struct vector){.x=(x), .y=(y)})

typedef size_t keycode;

typedef size_t color;

typedef size_t widget_handle;

typedef widget_handle button_handle;

struct vector {
	size_t x;
	size_t y;
};

enum event_type {
	EVENT_TYPE_KEY_PRESS,
	EVENT_TYPE_COUNT,
};

struct event {
	enum event_type type;
	union {
		struct key_press_event {keycode code;} key_press;
	} data;
};

struct window;

struct window *window_create(struct vector size);

void window_destroy(struct window *window);

void window_draw_text(struct window *window, struct vector position, char *text);

void window_draw_line_horizontal(struct window *window, struct vector start, size_t length);

void window_draw_line_vertical(struct window *window, struct vector start, size_t length);

void window_draw_widgets(struct window *window);

void window_update(struct window *window);

widget_handle window_add_widget_impl(struct window *window, void *widget, size_t widget_size, size_t widget_alignment);

widget_handle window_add_button(struct window *window, char *label);

#endif // UI_H
