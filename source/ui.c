#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>
#include "ui.h"
#include "list.h"

struct character_format {
	char foreground_color : 8;
	char background_color : 8;
	bool bold : 1;
	bool italic : 1;
	bool highlight : 1;
};

struct window {
	struct vector size;
	char *text; // The grid of characters in the window. Same dimensions as `size`. Points to a list. Not null terminated.
	struct character_format *format; // The format for each character of the window. Same dimensions as `text`.
};

struct window *window_create(struct vector size) {
	struct window *window = malloc(sizeof *window);
	if (!window) {
		goto error1;
	}
	*window = (struct window){
		.size = size,
		.text = list_create(size.x*size.y, sizeof *window->text),
	};
	if (!window->text) {
		goto error2;
	}
	window->format = list_create(size.x*size.y, sizeof *window->format);
	if (!window->format) {
		goto error3;
	}
	return window;

error3:
	list_destroy(&window->text);
error2:
	free(window);
error1:
	return NULL;
}

void window_destroy(struct window *window) {
	list_destroy(&window->text);
	list_destroy(&window->format);
	free(window);
}
