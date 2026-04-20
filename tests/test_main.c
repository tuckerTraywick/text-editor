#include <stddef.h>
#include <stdio.h>
#include "test.h"
#include "editor.h"

static struct buffer buffer;

static void setup(void) {
	buffer_initialize(&buffer, 1, 1);
}

static void teardown(void) {
	buffer_destroy(&buffer);
}

static void test_buffer_insert_piece_before(void) {
	struct piece *previous_first_piece = buffer.first_piece;
	struct piece *piece1 = buffer_insert_piece_before(&buffer, buffer.first_piece, NULL);
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
	struct piece *piece2 = buffer_insert_piece_before(&buffer, previous_first_piece, &piece_value);
	assert_eq(piece2 - buffer.pieces, (size_t)2, "%zu", "%zu");
	assert_eq(piece2->previous_piece_index, (uint32_t)(piece1 - buffer.pieces), "%u", "%u");
	assert_eq(piece2->next_piece_index, 0, "%u", "%u");
	assert_eq(piece2->selection.index, piece_value.selection.index, "%u", "%u");
	assert_eq(piece2->selection.length, piece_value.selection.length, "%u", "%u");
	assert_eq(piece2->is_new, 1, "%u", "%u");
	assert_eq((void*)buffer.first_piece, (void*)piece1, "%p", "%p");
	assert_eq(buffer.pieces->previous_piece_index, (uint32_t)(piece2 - buffer.pieces), "%u", "%u");
}

static void test_buffer_get_piece_and_offset(void);

int main(void) {
	setup();
	begin_testing();
		run_test(test_buffer_insert_piece_before);
	teardown();
	return end_testing();
}
