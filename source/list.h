#ifndef LIST_H
#define LIST_H

#include <stddef.h>
#include <stdbool.h>

#define list_destroy(list) (list_destroy_impl((void**)(list)))

#define list_get_capacity(list) (list_get_capacity_impl((void**)(list)))

// If `capacity` is less than `list`'s count, shrinks `list`'s count to match the new capacity.
// Returns true if no memory errors occurred.
#define list_set_capacity(list, capacity) (list_set_capacity_impl((void**)(list), (capacity)))

#define list_get_count(list) (list_get_count_impl((void**)(list)))

// Returns true if `count` is less than or equal to `list`'s capacity and no memory errors occurred,
// returns false and does nothing otherwise.
#define list_set_count(list, count) (list_set_count_impl((void**)(list), (count)))

#define list_get_bucket_size(list) (list_get_bucket_size_impl((void**)(list)))

// Returns null if `list` is empty.
#define list_get_back(list) (list_get_back_impl((void**)(list)))

#define list_is_empty(list) (list_is_empty_impl((void**)(list)))

// Assumes `index` is less than or equal to `list`'s count. Returns a pointer to the new element
// if no memory errors occurred, null otherwise.
#define list_insert_uninitialized(list, index) (list_insert_uninitialized_impl((void**)(list), (index)))

// Assumes `index` is less than or equal to `list`'s count. Returns a pointer to the new element
// if no memory errors occurred, null otherwise.
#define list_insert(list, index, value) (list_insert_impl((void**)(list), (index), (value)))

// Returns true and deletes the elements in the given range if `start_index` and
// `start_index + count` are both less than or equal to `list`'s count. Returns false and does
// nothing otherwise.
#define list_remove_range(list, start_index, count) (list_remove_range_impl((void**)(list), (start_index), (count)))

// Returns true and deletes the element at `index` if `index` is less than `list`'s count, returns
// false and does nothing otherwise.
#define list_remove(list, index) (list_remove_impl((void**)list, (index)))

// Returns a pointer to the new element if no memory errors occurred, null otherwise.
#define list_push_back_uninitialized(list) (list_push_back_uninitialized_impl((void**)(list)))

// Returns a pointer to the new element if no memory errors occurred, null otherwise.
#define list_push_back(list, value) (list_push_back_impl((void**)(list), (value)))

// Returns true and pops the end of `list` if it had an element to pop, false otherwise.
#define list_pop_back(list, result) (list_pop_back_impl((void**)(list), (result)))

extern const size_t list_growth_factor;

void *list_create(size_t capacity, size_t bucket_size);

void list_destroy_impl(void **list);

size_t list_get_capacity_impl(void **list);

bool list_set_capacity_impl(void **list, size_t capacity);

size_t list_get_count_impl(void **list);

bool list_set_count_impl(void **list, size_t count);

size_t list_get_bucket_size_impl(void **list);

void *list_get_back_impl(void **list);

bool list_is_empty_impl(void **list);

void *list_insert_uninitialized_impl(void **list, size_t index);

void *list_insert_impl(void **list, size_t index, void *value);

bool list_remove_range_impl(void **list, size_t start_index, size_t count);

bool list_remove_impl(void **list, size_t index);

void *list_push_back_uninitialized_impl(void **list);

void *list_push_back_impl(void **list, void *value);

bool list_pop_back_impl(void **list, void *result);

#endif // LIST_H
