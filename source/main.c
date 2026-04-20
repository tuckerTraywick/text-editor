#include <stdint.h>
#include <stdio.h>
#include "editor.h"

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
	// buffer_print_piece(&buffer, old_piece);
	// printf("offset = %u\n", offset);

	struct piece new_piece = {
		.is_new = true,
		.selection = {
			.index = 3,
			.length = 5,
		},
	};
	struct piece *new_piece_ptr = buffer_insert_piece_before(&buffer, old_piece, &new_piece);


	new_piece = (struct piece){
		.is_new = false,
		.selection = {
			.index = 7,
			.length = 9,
		},
	};
	buffer_insert_piece_before(&buffer, old_piece, &new_piece);


	buffer_print_pieces(&buffer);

	setup_ncurses();
	teardown_ncurses();

	buffer_destroy(&buffer);
	return 0;
}
