#include <assert.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include "list.h"

static void listRealloc(struct List *list) {
    if (list->length == list->capacity) {
        list->capacity *= 2;
    } else if (list->length <= list->capacity/2) {
        // Leave half of the gap between the length and the current capacity for future expansion.
        list->capacity -= (list->capacity - list->length)/2;
    }
    void *newElements = realloc(list->elements, list->elementSize*list->capacity);
    // TODO: Handle failed `realloc()`.
    assert(newElements && "`realloc()` failed.");
    list->elements = newElements;
}

struct List listCreate(size_t capacity, size_t elementSize) {
    assert(elementSize <= capacity);
    
    void *elements = malloc(elementSize*capacity);
    // TODO: Handle failed `malloc()`.
    assert(elements && "`malloc()` failed.");
    return (struct List){
        .capacity = capacity,
        .length = 0,
        .elementSize = elementSize,
        .elements = elements,
    };
}

void listDestroy(struct List *list) {
    assert(list);

    free(list->elements);
    *list = (struct List){0};
}

void *listGet(struct List *list, size_t index) {
    assert(list);
    assert(index < list->length && "Index out of bounds.");

    return (char*)list->elements + list->elementSize*index;
}

void listSet(struct List *list, size_t index, void *element) {
    assert(list);
    assert(element);
    assert(index < list->length && "Index out of bounds.");

    memcpy((char*)list->elements + list->elementSize*index, element, list->elementSize);
}

void listSwap(struct List *list, size_t indexA, size_t indexB) {
    assert(list);
    assert(indexA < list->length && "`indexA` out of bounds.");
    assert(indexB < list->length && "`indexB` out of bounds.");

    // *temp = *list[indexA]; *list[indexA] = *list[indexB]; *list[indexB] = *temp;
    void *temp = malloc(list->elementSize);
    // TODO: Handle failed `malloc()`.
    assert(temp && "`malloc()` failed.");
    memcpy(temp, listGet(list, indexA), list->elementSize);
    memcpy(listGet(list, indexA), listGet(list, indexB), list->elementSize);
    memcpy(listGet(list, indexB), temp, list->elementSize);
}

void listInsert(struct List *list, size_t index, void *element) {
    assert(list);
    assert(element);
    assert(index <= list->length && "Index out of bounds.");
    assert(list->length <= list->capacity && "Length incremented too much.");

    listRealloc(list);
    memmove(
        (char*)list->elements + list->elementSize*(index + 1),
        (char*)list->elements + list->elementSize*index,
        list->elementSize*(list->length - index)
    );
    memcpy((char*)list->elements + list->elementSize*index, element, list->elementSize);
    ++list->length;
}

void listAppend(struct List *list, void *element) {
    assert(list);
    assert(element);

    listRealloc(list);
    memcpy((char*)list->elements + list->elementSize*list->length, element, list->elementSize);
    ++list->length;
}

void listRemove(struct List *list, size_t index) {
    assert(list);
    assert(index < list->length && "Index out of bounds.");

    memmove(
        (char*)list->elements + list->elementSize*index,
        (char*)list->elements + list->elementSize*(index + 1),
        list->elementSize*(list->length - index)
    );
    --list->length;
    listRealloc(list);
}
