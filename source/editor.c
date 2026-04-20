#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <ncurses.h>
#include "editor.h"
#include "list.h"

// Sentinal used as a piece's next/previous index to indicate there is no piece before/after it.
#define PIECE_NONE UINT32_MAX

// A UTF-8 code unit.
typedef char char8;

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
	bool is_original;
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
bool buffer_initialize(struct buffer *buffer, uint32_t new_text_capacity, uint32_t pieces_capacity) {
	// Initialize the buffer's arenas.
	*buffer = (struct buffer){0};
	buffer->new_text = list_create(new_text_capacity, sizeof *buffer->new_text);
	if (!buffer->new_text) {
		goto error1;
	}
	buffer->pieces = list_create(pieces_capacity, sizeof *buffer->pieces);
	if (!buffer->pieces) {
		goto error2;
	}
	buffer->first_piece = buffer->pieces;

	// Add the initial piece.
	struct piece first_piece = {
		.previous_piece_index = PIECE_NONE,
		.next_piece_index = PIECE_NONE,
	};
	if (!list_push_back(&buffer->pieces, &first_piece)) {
		goto error3;
	}
	return true;

error3:
	list_destroy(&buffer->pieces);
error2:
	list_destroy(&buffer->new_text);
error1:
	*buffer = (struct buffer){0};
	return false;
}

void buffer_destroy(struct buffer *buffer) {
	list_destroy(&buffer->pieces);
	list_destroy(&buffer->new_text);
	// TODO: Unmap `buffer->old_text` if it is not null.
	*buffer = (struct buffer){0};
}

// Returns the piece containing the character at `position` and the character's offset within the
// piece. Assumes `position` is in the bounds of `buffer`.
void buffer_get_piece_and_offset(struct buffer *buffer, uint32_t position, struct piece **piece, uint32_t *offset) {
	*piece = buffer->pieces;
	uint32_t current_piece_offset = 0;
	while (true) {
		struct selection text = (*piece)->selection;
		if (position >= current_piece_offset && position <= current_piece_offset + text.length) {
			*offset = position - current_piece_offset;
			return;
		}
		*piece = buffer->pieces + (*piece)->next_piece_index;
		current_piece_offset += text.length;
	}
}

// Assumes `position` is in the bounds of `buffer`.
// TODO: Make this use `char32`.
char8 *buffer_get_character_pointer(struct buffer *buffer, uint32_t position) {
	struct piece *piece = {0};
	uint32_t offset = 0;
	buffer_get_piece_and_offset(buffer, position, &piece, &offset);
	if (piece->is_original) {
		return buffer->original_text + piece->selection.index + offset;
	}
	return buffer->new_text + piece->selection.index + offset;
}

// Assumes `position` is in the bounds of `buffer`.
// TODO: Make this use `char32`.
char8 buffer_get_character(struct buffer *buffer, uint32_t position) {
	return *buffer_get_character_pointer(buffer, position);
}

// Assumes `position` is in the bounds of `buffer`.
// TODO: Make this use `char32`.
void buffer_set_character(struct buffer *buffer, uint32_t position, char8 character) {
	*buffer_get_character_pointer(buffer, position) = character;
}

// If `source` is null, appends an empty piece. Returns a pointer to the new piece if no memory
// errors occurred.
struct piece *buffer_insert_piece_before(struct buffer *buffer, struct piece *destination, struct piece *source) {
	struct piece *new_piece = buffer->free_pieces;
	// Try to find a free piece first.
	if (new_piece) {
		if (buffer->free_pieces->next_piece_index) {
			buffer->free_pieces = buffer->pieces + buffer->free_pieces->next_piece_index;
		} else {
			buffer->free_pieces = NULL;
		}
	// Allocate a new piece if none are available.
	} else {
		new_piece = list_push_back_uninitialized(&buffer->pieces);
		if (!new_piece) {
			return NULL;
		}
	}

	if (source) {
		*new_piece = *source;
	} else {
		*new_piece = (struct piece){0};
	}

	// Fix the new piece's links.
	new_piece->previous_piece_index = destination->previous_piece_index;
	new_piece->next_piece_index = destination - buffer->pieces;

	// Update the pointer to the first piece if we are inserting before it.
	if (destination->previous_piece_index == PIECE_NONE) {
		buffer->first_piece = new_piece;
	// Else, fix the previous piece's link.
	} else {
		struct piece *previous = buffer->pieces + destination->previous_piece_index;
		previous->next_piece_index = new_piece - buffer->pieces;
	}

	// Fix the destination piece's link.
	destination->previous_piece_index = new_piece - buffer->pieces;
	return new_piece;
}

// Splits `piece` in half at `offset`. Returns both halves and true if no memory errors occurred.
bool buffer_split_piece(struct buffer *buffer, struct piece *piece, uint32_t offset, struct piece **left, struct piece **right) {
	// Insert the new piece.
	struct piece *new_piece = buffer_insert_piece_before(buffer, piece, NULL);
	if (!new_piece) {
		return false;
	}

	// Fix the new piece.
	*new_piece = (struct piece){
		.selection = {
			.index = piece->selection.index,
			.length = offset,
		},
		.is_original = piece->is_original,
	};

	// Fix the original piece.
	piece->selection.index = offset + 1;
	piece->selection.length -= offset;
	*left = new_piece;
	*right = piece;
	return true;
}

// Assumes `position` is in the bounds of `buffer`.
// TODO: Make this use `char32` and accept a string instead of a single character.
bool buffer_insert_character(struct buffer *buffer, uint32_t position, char8 character);

void buffer_print_piece(struct buffer *buffer, struct piece *piece) {
	char *source_name = (piece->is_original) ? "original" : "new";
	char *source_text = (piece->is_original) ? buffer->original_text : buffer->new_text;
	printf("%lu %s index=%u, length=%u", piece - buffer->pieces, source_name, piece->selection.index, piece->selection.length);
	if (source_text) {
		printf(", text=`%.*s`", piece->selection.length, source_text);
	}
	printf("\n");
}

void buffer_print_pieces(struct buffer *buffer) {
	struct piece *current_piece = buffer->pieces;
	while (true) {
		buffer_print_piece(buffer, current_piece);
		if (current_piece->next_piece_index == PIECE_NONE) {
			return;
		}
		current_piece = buffer->pieces + current_piece->next_piece_index;
	}
}

void setup_ncurses(void) {
	initscr();
	raw();
	noecho();
	keypad(stdscr, TRUE);
	set_escdelay(0);
}

void teardown_ncurses(void) {
	endwin();
}

int main(void) {
	const uint32_t initial_text_capacity = 1024;
	const uint32_t initial_piece_capacity = 100;
	struct buffer buffer = {0};
	if (!buffer_initialize(&buffer, initial_text_capacity, initial_piece_capacity)) {
		printf("Error initializing piece buffer.\n");
		return 1;
	}

	struct piece *old_piece = NULL;
	uint32_t offset = 0;
	buffer_get_piece_and_offset(&buffer, 0, &old_piece, &offset);
	buffer_print_piece(&buffer, old_piece);
	printf("offset = %u\n", offset);

	struct piece new_piece = {
		.is_original = true,
		.selection = {
			.index = 3,
			.length = 5,
		},
	};
	struct piece *new_piece_ptr = buffer_insert_piece_before(&buffer, old_piece, &new_piece);
	buffer_print_piece(&buffer, new_piece_ptr);


	buffer_print_pieces(&buffer);

	setup_ncurses();
	teardown_ncurses();

	buffer_destroy(&buffer);
	return 0;
}
