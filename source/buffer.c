#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include "buffer.h"
#include "list.h"

static const size_t initial_file_path_capacity = 4*1024;

bool buffer_initialize(struct buffer *buffer, uint32_t lines_capacity, uint32_t line_character_capaity) {
	buffer->file_path = list_create(initial_file_path_capacity, sizeof *buffer->file_path);
	if (!buffer->file_path) {
		goto error1;
	}
	buffer->lines = list_create(lines_capacity, sizeof *buffer->lines);
	if (!buffer->lines) {
		goto error2;
	}
	if (!line_initialize(buffer->lines, line_character_capaity)) {
		goto error3;
	}
	buffer->first_line_index = 0;
	buffer->last_line_index = 0;
	buffer->last_free_line_index = BUFFER_NONE;
	return true;

error3:
	list_destroy(&buffer->lines);
error2:
	list_destroy(&buffer->file_path);
error1:
	*buffer = (struct buffer){0};
	return false;
}

void buffer_destroy(struct buffer *buffer) {
	for (size_t i = 0; i < list_get_count(&buffer); ++i) {
		line_destroy(buffer->lines + i);
	}
	list_destroy(&buffer->lines);
	list_destroy(&buffer->file_path);
	*buffer = (struct buffer){0};
}

bool line_initialize(struct line *line, uint32_t capacity) {
	line->text = list_create(capacity, sizeof *line->text);
	if (!line->text) {
		*line = (struct line){0};
		return false;
	}
	line->previous_index = BUFFER_NONE;
	line->next_index = BUFFER_NONE;
	return true;
}

void line_destroy(struct line *line) {
	list_destroy(&line->text);
	*line = (struct line){0};
}
