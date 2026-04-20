#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include "list.h"

struct list_header {
	size_t buckets_capacity;
	size_t buckets_count;
	size_t bucket_size;
	char buckets[];
};

const size_t list_growth_factor = 2;

static struct list_header *get_header(void **list) {
	return (struct list_header*)*list - 1;
}

void *list_create(size_t capacity, size_t bucket_size) {
	struct list_header *header = malloc(sizeof *header + capacity*bucket_size);
	if (!header) {
		return NULL;
	}
	*header = (struct list_header){
		.buckets_capacity = capacity,
		.bucket_size = bucket_size,
	};
	return &header->buckets;
}

void list_destroy_impl(void **list) {
	struct list_header *header = get_header(list);
	free(header);
	*list = NULL;
}

size_t list_get_capacity_impl(void **list) {
	struct list_header *header = get_header(list);
	return header->buckets_capacity;
}

bool list_set_capacity_impl(void **list, size_t capacity) {
	struct list_header *header = get_header(list);
	if (capacity < header->buckets_count) {
		header->buckets_count = capacity;
	}
	header = realloc(header, sizeof *header + capacity*header->bucket_size);
	if (!header) {
		return false;
	}
	header->buckets_capacity = capacity;
	*list = &header->buckets;
	return true;
}

size_t list_get_count_impl(void **list) {
	struct list_header *header = get_header(list);
	return header->buckets_count;
}

bool list_set_count_impl(void **list, size_t count) {
	struct list_header *header = get_header(list);
	if (count > header->buckets_capacity) {
		return false;
	}
	header->buckets_count = count;
	return true;
}

size_t list_get_bucket_size_impl(void **list) {
	struct list_header *header = get_header(list);
	return header->bucket_size;
}

void *list_get_back_impl(void **list) {
	struct list_header *header = get_header(list);
	if (header->buckets_count == 0) {
		return NULL;
	}
	return (char*)*list + (header->buckets_count - 1)*header->bucket_size;
}

bool list_is_empty_impl(void **list) {
	struct list_header *header = get_header(list);
	return header->buckets_count == 0;
}

bool list_is_not_empty_impl(void **list) {
	struct list_header *header = get_header(list);
	return header->buckets_count != 0;
}

bool list_push_back_impl(void **list, void *value) {
	struct list_header *header = get_header(list);
	if (header->buckets_count == header->buckets_capacity && !list_set_capacity_impl(list, list_growth_factor*header->buckets_capacity)) {
		return false;
	}
	header = get_header(list);
	memcpy(header->buckets + header->buckets_count*header->bucket_size, value, header->bucket_size);
	++header->buckets_count;
	return true;
}

bool list_pop_back_impl(void **list, void *result) {
	struct list_header *header = get_header(list);
	if (header->buckets_count == 0) {
		return false;
	}
	memcpy(result, (char*)*list + (header->buckets_count - 1)*header->bucket_size, header->bucket_size);
	--header->buckets_count;
	return true;
}
