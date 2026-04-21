#include <stddef.h>
#include <stdio.h>
#include "test.h"
#include "editor.h"
#include "list.h"

static void test_buffer_initialize_and_destroy(void) {
	struct buffer buffer = {0};
	buffer_initialize(&buffer, 1, 1);
	assert_eq((void*)buffer.pieces, (void*)buffer.first_piece, "%p", "%p");
	assert_eq(list_get_capacity(&buffer.pieces), (size_t)1, "%zu", "%zu");
	assert_eq(list_get_count(&buffer.pieces), (size_t)1, "%zu", "%zu");

	buffer_destroy(&buffer);
	assert_eq((void*)buffer.original_text, NULL, "%p", "%p");
	assert_eq((void*)buffer.new_text, NULL, "%p", "%p");
	assert_eq((void*)buffer.pieces, NULL, "%p", "%p");
	assert_eq((void*)buffer.free_pieces, NULL, "%p", "%p");
	assert_eq((void*)buffer.first_piece, NULL, "%p", "%p");
}

static void test_buffer_insert_piece_before(void) {
	struct buffer buffer = {0};
	buffer_initialize(&buffer, 1, 1);

	struct piece *piece1 = buffer_insert_piece_before(&buffer, 0, NULL);
	assert_eq(piece1 - buffer.pieces, (size_t)1, "%zu", "%zu");
	assert_eq(piece1->previous_piece_index, PIECE_NONE, "%u", "%u");
	assert_eq(piece1->next_piece_index, 0, "%u", "%u");
	assert_eq(piece1->selection.index, 0, "%u", "%u");
	assert_eq(piece1->selection.length, 0, "%u", "%u");
	assert_eq(piece1->is_new, 0, "%u", "%u");
	assert_eq((void*)buffer.first_piece, (void*)piece1, "%p", "%p");
	assert_eq(buffer.pieces->previous_piece_index, (uint32_t)(piece1 - buffer.pieces), "%u", "%u");

	struct piece piece_value = {
		.is_new = true,
		.selection = {
			.index = 6,
			.length = 4,
		},
	};
	struct piece *piece2 = buffer_insert_piece_before(&buffer, 0, &piece_value);
	assert_eq(piece2 - buffer.pieces, (size_t)2, "%zu", "%zu");
	assert_eq(piece2->previous_piece_index, 1, "%u", "%u");
	assert_eq(piece2->next_piece_index, 0, "%u", "%u");
	assert_eq(piece2->selection.index, piece_value.selection.index, "%u", "%u");
	assert_eq(piece2->selection.length, piece_value.selection.length, "%u", "%u");
	assert_eq(piece2->is_new, 1, "%u", "%u");
	assert_eq((void*)buffer.first_piece, (void*)piece1, "%p", "%p");
	assert_eq(buffer.pieces->previous_piece_index, (uint32_t)(piece2 - buffer.pieces), "%u", "%u");

	assert_eq(list_get_count(&buffer.pieces), (size_t)3, "%zu", "%zu");
	assert_eq(list_get_capacity(&buffer.pieces), (size_t)4, "%zu", "%zu");
	buffer_destroy(&buffer);
}

static void test_buffer_split_piece(void) {
	struct buffer buffer = {0};
	buffer_initialize(&buffer, 1, 1);
	buffer.pieces->selection = (struct selection){
		.index = 1,
		.length = 5,
	};
	struct piece *left = NULL;
	struct piece *right = NULL;
	assert(buffer_split_piece(&buffer, 0, 3, &left, &right));
	assert(left);
	assert(right);
	assert_eq(left->next_piece_index, 0, "%u", "%u");
	assert_eq(left->previous_piece_index, PIECE_NONE, "%u", "%u");
	assert_eq(right->previous_piece_index, 1, "%u", "%u");
	assert_eq(right->next_piece_index, PIECE_NONE, "%u", "%u");
	assert_eq(left->selection.index, 1, "%u", "%u");
	assert_eq(left->selection.length, 3, "%u", "%u");
	assert_eq(right->selection.index, 4, "%u", "%u");
	assert_eq(right->selection.length, 2, "%u", "%u");

	buffer_destroy(&buffer);
}

int main(void) {
	begin_testing();
		run_test(test_buffer_initialize_and_destroy);
		run_test(test_buffer_insert_piece_before);
		run_test(test_buffer_split_piece);
	return end_testing();
}
