#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include "ui.h"

static const size_t initial_nodes_capacity = 1000;

enum ui_node_type {
	UI_NODE_TYPE_LABEL,
	UI_NODE_TYPE_BUTTON,
	UI_NODE_TYPE_ROW,
	UI_NODE_TYPE_COLUMN,
	UI_NODE_TYPE_COUNT,
};

struct ui_node {
	enum ui_node_type type;
	uint32_t next_index;
	union {
		struct {
			char *text;
		} label;

		struct {
			char *text;
			bool is_pressed;
		} button;

		struct {
			uint32_t child_index;
			uint32_t padding;
			float y_alignment;
		} row;
	};
};

struct window {
	uint32_t width;
	uint32_t height;
	struct ui_node *nodes; // Freed by `window_destroy()`.
	size_t nodes_capacity;
	size_t nodes_count;
};

struct window *window_create(uint32_t width, uint32_t height) {
	struct window *window = malloc(sizeof *window);
	if (!window) {
		goto error1;
	}
	*window = (struct window){
		.width = width,
		.height = height,
		.nodes_capacity = initial_nodes_capacity,
	};
	window->nodes = malloc(initial_nodes_capacity*sizeof *window->nodes);
	if (!window->nodes) {
		goto error2;
	}
	return window;

error2:
	free(window);
error1:
	return NULL;
}

void window_destroy(struct window *window) {
	free(window->nodes);
	free(window);
}

void button(struct window *window, char *label) {
	
}
