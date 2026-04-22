#ifndef BUFFER_H

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

// A UTF-8 code unit.
typedef uint8_t char8;

// An entire unicode code point.
typedef uint32_t char32;

// A span of text in a buffer.
struct selection {
	uint32_t index;
	uint32_t length;
};

// A string with a pre-computed length. Assumed NOT to be null-terminated.
struct slice {
	char8 *text;
	uint32_t length;
};

// A piece of text being edited. Can be edited by multiple `buffer_view`s at once.
struct buffer {
	char8 *original_text; // Points to an `mmap()`ed chunk of memory if a file has been read into the buffer.
	char8 *new_text; // Points to a list.
	struct piece *pieces; // Points to a list.
	uint32_t first_piece_index; // A linked list of pieces that are currently in use.
	uint32_t last_free_piece_index; // A stack of pieces that have been deleted.
};

// Used to edit a buffer with selections.
struct buffer_view;

// Returns true if a memory error occurred. Do NOT call `buffer_destroy()` on `buffer` if this
// function fails.
bool buffer_initialize(struct buffer *buffer, uint32_t new_text_capacity, uint32_t pieces_capacity);

void buffer_destroy(struct buffer *buffer);

void buffer_clear(struct buffer *buffer);

bool buffer_read_from_file(struct buffer *buffer, FILE *file);

bool buffer_write_to_file(struct buffer *buffer, FILE *file);

// Assumes `index` is in the bounds of `buffer`.
// TODO: Make this use `char32`.
char8 buffer_get_character(struct buffer *buffer, uint32_t index);

// Assumes `index` is in the bounds of `buffer`.
// TODO: Make this use `char32`.
void buffer_set_character(struct buffer *buffer, uint32_t index, char8 character);

// Assumes `index` is in the bounds of `buffer`. Returns true if no memory errors occurred.
// TODO: Make this use `char32` and accept a string instead of a single character.
bool buffer_insert_character(struct buffer *buffer, uint32_t index, char8 character);

bool buffer_insert_slice(struct buffer *buffer, uint32_t index, struct slice slice);

// Assumes `index` is in the bounds of `buffer`.
void buffer_delete_character(struct buffer *buffer, uint32_t index);

// Assumes `selection` is in the bounds of `buffer`.
void buffer_delete_selection(struct buffer *buffer, struct selection selection);

// Prints the active pieces in `buffer`'s piece table for debugging.
void buffer_debug_print_pieces(struct buffer *buffer);

// Prints the deleted piece in `buffer`'s piece table for debugging.
void buffer_debug_print_free_pieces(struct buffer *buffer);

bool buffer_view_initialize(struct buffer_view *buffer_view);

void buffer_view_destroy(struct buffer_view *buffer_view);

uint32_t buffer_view_coordinates_to_index(struct buffer_view *buffer_view, uint32_t x, uint32_t y);

#endif // BUFFER_H
