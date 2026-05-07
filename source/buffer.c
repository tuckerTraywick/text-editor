#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "buffer.h"
#include "list.h"

static const size_t initial_file_path_capacity = 3*1024;

bool buffer_initialize(struct buffer *buffer, uint32_t lines_capacity, uint32_t line_character_capaity) {
	buffer->file_path = list_create(initial_file_path_capacity, sizeof *buffer->file_path);
	if (!buffer->file_path) {
		goto error1;
	}
	buffer->lines = list_create(lines_capacity, sizeof *buffer->lines);
	if (!buffer->lines) {
		goto error2;
	}
	if (!list_push_back_uninitialized(&buffer->lines) || !line_initialize(buffer->lines, line_character_capaity)) {
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
	for (size_t i = 0; i < list_get_count(&buffer->lines); ++i) {
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

char8 line_get_character(struct line *line, uint32_t index) {
	if (index < list_get_count(&line->text)) {
		return line->text[index];
	}
	return '\0';
}

bool line_set_character(struct line *line, uint32_t index, char8 character) {
	if (index < list_get_count(&line->text)) {
		line->text[index] = character;
		return true;
	}
	return false;
}

bool line_insert_character(struct line *line, uint32_t index, char8 character) {
	if (index > list_get_count(&line->text)) {
		return false;
	}
	return list_insert(&line->text, (size_t)index, &character);
}

bool line_delete_range(struct line *line, uint32_t start_index, uint32_t count) {
	return list_remove_range(&line->text, start_index, count);
}

bool line_delete_character(struct line *line, uint32_t index) {
	return list_remove(&line->text, index);
}
