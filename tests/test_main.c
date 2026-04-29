#include <stddef.h>
#include <string.h>
#include <stdio.h>
#include "test.h"
#include "buffer.h"
#include "list.h"

struct buffer buffer;

void test_buffer_initialize(void) {
	assert(buffer_initialize(&buffer, 1, 1));
}

void test_buffer_destroy(void) {
	buffer_destroy(&buffer);
}

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

int main(void) {
	begin_testing();
		run_test(test_buffer_initialize);

		run_test(test_list_insert_uninitialized);
		run_test(test_list_insert);
		run_test(test_list_remove_range);

		run_test(test_buffer_destroy);
	return end_testing();
}
