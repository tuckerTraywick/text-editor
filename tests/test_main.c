#include <stddef.h>
#include <string.h>
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
	assert_eq((void*)buffer.last_free_piece, NULL, "%p", "%p");
	assert_eq((void*)buffer.first_piece, NULL, "%p", "%p");
}

static void test_buffer_insert_piece_before(void) {
	struct buffer buffer = {0};
	buffer_initialize(&buffer, 1, 1);

	struct piece *piece1 = buffer_insert_piece_before(&buffer, 0, NULL);
	assert_eq(piece1 - buffer.pieces, (size_t)1, "%zu", "%zu");
	assert_eq(piece1->previous_piece_index, PIECE_NONE, "%u", "%u");
	assert_eq(piece1->next_piece_index, 0, "%u", "%u");
	assert_eq(piece1->text.index, 0, "%u", "%u");
	assert_eq(piece1->text.length, 0, "%u", "%u");
	assert_eq(piece1->is_new, 0, "%u", "%u");
	assert_eq((void*)buffer.first_piece, (void*)piece1, "%p", "%p");
	assert_eq(buffer.pieces->previous_piece_index, (uint32_t)(piece1 - buffer.pieces), "%u", "%u");

	struct piece piece_value = {
		.is_new = true,
		.text = {
			.index = 6,
			.length = 4,
		},
	};
	struct piece *piece2 = buffer_insert_piece_before(&buffer, 0, &piece_value);
	assert_eq(piece2 - buffer.pieces, (size_t)2, "%zu", "%zu");
	assert_eq(piece2->previous_piece_index, 1, "%u", "%u");
	assert_eq(piece2->next_piece_index, 0, "%u", "%u");
	assert_eq(piece2->text.index, piece_value.text.index, "%u", "%u");
	assert_eq(piece2->text.length, piece_value.text.length, "%u", "%u");
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
	buffer.pieces->text = (struct span){
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
	assert_eq(left->text.index, 1, "%u", "%u");
	assert_eq(left->text.length, 3, "%u", "%u");
	assert_eq(right->text.index, 4, "%u", "%u");
	assert_eq(right->text.length, 2, "%u", "%u");

	buffer_destroy(&buffer);
}

static void test_buffer_delete_piece(void) {
	char text[] = "hello world goodbye";
	struct buffer buffer = {0};
	// We are deliberately ignoring the null terminator here.
	buffer_initialize(&buffer, sizeof text, 1);
	list_set_count(&buffer.new_text, sizeof text);
	strcpy((char*)buffer.new_text, text);
	struct piece piece = {
		.is_new = true,
		.text = {
			.index = 4,
			.length = 5,
		},
	};

	assert(buffer_insert_piece_before(&buffer, 0, &piece));
	buffer_delete_piece(&buffer, 0);
	assert_eq(buffer.first_piece - buffer.pieces, (size_t)1, "%zu", "%zu");
	assert_eq(buffer.pieces[1].previous_piece_index, PIECE_NONE, "%u", "%u");
	assert_eq(buffer.pieces[1].next_piece_index, PIECE_NONE, "%u", "%u");
	assert_eq(buffer.pieces[1].text.index, piece.text.index, "%u", "%u");
	assert_eq(buffer.pieces[1].text.length, piece.text.length, "%u", "%u");
	assert_eq(buffer.last_free_piece - buffer.pieces, (size_t)0, "%zu", "%zu");
	assert_eq(buffer.pieces[0].previous_piece_index, PIECE_NONE, "%u", "%u");
	assert_eq(buffer.pieces[0].next_piece_index, PIECE_NONE, "%u", "%u");
	assert_eq(buffer.pieces[0].text.index, 0, "%u", "%u");
	assert_eq(buffer.pieces[0].text.length, 0, "%u", "%u");
	
	// assert(buffer_insert_piece_before(&buffer, 0, &piece));
	// assert(buffer_insert_piece_before(&buffer, 0, &piece));

	buffer_print_pieces(&buffer);
	printf("\n");
	// buffer_print_free_pieces(&buffer);

	buffer_destroy(&buffer);
}

static void test_buffer_insert_character(void) {
	struct buffer buffer = {0};
	buffer_initialize(&buffer, 1, 1);
	assert(buffer_insert_character(&buffer, 0, 'a'));
	assert_eq(buffer_get_character(&buffer, 0), 'a', "%c", "%c");
	buffer_print_pieces(&buffer);
	
	buffer_destroy(&buffer);
}

int main(void) {
	begin_testing();
		run_test(test_buffer_initialize_and_destroy);
		run_test(test_buffer_insert_piece_before);
		run_test(test_buffer_split_piece);
		run_test(test_buffer_delete_piece);
		// run_test(test_buffer_insert_character);
	return end_testing();
}
