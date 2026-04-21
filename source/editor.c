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
		return buffer->new_text + piece->text.index + offset;
	}
	return buffer->original_text + piece->text.index + offset;
}

// Takes 3 pieces and merges any adjacent pieces into one.
static void buffer_merge_pieces(struct buffer *buffer, struct piece *left, struct piece *middle, struct piece *right) {
	if (left->is_new == middle->is_new && left->text.index + left->text.length == middle->text.index) {
		// Merge the left and the middle.
		left->text.length += middle->text.length;
		buffer_delete_piece(buffer, middle - buffer->pieces);
		middle = left;
	}

	// if (middle->is_new == right->is_new && middle->text.index + middle->text.length == right->text.index) {
	// 	// Merge the middle and the right.
	// 	middle->text.length += right->text.length;
	// 	buffer_delete_piece(buffer, right - buffer->pieces);
	// }
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
	
	// Add the initial piece.
	struct piece first_piece = {
		.previous_piece_index = PIECE_NONE,
		.next_piece_index = PIECE_NONE,
		.is_new = true,
	};
	if (!list_push_back(&buffer->pieces, &first_piece)) {
		goto error3;
	}
	buffer->first_piece = buffer->pieces;
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
		struct span text = (*piece)->text;
		if ((*piece)->next_piece_index == PIECE_NONE || (position >= current_piece_offset && position < current_piece_offset + text.length)) {
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
	struct piece *new_piece = buffer->last_free_piece;
	// Try to find a free piece first.
	if (new_piece) {
		if (buffer->last_free_piece->previous_piece_index == PIECE_NONE) {
			buffer->last_free_piece = NULL;
		} else {
			buffer->last_free_piece = buffer->pieces + buffer->last_free_piece->previous_piece_index;
		}
	// Allocate a new piece if none are free.
	} else {
		new_piece = list_push_back_uninitialized(&buffer->pieces);
		if (!new_piece) {
			return NULL;
		}
	}

	// Copy the source if needed.
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

bool buffer_split_piece(struct buffer *buffer, uint32_t piece_index, uint32_t offset, struct piece **left, struct piece **right) {
	// Insert the new piece.
	struct piece *new_piece = buffer_insert_piece_before(buffer, piece_index, NULL);
	if (!new_piece) {
		return false;
	}
	struct piece *piece = buffer->pieces + piece_index;

	// Fix the new piece.
	new_piece->text = (struct span){
		.index = piece->text.index,
		.length = offset,
	};
	new_piece->is_new = piece->is_new;

	// Fix the original piece.
	piece->text.index += offset;
	piece->text.length -= offset;
	*left = new_piece;
	*right = piece;
	return true;
}

void buffer_delete_piece(struct buffer *buffer, uint32_t piece_index) {
	struct piece *piece = buffer->pieces + piece_index;
	// Fix the previous piece's link.
	if (piece->previous_piece_index == PIECE_NONE) {
		buffer->first_piece = buffer->pieces + piece->next_piece_index;
	} else {
		struct piece *previous_piece = buffer->pieces + piece->previous_piece_index;
		previous_piece->next_piece_index = piece->next_piece_index;
	}

	// Fix the next piece's link.
	if (piece->next_piece_index != PIECE_NONE) {
		struct piece *next_piece = buffer->pieces + piece->next_piece_index;
		next_piece->previous_piece_index = piece->previous_piece_index;
	}

	// Add the piece to the stack of free pieces.
	if (buffer->last_free_piece == NULL) {
		piece->previous_piece_index = PIECE_NONE;
		buffer->last_free_piece = piece;
		return;
	}
	piece->previous_piece_index = buffer->last_free_piece - buffer->pieces;
	buffer->last_free_piece = piece;
}

bool buffer_insert_character(struct buffer *buffer, uint32_t position, char8 character) {
	// Add the character to the new text arena.
	if (!list_push_back(&buffer->new_text, &character)) {
		return false;
	}
	uint32_t character_index = list_get_count(&buffer->new_text) - 1;
	
	// Find which piece the insertion point is in.
	struct piece *piece = {0};
	uint32_t offset = 0;
	buffer_get_piece_and_offset(buffer, position, &piece, &offset);
	uint32_t piece_index = piece - buffer->pieces;

	// Split the piece.
	struct piece *left = NULL;
	struct piece *right = NULL;
	if (!buffer_split_piece(buffer, piece_index, offset, &left, &right)) {
		return false;
	}

	// Insert a new piece between the halves.
	struct piece *middle = buffer_insert_piece_before(buffer, right - buffer->pieces, NULL);
	if (!middle) {
		return false;
	}
	*middle = (struct piece){
		.text = {
			.index = character_index,
			.length = 1,
		},
		.is_new = true,
	};

	// Merge any pieces with adjacent text.
	buffer_merge_pieces(buffer, left, middle, right);
	return true;
}

void buffer_print_piece(struct buffer *buffer, struct piece *piece) {
	char *source_name = (piece->is_new) ? "new" : "original";
	char *source_text = (char*)((piece->is_new) ? buffer->new_text : buffer->original_text);
	printf("%lu %s index=%u, length=%u, previous=%u, next=%u", piece - buffer->pieces, source_name, piece->text.index, piece->text.length, piece->previous_piece_index, piece->next_piece_index);
	if (source_text) {
		printf(", text=`%.*s`", piece->text.length, source_text + piece->text.index);
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

void buffer_print_free_pieces(struct buffer *buffer) {
	struct piece *current_piece = buffer->last_free_piece;
	if (!current_piece) {
		return;
	}

	while (true) {
		buffer_print_piece(buffer, current_piece);
		if (current_piece->previous_piece_index == PIECE_NONE) {
			return;
		}
		current_piece = buffer->pieces + current_piece->previous_piece_index;
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
