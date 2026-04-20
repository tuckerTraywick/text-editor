#ifndef EDITOR_H

#include <stdbool.h>
#include <stdint.h>

// A UTF-8 code unit.
typedef uint8_t char8;

// An entire unicode code point.
typedef uint32_t char32;

struct selection {
	uint32_t index;
	uint32_t length;
};

struct piece {
	uint32_t previous_piece_index; // The index of the previous piece in the chain.
	uint32_t next_piece_index; // The index of the next piece in the chain.
	struct selection selection; // Relative to the start of the arena this piece points to.
	bool is_new;
};

// A piece of text being edited stored as a piece table.
struct buffer {
	char8 *original_text; // Points to an `mmap()`ed chunk of memory if a file has been read into the buffer.
	char8 *new_text; // Points to a list.
	struct piece *pieces; // Points to a list.
	struct piece *free_pieces; // A linked list of pieces that have been deleted. Not a list. Don't free.
	struct piece *first_piece;
};

// A view used to edit a buffer. Multiple views can edit the same buffer.
struct buffer_view {
	struct buffer *buffer;
	struct selection *selections; // Points to a list.
	uint32_t current_selection_index;
	struct selection *matches; // Points to a list. The matches for the find term in the buffer being viewed.
	uint32_t current_match_index;
};

// Returns true if a memory error occurred. Do NOT call `buffer_destroy()` on `buffer` if this
// function fails.
bool buffer_initialize(struct buffer *buffer, uint32_t new_text_capacity, uint32_t pieces_capacity);

void buffer_destroy(struct buffer *buffer);

// Returns the piece containing the character at `position` and the character's offset within the
// piece. Assumes `position` is in the bounds of `buffer`.
void buffer_get_piece_and_offset(struct buffer *buffer, uint32_t position, struct piece **piece, uint32_t *offset);

// Assumes `position` is in the bounds of `buffer`.
// TODO: Make this use `char32`.
char8 buffer_get_character(struct buffer *buffer, uint32_t position);

// Assumes `position` is in the bounds of `buffer`.
// TODO: Make this use `char32`.
char8 buffer_get_character(struct buffer *buffer, uint32_t position);

// Assumes `position` is in the bounds of `buffer`.
// TODO: Make this use `char32`.
void buffer_set_character(struct buffer *buffer, uint32_t position, char8 character);

// If `source` is null, appends an empty piece. Returns a pointer to the new piece if no memory
// errors occurred.
struct piece *buffer_insert_piece_before(struct buffer *buffer, struct piece *destination, struct piece *source);

// Splits `piece` in half at `offset`. Returns both halves and true if no memory errors occurred.
bool buffer_split_piece(struct buffer *buffer, struct piece *piece, uint32_t offset, struct piece **left, struct piece **right);

// Assumes `position` is in the bounds of `buffer`.
// TODO: Make this use `char32` and accept a string instead of a single character.
bool buffer_insert_character(struct buffer *buffer, uint32_t position, char8 character);

void buffer_print_piece(struct buffer *buffer, struct piece *piece);

void buffer_print_pieces(struct buffer *buffer);

void setup_ncurses(void);

void teardown_ncurses(void);

#endif // EDITOR_H
