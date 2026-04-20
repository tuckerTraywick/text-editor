#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <ncurses.h>
#include "editor.h"
#include "list.h"

// Assumes `position` is in the bounds of `buffer`.
// TODO: Make this use `char32`.
static char8 *buffer_get_character_pointer(struct buffer *buffer, uint32_t position) {
	struct piece *piece = {0};
	uint32_t offset = 0;
	buffer_get_piece_and_offset(buffer, position, &piece, &offset);
	if (piece->is_new) {
		return buffer->new_text + piece->selection.index + offset;
	}
	return buffer->original_text + piece->selection.index + offset;
}

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

void buffer_get_piece_and_offset(struct buffer *buffer, uint32_t position, struct piece **piece, uint32_t *offset) {
	*piece = buffer->first_piece;
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

char8 buffer_get_character(struct buffer *buffer, uint32_t position) {
	return *buffer_get_character_pointer(buffer, position);
}

void buffer_set_character(struct buffer *buffer, uint32_t position, char8 character) {
	*buffer_get_character_pointer(buffer, position) = character;
}

struct piece *buffer_insert_piece_before(struct buffer *buffer, uint32_t destination_index, struct piece *source) {
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
	struct piece *destination = buffer->pieces + destination_index;
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

// bool buffer_split_piece(struct buffer *buffer, struct piece *piece, uint32_t offset, struct piece **left, struct piece **right) {
// 	// Insert the new piece.
// 	struct piece *new_piece = buffer_insert_piece_before(buffer, piece, NULL);
// 	if (!new_piece) {
// 		return false;
// 	}

// 	// Fix the new piece.
// 	*new_piece = (struct piece){
// 		.selection = {
// 			.index = piece->selection.index,
// 			.length = offset,
// 		},
// 		.is_new = piece->is_new,
// 	};

// 	// Fix the original piece.
// 	piece->selection.index = offset + 1;
// 	piece->selection.length -= offset;
// 	*left = new_piece;
// 	*right = piece;
// 	return true;
// }

void buffer_print_piece(struct buffer *buffer, struct piece *piece) {
	char *source_name = (piece->is_new) ? "new" : "original";
	char *source_text = (char*)((piece->is_new) ? buffer->new_text : buffer->original_text);
	printf("%lu %s index=%u, length=%u, previous=%u, next=%u", piece - buffer->pieces, source_name, piece->selection.index, piece->selection.length, piece->previous_piece_index, piece->next_piece_index);
	if (source_text) {
		printf(", text=`%.*s`", piece->selection.length, source_text);
	}
	printf("\n");
}

void buffer_print_pieces(struct buffer *buffer) {
	struct piece *current_piece = buffer->first_piece;
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
