#ifndef LIST_H
#define LIST_H

#include <stddef.h>

// Represents a dynamic array that can grow and shrink at runtime.
struct List {
    size_t capacity; // The number of elements allocated.
    size_t length; // The current number of elements.
    size_t elementSize; // The size in bytes of one element.
    void *elements; // The buffer containing the elements.
};

// Returns a new list. The list must be destroy by `listDestroy()`.
struct List listCreate(size_t capacity, size_t elementSize);

// Deallocates a list's elements and zeroes its memory.
void listDestroy(struct List *list);

// Returns a pointer to the element at `index`.
void *listGet(struct List *list, size_t index);

// Copies `element` to the element at `index`.
void listSet(struct List *list, size_t index, void *element);

// Swaps the elements at `indexA` and `indexB`.
void listSwap(struct List *list, size_t indexA, size_t indexB);

// Inserts `element` at `index`.
void listInsert(struct List *list, size_t index, void *element);

// Appends `element` to the end of the list.
void listAppend(struct List *list, void *element);

// Removes the element at `index`. Be sure to destroy the element if needed before calling this
// method.
void listRemove(struct List *list, size_t index);

#endif // LIST_H
