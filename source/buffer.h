#ifndef BUFFER_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

// Sentinel value used in `buffer` to indicate a line index is invalid.
#define BUFFER_NONE SIZE_MAX

// A position in a buffer.
struct mark {
	size_t x; // Column.
	size_t y; // Row.
	size_t line_index;
};

// A span of text in a buffer.
struct selection {
	struct mark start; // The point where the user started selecting.
	struct mark end; // The point where the cursor is.
};

struct line {
	size_t previous_index;
	size_t next_index;
	char *text; // Points to a list. Doesn't end with a newline. Not null terminated. Tabs not expanded.
	char *highlight; // Points to a list. Doesn't end with a newline. Not null terminated. Tabs not expanded.
};

// A piece of text being edited. Can be edited by multiple `buffer_view`s at once.
struct buffer {
	char *file_path; // Points to a list. Not null terminated.
	struct line *lines; // Points to a list.
	size_t first_line_index;
	size_t last_line_index;
	size_t last_free_line_index;
	size_t lines_count; // The number of lines actually being used.
};

// Used to edit a buffer with selections.
struct buffer_view {
	struct buffer *buffer;
	struct selection *selections; // Points to a list.
	size_t current_selection_index;
	struct selection *matches; // Points to a list.
	size_t current_match_index;
	bool is_selecting; // Whether the user is selecting text.
	size_t scroll_x;
	size_t scroll_y;
	size_t page_width;
	size_t page_height;
};

// Returns false if a memory error occurred.
bool line_initialize(struct line *line, size_t capacity);

void line_destroy(struct line *line);

// Returns '\0' if `index` is out of bounds.
char line_get_character(struct line *line, size_t index);

// Returns false if `index` is out of bounds.
bool line_set_character(struct line *line, size_t index, char character);

// Returns false if `index` is out of bounds or a memory error occurred.
bool line_insert_character(struct line *line, size_t index, char character);

// Returns false if `start_index` or `start_index + count` is out of bounds or a memory error occurred.
bool line_delete_range(struct line *line, size_t start_index, size_t count);

// Returns false if `index` is out of bounds or a memory error occurred.
bool line_delete_character(struct line *line, size_t index);

// Returns false if a memory error occurred.
bool buffer_initialize(struct buffer *buffer, size_t lines_capacity, size_t line_character_capaity);

void buffer_destroy(struct buffer *buffer);

// Returns '\0' if `position` is out of bounds.
// char buffer_get_character(struct buffer *buffer, struct mark position);

// Returns false if `position` is out of bounds.
// bool buffer_set_character(struct buffer *buffer, struct mark position, char character);

// Returns false if a memory error occurred.
bool buffer_view_initialize(struct buffer_view *view, struct buffer *buffer);

// Doesn't destroy the buffer `view` points to internally.
void buffer_view_destroy(struct buffer_view *view);

// Converts position in text without tabs expanded/lines wrapped to a position with everything
// expanded and wrapped.
size_t buffer_view_get_screen_position(struct buffer_view *view, struct mark logical_position);

struct selection *buffer_view_get_current_selection(struct buffer_view *view);

void buffer_view_move_up_line(struct buffer_view *view);

void buffer_view_move_down_line(struct buffer_view *view);

void buffer_view_move_left_character(struct buffer_view *view);

void buffer_view_move_right_character(struct buffer_view *view);

void buffer_view_start_selecting(struct buffer_view *view);

void buffer_view_stop_selecting(struct buffer_view *view);

void buffer_view_delete_selection(struct buffer_view *view);

bool buffer_view_delete_character_left(struct buffer_view *view);

bool buffer_view_delete_character_right(struct buffer_view *view);

bool buffer_view_insert_character(struct buffer_view *view, char character);

void buffer_view_scroll_up_line(struct buffer_view *view);

void buffer_view_scroll_down_line(struct buffer_view *view);

void buffer_view_scroll_left_character(struct buffer_view *view);

void buffer_view_scroll_right_character(struct buffer_view *view);

#endif // BUFFER_H
