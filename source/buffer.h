#ifndef BUFFER_H

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

// Sentinel value used in `buffer` to indicate a line index is invalid.
#define BUFFER_NONE UINT32_MAX

// A UTF-8 code unit.
typedef uint8_t char8;

// An entire unicode code point.
typedef uint32_t char32;

// A position in a buffer.
struct mark {
	uint32_t x; // Column.
	uint32_t y; // Row.
};

// A span of text in a buffer.
struct selection {
	struct mark start;
	struct mark end; // The character AFTER the last character selected.
};

struct line {
	uint32_t previous_index;
	uint32_t next_index;
	char8 *text; // Points to a list. Doesn't end with a newline. Not null terminated.
};

// A piece of text being edited. Can be edited by multiple `buffer_view`s at once.
struct buffer {
	char *file_path; // Points to a list. Not null terminated.
	struct line *lines; // Points to a list.
	uint32_t first_line_index;
	uint32_t last_line_index;
	uint32_t last_free_line_index;
};

// Used to edit a buffer with selections.
struct buffer_view {
	struct buffer *buffer;
	struct selection *selections; // Points to a list.
	uint32_t current_selection_index;
	struct selection *matches; // Points to a list.
	uint32_t current_match_index;
	uint32_t scroll_x;
	uint32_t scroll_y;
	uint32_t page_width;
	uint32_t page_height;
};

// Returns false if a memory error occurred.
bool buffer_initialize(struct buffer *buffer, uint32_t lines_capacity, uint32_t line_character_capaity);

void buffer_destroy(struct buffer *buffer);

// Returns false if a memory error occurred.
bool line_initialize(struct line *line, uint32_t capacity);

void line_destroy(struct line *line);

// Returns '\0' if `index` is out of bounds.
char8 line_get_character(struct line *line, uint32_t index);

// Returns false if a memory error occurred.
bool line_set_character(struct line *line, uint32_t index, char8 character);

// Returns false if `index` is out of bounds or a memory error occurred.
bool line_insert_character(struct line *line, uint32_t index, char8 character);

// Returns false if `start_index` or `start_index + count` is out of bounds or a memory error occurred.
bool line_delete_range(struct line *line, uint32_t start_index, uint32_t count);

#endif // BUFFER_H
