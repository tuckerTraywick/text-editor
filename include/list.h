#ifndef LIST_H
#define LIST_H

#include <stddef.h>

struct List {
    size_t capacity;
    size_t length;
    size_t elementSize;
    void *elements;
};

struct List listCreate(size_t capacity, size_t elementSize);

void listDestroy(struct List *list);

void *listGet(struct List *list, size_t index);

void listSet(struct List *list, size_t index, void *element);

void listSwap(struct List *list, size_t indexA, size_t indexB);

void listInsert(struct List *list, size_t index, void *element);

void listAppend(struct List *list, void *element);

void listRemove(struct List *list, size_t index);

#endif // LIST_H
