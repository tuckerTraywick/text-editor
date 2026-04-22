#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include "buffer.h"
#include "list.h"

// Sentinel used as a piece's next/previous index to indicate there is no piece before/after it.
#define PIECE_NONE UINT32_MAX

struct piece {
	uint32_t previous_piece_index; // The index of the previous piece in the chain.
	uint32_t next_piece_index; // The index of the next piece in the chain.
	uint32_t text_index;
	uint32_t text_length;
	bool is_new; // Whether the piece refers to the original file's text or newly added text.
};

struct buffer_view {
	struct buffer *buffer;
	char *rendered_text; // Ponts to a list.
	struct selection *selections; // Points to a list.
	uint32_t current_selection_index;
	struct selection *matches; // Points to a list.
	uint32_t current_match_index;
	uint32_t render_start_index;
	uint32_t scroll_x;
	uint32_t scroll_y;
	uint32_t page_height;
	uint32_t page_width;
};

// Returns the piece containing the character at `index` and the character's offset within the
// piece including the character after the piece. Assumes `index` is in the bounds of `buffer`.
// static void buffer_get_piece_and_offset(struct buffer *buffer, uint32_t index, struct piece **piece, uint32_t *offset) {
// 	*piece = buffer->pieces + buffer->first_piece_index;
// 	uint32_t current_piece_offset = 0;
// 	while (true) {
// 		if ((*piece)->next_piece_index == PIECE_NONE || (index >= current_piece_offset && index <= current_piece_offset + (*piece)->text_length)) {
// 			*offset = index - current_piece_offset;
// 			return;
// 		}
// 		*piece = buffer->pieces + (*piece)->next_piece_index;
// 		current_piece_offset += (*piece)->text_length;
// 	}
// }

// Assumes `index` is in the bounds of `buffer`.
// TODO: Make this use `char32`.
// static char8 *buffer_get_character_pointer(struct buffer *buffer, uint32_t index) {
// 	struct piece *piece = {0};
// 	uint32_t offset = 0;
// 	buffer_get_piece_and_offset(buffer, index, &piece, &offset);
// 	if (piece->is_new) {
// 		return buffer->new_text + piece->text_index + offset;
// 	}
// 	return buffer->original_text + piece->text_index + offset;
// }


// If `source` is null, appends an empty piece. Returns a pointer to the new piece if no memory
// errors occurred.
// TODO: Remove `source` argument. Rename to `buffer_new_piece_before()`.
// static struct piece *buffer_insert_piece_before(struct buffer *buffer, uint32_t destination_index, struct piece *source) {
// 	// Allocate a new piece.
// 	struct piece *new_piece = list_push_back_uninitialized(&buffer->pieces);
// 	if (!new_piece) {
// 		return NULL;
// 	}

// 	// Copy the source if needed.
// 	if (source) {
// 		*new_piece = *source;
// 	} else {
// 		*new_piece = (struct piece){0};
// 	}

// 	// Fix the new piece's links.
// 	struct piece *destination = buffer->pieces + destination_index;
// 	new_piece->previous_piece_index = destination->previous_piece_index;
// 	new_piece->next_piece_index = destination - buffer->pieces;

// 	// Update the pointer to the first piece if we are inserting before it.
// 	if (destination->previous_piece_index == PIECE_NONE) {
// 		buffer->first_piece_index = new_piece - buffer->pieces;
// 	// Else, fix the previous piece's link.
// 	} else {
// 		struct piece *previous = buffer->pieces + destination->previous_piece_index;
// 		previous->next_piece_index = new_piece - buffer->pieces;
// 	}

// 	// Fix the destination piece's link.
// 	destination->previous_piece_index = new_piece - buffer->pieces;
// 	return new_piece;
// }

