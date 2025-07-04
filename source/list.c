#include <assert.h>
#include <stdio.h>

#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include "list.h"

#define min(a, b) (((a) <= (b)) ? (a) : (b))

#define max(a, b) (((a) >= (b)) ? (a) : (b))

typedef struct List_Header {
	size_t capacity;
	size_t size;
	size_t element_size;
	size_t pad;
	char data[];
} List_Header;

static List_Header *list_get_header(void *list) {
	return (List_Header*)list - 1;
}

void *list_create(size_t capacity, size_t element_size) {
	List_Header *list = malloc(sizeof (List_Header) + capacity*element_size);
	if (!list) {
		return NULL;
	}
	*list = (List_Header){
		.capacity = capacity,
		.element_size = element_size,
	};
	return list + 1;
}

void list_destroy(void *list) {
	free((List_Header*)list - 1);
}

size_t list_get_capacity(void *list) {
	List_Header *header = list_get_header(list);
	return header->capacity;
}

void *list_set_capacity(void *list, size_t capacity) {
	List_Header *new_list = realloc(list_get_header(list), sizeof (List_Header) + capacity*list_get_element_size(list));
	if (!new_list) {
		return NULL;
	}
	new_list->capacity = capacity;
	return new_list + 1;
}

size_t list_get_size(void *list) {
	List_Header *header = list_get_header(list);
	return header->size;
}

void *list_set_size(void *list, size_t size) {
	if (size >= list_get_capacity(list)) {
		list = list_set_capacity(list, max(list_get_capacity(list)*2, size));
		if (!list) {
			return NULL;
		}
	}
	List_Header *header = list_get_header(list);
	header->size = size;
	return list;
}

size_t list_get_element_size(void *list) {
	List_Header *header = list_get_header(list);
	return header->element_size;
}

void *list_push(void *list, void *element) {
	list = list_set_size(list, list_get_size(list) + 1);
	if (list) {
		memcpy((char*)list + (list_get_size(list) - 1)*list_get_element_size(list), element, list_get_element_size(list));
	}
	return list;
}

void *list_pop(void *list, void *destination) {
	list = list_set_size(list, list_get_size(list) - 1);
	if (list) {
		memcpy(destination, (char*)list + (list_get_size(list) + 1)*list_get_element_size(list), list_get_element_size(list));
	}
	return list;
}

#undef min
#undef max
