#include <stddef.h>
#include <string.h>
#include <stdio.h>
#include "test.h"
#include "buffer.h"
#include "list.h"

void test_list_insert_uninitialized(void) {
	int *list = list_create(1, sizeof *list);
	assert(list);

	int *item = list_insert_uninitialized(&list, 0);
	assert(item);
	*item = 1;
	assert_eq(list[0], 1, "%d", "%d");
	assert_eq(list_get_count(&list), (size_t)1, "%zu", "%zu");
	assert_eq(list_get_capacity(&list), (size_t)1, "%zu", "%zu");

	item = list_insert_uninitialized(&list, 0);
	assert(item);
	*item = 2;
	assert_eq(list[0], 2, "%d", "%d");
	assert_eq(list[1], 1, "%d", "%d");
	assert_eq(list_get_count(&list), (size_t)2, "%zu", "%zu");
	assert_eq(list_get_capacity(&list), (size_t)2, "%zu", "%zu");

	item = list_insert_uninitialized(&list, 1);
	assert(item);
	*item = 3;
	assert_eq(list[0], 2, "%d", "%d");
	assert_eq(list[1], 3, "%d", "%d");
	assert_eq(list[2], 1, "%d", "%d");
	assert_eq(list_get_count(&list), (size_t)3, "%zu", "%zu");
	assert_eq(list_get_capacity(&list), (size_t)4, "%zu", "%zu");

	list_destroy(&list);
}

void test_list_insert(void) {
	int *list = list_create(1, sizeof *list);
	assert(list);

	int item = 1;
	assert_eq(list_insert(&list, 0, &item), (void*)list, "%p", "%p");
	assert_eq(list_get_count(&list), (size_t)1, "%zu", "%zu");
	assert_eq(list_get_capacity(&list), (size_t)1, "%zu", "%zu");
	assert_eq(list[0], 1, "%d", "%d");

	item = 2;
	assert_eq(list_insert(&list, 0, &item), (void*)list, "%p", "%p");
	assert_eq(list_get_count(&list), (size_t)2, "%zu", "%zu");
	assert_eq(list_get_capacity(&list), (size_t)2, "%zu", "%zu");
	assert_eq(list[0], 2, "%d", "%d");
	assert_eq(list[1], 1, "%d", "%d");

	item = 3;
	assert_eq(list_insert(&list, 1, &item), (void*)(list + 1), "%p", "%p");
	assert_eq(list_get_count(&list), (size_t)3, "%zu", "%zu");
	assert_eq(list_get_capacity(&list), (size_t)4, "%zu", "%zu");
	assert_eq(list[0], 2, "%d", "%d");
	assert_eq(list[1], 3, "%d", "%d");
	assert_eq(list[2], 1, "%d", "%d");
	
	list_destroy(&list);
}

void test_list_remove_range(void) {
	int *list = list_create(10, sizeof *list);
	assert(list);

	list_set_count(&list, 5);
	list[0] = 1;
	list[1] = 2;
	list[2] = 3;
	list[3] = 4;
	list[4] = 5;

	list_remove_range(&list, 1, 3);
	assert_eq(list[0], 1, "%d", "%d");
	assert_eq(list[1], 5, "%d", "%d");
	assert_eq(list_get_count(&list), (size_t)2, "%zu", "%zu");

	list_remove_range(&list, 0, 1);
	assert_eq(list[0], 5, "%d", "%d");
	assert_eq(list_get_count(&list), (size_t)1, "%zu", "%zu");

	list_destroy(&list);
}

void test_list_remove(void) {
	int *list = list_create(1, sizeof *list);
	assert(list);

	int element = 1;
	assert(list_push_back(&list, &element));
	element = 2;
	assert(list_push_back(&list, &element));
	element = 3;
	assert(list_push_back(&list, &element));
	assert_eq(list_get_count(&list), (size_t)3, "%zu", "%zu");
	
	list_remove(&list, 0);
	assert_eq(list_get_count(&list), (size_t)2, "%zu", "%zu");
	assert_eq(list[0], 2, "%d", "%d");

	list_remove(&list, 1);
	assert_eq(list_get_count(&list), (size_t)1, "%zu", "%zu");
	assert_eq(list[0], 2, "%d", "%d");

	list_destroy(&list);
}

void test_line_create_and_destroy(void) {
	struct line line = {0};
	assert(line_initialize(&line, 1));
	assert_eq(line.previous_index, BUFFER_NONE, "%d", "%d");
	assert_eq(line.next_index, BUFFER_NONE, "%d", "%d");
	assert_eq(list_get_capacity(&line.text), (size_t)1, "%zu", "%zu");
	assert_eq(list_get_count(&line.text), (size_t)0, "%zu", "%zu");
	line_destroy(&line);
}

void test_line_get_and_set_character(void) {
	struct line line = {0};
	assert(line_initialize(&line, 5));
	list_set_count(&line.text, 2);
	
	assert(line_set_character(&line, 0, 'a'));
	assert_eq(line_get_character(&line, 0), 'a', "%c", "%c");

	assert(line_set_character(&line, 1, 'b'));
	assert_eq(line_get_character(&line, 1), 'b', "%c", "%c");

	assert(!line_set_character(&line, 2, 'c'));
	assert_eq(line_get_character(&line, 2), '\0', "%c", "%c");

	line_destroy(&line);
}

