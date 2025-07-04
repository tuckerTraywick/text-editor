#ifndef LIST_H
#define LIST_H

#include <stddef.h>
#include <stdbool.h>

// Returns a pointer to the last element of a list. Returns null if the list is empty.
#define list_get_last(list) ((list_get_size(list)) ? list + list_get_size(list) - 1 : NULL)

void *list_create(size_t capacity, size_t element_size);

void list_destroy(void *list);

// Returns the maximum capacity of a list.
size_t list_get_capacity(void *list);

// Sets the maximum capacity of a list. Returns a pointer to the list. May reallocate the list.
void *list_set_capacity(void *list, size_t capacity);

// Returns the number of elements in the list.
size_t list_get_size(void *list);

// Sets the number of elements used in a list. DOES NOT ZERO ELEMENTS. Returns a pointer to the
// list. May reallocate the list.
void *list_set_size(void *list, size_t size);

// Returns the size of each element in a list.
size_t list_get_element_size(void *list);

// Pushes an element on the end of a list. Returns the list. May reallocate the list.
void *list_push(void *list, void *element);

// Pops an element off the end of a list. Returns the list. May reallocate the list.
void *list_pop(void *list, void *destination);

#endif // LIST_H
