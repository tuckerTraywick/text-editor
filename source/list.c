#include <assert.h>
#include <stddef.h>
#include <stdlib.h>
#include "list.h"

struct List listCreate(size_t capacity, size_t elementSize) {
    assert(elementSize <= capacity);
    
    void *elements = malloc(capacity*elementSize);
    assert(elements && "`malloc()` failed.");
    return (struct List) {
        .capacity = capacity,
        .length = 0,
        .elementSize = elementSize,
        .elements = elements,
    };
}

void listDestroy(struct List *list);

void *listGet(struct List *list, size_t index);

void listSet(struct List *list, size_t index, void *element);

void listSwap(struct List *list, size_t indexA, size_t indexB);

void listInsert(struct List *list, size_t index, void *element);

void listAppend(struct List *list, void *element);

void listRemove(struct List *list, size_t index);