// Deletes the piece at `piece_index` and adds it to the list of free pieces. Assumes that
// `piece_index` points to a valid piece and that you will not call this function when the buffer
// only has 1 piece.
// static void buffer_delete_piece(struct buffer *buffer, uint32_t piece_index) {
// 	struct piece *piece = buffer->pieces + piece_index;
// 	// Fix the previous piece's link.
// 	if (piece->previous_piece_index == PIECE_NONE) {
// 		buffer->first_piece_index = piece->next_piece_index;
// 	} else {
// 		struct piece *previous_piece = buffer->pieces + piece->previous_piece_index;
// 		previous_piece->next_piece_index = piece->next_piece_index;
// 	}

// 	// Fix the next piece's link.
// 	if (piece->next_piece_index != PIECE_NONE) {
// 		struct piece *next_piece = buffer->pieces + piece->next_piece_index;
// 		next_piece->previous_piece_index = piece->previous_piece_index;
// 	}

// 	// Add the piece to the stack of free pieces.
// 	if (buffer->last_free_piece_index == PIECE_NONE) {
// 		piece->previous_piece_index = PIECE_NONE;
// 		buffer->last_free_piece_index = piece - buffer->pieces;
// 		return;
// 	}
// 	piece->previous_piece_index = buffer->last_free_piece_index;
// 	buffer->last_free_piece_index = piece - buffer->pieces;
// }

static void buffer_debug_print_piece(struct buffer *buffer, struct piece *piece) {
	char *source_name = (piece->is_new) ? "new" : "original";
	char *source_text = (char*)((piece->is_new) ? buffer->new_text : buffer->original_text);
	printf("%lu %s index=%u, length=%u, previous=%u, next=%u", piece - buffer->pieces, source_name, piece->text_index, piece->text_length, piece->previous_piece_index, piece->next_piece_index);
	if (source_text) {
		printf(", text=`%.*s`", piece->text_length, source_text + piece->text_index);
	}
	printf("\n");
}

bool buffer_initialize(struct buffer *buffer, uint32_t new_text_capacity, uint32_t pieces_capacity) {
	*buffer = (struct buffer){
		.first_piece_index = PIECE_NONE,
		.last_free_piece_index = PIECE_NONE,
		.new_text = list_create(new_text_capacity, sizeof *buffer->new_text),
	};
	if (!buffer->new_text) {
		goto error1;
	}
	buffer->pieces = list_create(pieces_capacity, sizeof *buffer->pieces);
	if (!buffer->pieces) {
		goto error2;
	}

	return true;

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

// char8 buffer_get_character(struct buffer *buffer, uint32_t index) {
// 	return *buffer_get_character_pointer(buffer, index);
// }

// void buffer_set_character(struct buffer *buffer, uint32_t index, char8 character) {
// 	*buffer_get_character_pointer(buffer, index) = character;
// }

// bool buffer_insert_character(struct buffer *buffer, uint32_t index, char8 character) {
// 	// Add the character to the new text arena.
// 	if (!list_push_back(&buffer->new_text, &character)) {
// 		return false;
// 	}
// 	uint32_t character_index = list_get_count(&buffer->new_text) - 1;
	
// 	// Find which piece the insertion point is in.
// 	struct piece *piece = {0};
// 	uint32_t offset = 0;
// 	buffer_get_piece_and_offset(buffer, index, &piece, &offset);
// 	uint32_t piece_index = piece - buffer->pieces;
// }

void buffer_debug_print_pieces(struct buffer *buffer) {
	if (buffer->first_piece_index == PIECE_NONE) {
		return;
	}

	struct piece *current_piece = buffer->pieces + buffer->first_piece_index;
	while (true) {
		buffer_debug_print_piece(buffer, current_piece);
		if (current_piece->next_piece_index == PIECE_NONE) {
			return;
		}
		current_piece = buffer->pieces + current_piece->next_piece_index;
	}
}

void buffer_debug_print_free_pieces(struct buffer *buffer) {
	if (buffer->last_free_piece_index == PIECE_NONE) {
		return;
	}

	struct piece *current_piece = buffer->pieces + buffer->last_free_piece_index;
	while (true) {
		buffer_debug_print_piece(buffer, current_piece);
		if (current_piece->previous_piece_index == PIECE_NONE) {
			return;
		}
		current_piece = buffer->pieces + current_piece->previous_piece_index;
	}
}

#undef PIECE_NONE
