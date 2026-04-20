#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <ncurses.h>
#include "editor.h"
#include "list.h"

struct mark {
	uint32_t x, y; // Column, row.
};

struct selection {
	struct mark start, end;
};

struct piece {
	uint32_t previous; // The index of the previous piece in the chain.
	uint32_t next; // The index of the next piece in the chain.
	struct selection text; // Refers to the actual contents of a buffer.
	struct selection rendered_text; // Refers to the rendered text as it appears on the screen.
	bool is_original;
};

// A piece of text to be edited. Represented as a piece table.
struct buffer {
	FILE *file;
	char *original_text; // Points to the `mmap()`ed contents of `file` if it is not null, or `malloc()`ed buffer if it is.
	char *new_text; // Points to a list.
	char *rendered_text; // Points to a list.
	struct piece *pieces; // Points to a list.
	struct piece *free_pieces; // A linked list of pieces that have been deleted. Not a list. Don't free.
};

struct buffer_view {
	struct buffer buffer; // The text being viewed.
	struct selection *selections; // Points to a list.
	uint32_t current_selection_index;
	struct selection *matches; // Points to a list. The matches for the find term in the buffer being viewed.
	uint32_t current_match_index;
	struct buffer find_buffer; // Holds the text of the find field.
	struct selection find_buffer_selection;
	struct buffer replace_buffer; // Holds the text of the replace field.
	struct buffer replace_buffer_selection;
};

// Returns a mark pointing to the beginning of the selection.
// struct mark selection_get_start(struct selection *selection);

// Returns a mark pointing to the end (inclusive) of the selection.
// struct mark selection_get_end(struct selection *selection);

bool buffer_initialize(struct buffer *buffer, uint32_t text_capacity, uint32_t piece_capacity) {
	*buffer = (struct buffer){0};
	buffer->original_text = list_create(text_capacity, sizeof *buffer->original_text);
	if (!buffer->original_text) {
		goto error1;
	}
	buffer->new_text = list_create(text_capacity, sizeof *buffer->new_text);
	if (!buffer->new_text) {
		goto error2;
	}
	buffer->rendered_text = list_create(text_capacity, sizeof *buffer->rendered_text);
	if (!buffer->rendered_text) {
		goto error3;
	}
	buffer->pieces = list_create(piece_capacity, sizeof *buffer->pieces);
	if (!buffer->pieces) {
		goto error4;
	}
	return true;

error4:
	list_destroy(&buffer->rendered_text);
error3:
	list_destroy(&buffer->new_text);
error2:
	list_destroy(&buffer->original_text);
error1:
	*buffer = (struct buffer){0};
	return false;
}

bool buffer_open_file(struct buffer *buffer, FILE *file);

void buffer_destroy(struct buffer *buffer) {
	list_destroy(&buffer->original_text);
	list_destroy(&buffer->new_text);
	list_destroy(&buffer->rendered_text);
	list_destroy(&buffer->pieces);
	*buffer = (struct buffer){0};
}

void buffer_save(struct buffer *buffer);

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
		printf("Error initializing buffer.\n");
		return 1;
	}

	setup_ncurses();
	teardown_ncurses();

	buffer_destroy(&buffer);
	return 0;
}
