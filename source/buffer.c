#include <assert.h>

#include <stddef.h>
#include <stdbool.h>
#include <string.h>
#include "buffer.h"
#include "list.h"

#define MIN(a, b) (((a) <= (b)) ? (a) : (b))

static const size_t initial_file_path_capacity = 3*1024;

static const size_t initial_selections_capacity = 100;

static const size_t initial_matches_capacity = 100;

static void selection_adjust_scroll(struct selection *selection, struct buffer_view *view) {
	if ((size_t)(selection - view->selections) != view->current_selection_index) {
		return;
	}
	// Adjust the x scroll.
	if (selection->end.x > view->scroll_x + view->page_width) {
		view->scroll_x = selection->end.x - view->page_width;
	}
	// Adjust the y scroll.
	if (selection->end.y > view->scroll_y + view->page_height) {
		view->scroll_y = selection->end.y - view->page_height;
	}
}

static void selection_move_down_line(struct selection *selection, struct buffer_view *view) {
	struct line *line = view->buffer->lines + selection->end.line_index;
	size_t line_length = list_get_count(&line->text);
	// If the cursor is at the last line, scroll down if needed and put it at the end of the line.
	if (line->next_index == BUFFER_NONE) {
		if (selection == buffer_view_get_current_selection(view) && selection->start.x == line_length) {
			buffer_view_scroll_down_line(view);
			return;
		}
		selection->start.x = line_length;
		return;
	}
	// Else, go down a line.
	line = view->buffer->lines + line->next_index;
	++selection->end.line_index;
	selection->end.x = MIN(selection->end.x, list_get_count(&line->text));
	++selection->end.y;
	selection_adjust_scroll(selection, view);
}

static void selection_move_right_character(struct selection *selection, struct buffer_view *view) {
	struct line *line = view->buffer->lines + selection->end.line_index;
	if (selection->end.x < list_get_count(&line->text)) {
		++selection->end.x;
		selection_adjust_scroll(selection, view);
		return;
	}
	selection_move_down_line(selection, view);
}

static void selection_delete(struct selection *selection, struct buffer_view *view) {
	if (!view->is_selecting) {
		return;
	}
	// TODO: Delete selection and adjust other selections.
	// TODO: Adjust selections in other views for this buffer.
}

static bool selection_insert_character(struct selection *selection, struct buffer_view *view, char character) {
	selection_delete(selection, view);
	struct line *line = view->buffer->lines + selection->end.line_index;
	if (!line_insert_character(line, selection->end.x, character)) {
		return false;
	}
	selection_move_right_character(selection, view);
	// TODO: Adjust selections in other views for this buffer.
	return true;
}

bool line_initialize(struct line *line, size_t capacity) {
	line->text = list_create(capacity, sizeof *line->text);
	if (!line->text) {
		goto error1;
	}
	line->highlight = list_create(capacity, sizeof *line->highlight);
	if (!line->highlight) {
		goto error2;
	}
	line->previous_index = BUFFER_NONE;
	line->next_index = BUFFER_NONE;
	return true;

error2:
	list_destroy(&line->text);
error1:
	*line = (struct line){0};
	return false;
}

void line_destroy(struct line *line) {
	list_destroy(&line->text);
	list_destroy(&line->highlight);
	*line = (struct line){0};
}

char line_get_character(struct line *line, size_t index) {
	if (index < list_get_count(&line->text)) {
		return line->text[index];
	}
	return '\0';
}

bool line_set_character(struct line *line, size_t index, char character) {
	if (index < list_get_count(&line->text)) {
		line->text[index] = character;
		return true;
	}
	return false;
}

bool line_insert_character(struct line *line, size_t index, char character) {
	if (index > list_get_count(&line->text)) {
		return false;
	}
	return list_insert(&line->text, (size_t)index, &character);
}

bool line_delete_range(struct line *line, size_t start_index, size_t count) {
	return list_remove_range(&line->text, start_index, count);
}

bool line_delete_character(struct line *line, size_t index) {
	return list_remove(&line->text, index);
}

bool buffer_initialize(struct buffer *buffer, size_t lines_capacity, size_t line_character_capaity) {
	buffer->file_path = list_create(initial_file_path_capacity, sizeof *buffer->file_path);
	if (!buffer->file_path) {
		goto error1;
	}
	buffer->lines = list_create(lines_capacity, sizeof *buffer->lines);
	if (!buffer->lines) {
		goto error2;
	}
	if (!list_push_back_uninitialized(&buffer->lines) || !line_initialize(buffer->lines, line_character_capaity)) {
		goto error3;
	}
	buffer->first_line_index = 0;
	buffer->last_line_index = 0;
	buffer->last_free_line_index = BUFFER_NONE;
	buffer->lines_count = 1;
	return true;

error3:
	list_destroy(&buffer->lines);
error2:
	list_destroy(&buffer->file_path);
error1:
	*buffer = (struct buffer){0};
	return false;
}

void buffer_destroy(struct buffer *buffer) {
	for (size_t i = 0; i < list_get_count(&buffer->lines); ++i) {
		line_destroy(buffer->lines + i);
	}
	list_destroy(&buffer->lines);
	list_destroy(&buffer->file_path);
	*buffer = (struct buffer){0};
}

bool buffer_view_initialize(struct buffer_view *view, struct buffer *buffer) {
	*view = (struct buffer_view){0};
	view->buffer = buffer;
	view->selections = list_create(initial_selections_capacity, sizeof *view->selections);
	if (!view->selections) {
		goto error1;
	}
	// Add the initial cursor to the selections.
	struct selection *selection = list_push_back_uninitialized(&view->selections);
	if (!selection) {
		goto error1;
	}
	*selection = (struct selection){.end.line_index = buffer->first_line_index};
	view->matches = list_create(initial_matches_capacity, sizeof *view->matches);
	if (!view->matches) {
		goto error2;
	}
	return true;

error2:
	list_destroy(&view->selections);
error1:
	return false;
}

void buffer_view_destroy(struct buffer_view *view) {
	list_destroy(&view->selections);
	list_destroy(&view->matches);
	*view = (struct buffer_view){0};
}

struct selection *buffer_view_get_current_selection(struct buffer_view *view) {
	return view->selections + view->current_selection_index;
}

void buffer_view_move_down_line(struct buffer_view *view) {
	assert(list_get_count(&view->selections));
	for (ssize_t i = (ssize_t)list_get_count(&view->selections); i > -1; --i) {
		selection_move_down_line(view->selections + i, view);
	}
}

void buffer_view_start_selecting(struct buffer_view *view) {
	if (view->is_selecting) {
		return;
	}
	view->is_selecting = true;
	for (size_t i = 0; i < list_get_count(&view->selections); ++i) {
		struct selection *selection = view->selections + i;
		selection->start = selection->end;
	}
}

void buffer_view_stop_selecting(struct buffer_view *view) {
	view->is_selecting = false;
}

bool buffer_view_insert_character(struct buffer_view *view, char character) {
	for (size_t i = 0; i < list_get_count(&view->selections); ++i) {
		if (!selection_insert_character(view->selections + i, view, character)) {
			return false;
		}
	}
	return true;
}

void buffer_view_scroll_down_line(struct buffer_view *view) {
	if (view->scroll_y < view->buffer->lines_count + view->page_height) {
		++view->scroll_y;
	}
}