void test_line_insert_character(void) {
	struct line line = {0};
	assert(line_initialize(&line, 1));

	assert(line_insert_character(&line, 0, 'a'));
	assert_eq(list_get_count(&line.text), (size_t)1, "%zu", "%zu");
	assert_eq(line_get_character(&line, 0), 'a', "%u", "%u");

	assert(line_insert_character(&line, 0, 'b'));
	assert_eq(list_get_count(&line.text), (size_t)2, "%zu", "%zu");
	assert_eq(line_get_character(&line, 0), 'b', "%c", "%c");
	assert_eq(line_get_character(&line, 1), 'a', "%c", "%c");

	assert(line_insert_character(&line, 1, 'c'));
	assert_eq(list_get_count(&line.text), (size_t)3, "%zu", "%zu");
	assert_eq(line_get_character(&line, 0), 'b', "%c", "%c");
	assert_eq(line_get_character(&line, 1), 'c', "%c", "%c");
	assert_eq(line_get_character(&line, 2), 'a', "%c", "%c");

	line_destroy(&line);
}

void test_line_delete_character(void) {
	struct line line = {0};
	assert(line_initialize(&line, 1));

	assert(line_insert_character(&line, 0, 'a'));
	assert_eq(list_get_count(&line.text), (size_t)1, "%zu", "%zu");
	assert(line_insert_character(&line, 1, 'b'));
	assert_eq(list_get_count(&line.text), (size_t)2, "%zu", "%zu");
	assert(line_insert_character(&line, 2, 'c'));
	assert_eq(list_get_count(&line.text), (size_t)3, "%zu", "%zu");

	assert_eq(line.text[0], 'a', "%c", "%c");
	assert_eq(line.text[1], 'b', "%c", "%c");
	assert_eq(line.text[2], 'c', "%c", "%c");

	assert(line_delete_character(&line, 0));
	assert_eq(list_get_count(&line.text), (size_t)2, "%zu", "%zu");
	assert_eq(line.text[0], 'b', "%c", "%c");

	assert(line_delete_character(&line, 1));
	assert_eq(list_get_count(&line.text), (size_t)1, "%zu", "%zu");
	assert_eq(line.text[0], 'b', "%c", "%c");
	
	assert(line_delete_character(&line, 0));
	assert_eq(list_get_count(&line.text), (size_t)0, "%zu", "%zu");	

	line_destroy(&line);
}

void test_line_delete_range(void) {
	struct line line = {0};
	assert(line_initialize(&line, 1));

	assert(line_insert_character(&line, 0, 'a'));
	assert(line_insert_character(&line, 1, 'b'));
	assert(line_insert_character(&line, 2, 'c'));
	assert(line_insert_character(&line, 3, 'd'));

	assert(line_delete_range(&line, 1, 2));
	assert_eq(list_get_count(&line.text), (size_t)2, "%zu", "%zu");
	assert_eq(line.text[0], 'a', "%c", "%c");
	assert_eq(line.text[1], 'd', "%c", "%c");

	assert(line_delete_range(&line, 0, 1));
	assert_eq(list_get_count(&line.text), (size_t)1, "%zu", "%zu");
	assert_eq(line.text[0], 'd', "%c", "%c");

	line_destroy(&line);
}

void test_buffer_initialize_and_destroy(void) {
	struct buffer buffer = {0};
	assert(buffer_initialize(&buffer, 1, 1));
	buffer_destroy(&buffer);
}

void test_buffer_view_initialize_and_destroy(void) {
	struct buffer buffer = {0};
	struct buffer_view view = {0};
	assert(buffer_view_initialize(&view, &buffer));
	buffer_view_destroy(&view);
}

void test_buffer_view_insert_character(void) {
	struct buffer buffer = {0};
	assert(buffer_initialize(&buffer, 1, 1));
	struct buffer_view view = {0};
	assert(buffer_view_initialize(&view, &buffer));

	assert(buffer_view_insert_character(&view, 'a'));
	struct line *line = buffer.lines + buffer.first_line_index;
	assert_eq(list_get_count(&line->text), (size_t)1, "%zu", "%zu");
	assert_eq(line->text[0], 'a', "%c", "%c");


	buffer_destroy(&buffer);
	buffer_view_destroy(&view);
}

int main(void) {
	begin_testing();
		run_test(test_list_insert_uninitialized);
		run_test(test_list_insert);
		run_test(test_list_remove_range);
		run_test(test_list_remove);

		run_test(test_line_create_and_destroy);
		run_test(test_line_get_and_set_character);
		run_test(test_line_insert_character);
		run_test(test_line_delete_character);
		run_test(test_line_delete_range);

		run_test(test_buffer_initialize_and_destroy);
		
		run_test(test_buffer_view_initialize_and_destroy);
		run_test(test_buffer_view_insert_character);
	return end_testing();
}
