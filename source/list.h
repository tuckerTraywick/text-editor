#ifndef LIST_H
#define LIST_H

#include <stddef.h>
#include <stdbool.h>

#define list_destroy(list) (list_destroy_impl((void**)(list)))

#define list_get_capacity(list) (list_get_capacity_impl((void**)(list)))

// Returns true if successful, false if memory error. If you pass a capacity smaller than the list's
// count, the count of the list shrinks to the new capacity.
#define list_set_capacity(list, capacity) (list_set_capacity_impl((void**)(list), (capacity)))

#define list_get_count(list) (list_get_count_impl((void**)(list)))

// Returns true if the new count was <= the list's capacity, returns false and does nothing
// otherwise.
#define list_set_count(list, count) (list_set_count_impl((void**)(list), (count)))

#define list_get_bucket_size(list) (list_get_bucket_size_impl((void**)(list)))

#define list_get_back(list) (list_get_back_impl((void**)(list)))

#define list_is_empty(list) (list_is_empty_impl((void**)(list)))

#define list_is_not_empty(list) (list_is_not_empty_impl((void**)(list)))

#define list_push_back(list, value) (list_push_back_impl((void**)(list), (value)))

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

bool list_is_not_empty_impl(void **list);

bool list_push_back_impl(void **list, void *value);

bool list_pop_back_impl(void **list, void *result);

#endif // LIST_H
