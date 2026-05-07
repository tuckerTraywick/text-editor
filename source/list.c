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

static struct list_header *list_get_header(void **list) {
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
	struct list_header *header = list_get_header(list);
	free(header);
	*list = NULL;
}

size_t list_get_capacity_impl(void **list) {
	struct list_header *header = list_get_header(list);
	return header->buckets_capacity;
}

bool list_set_capacity_impl(void **list, size_t capacity) {
	struct list_header *header = list_get_header(list);
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
	struct list_header *header = list_get_header(list);
	return header->buckets_count;
}

bool list_set_count_impl(void **list, size_t count) {
	struct list_header *header = list_get_header(list);
	if (count > header->buckets_capacity) {
		return false;
	}
	header->buckets_count = count;
	return true;
}

size_t list_get_bucket_size_impl(void **list) {
	struct list_header *header = list_get_header(list);
	return header->bucket_size;
}

void *list_get_back_impl(void **list) {
	struct list_header *header = list_get_header(list);
	if (header->buckets_count == 0) {
		return NULL;
	}
	return (char*)*list + (header->buckets_count - 1)*header->bucket_size;
}

bool list_is_empty_impl(void **list) {
	struct list_header *header = list_get_header(list);
	return header->buckets_count == 0;
}

void *list_insert_uninitialized_impl(void **list, size_t index) {
	struct list_header *header = list_get_header(list);
	// Expand the list if needed.
	if (header->buckets_count == header->buckets_capacity && !list_set_capacity_impl(list, list_growth_factor*header->buckets_capacity)) {
		return NULL;
	}
	header = list_get_header(list);

	// Move the elements after `index` one to the right if needed.
	if (index < header->buckets_count) {
		memmove(header->buckets + (index + 1)*header->bucket_size, header->buckets + index*header->bucket_size, (header->buckets_count - index)*header->bucket_size);
	}
	++header->buckets_count;
	return header->buckets + index*header->bucket_size;
}

void *list_insert_impl(void **list, size_t index, void *value) {
	void *new_value = list_insert_uninitialized_impl(list, index);
	if (!new_value) {
		return NULL;
	}
	struct list_header *header = list_get_header(list);
	memcpy(new_value, value, header->bucket_size);
	return new_value;
}

bool list_remove_range_impl(void **list, size_t start_index, size_t count) {
	struct list_header *header = list_get_header(list);
	if (start_index > header->buckets_count || start_index + count > header->buckets_count) {
		return false;
	}
	if (count == 0) {
		return true;
	}
	if (header->buckets_count == 0) {
		return false;
	}

	if (start_index + count < header->buckets_count) {
		memmove(header->buckets + start_index*header->bucket_size, header->buckets + (start_index + count)*header->bucket_size, (header->buckets_count - start_index - count)*header->bucket_size);
	}
	header->buckets_count -= count;
	return true;
}

bool list_remove_impl(void **list, size_t index) {
	return list_remove_range_impl(list, index, 1);
}

void *list_push_back_uninitialized_impl(void **list) {
	return list_insert_uninitialized_impl(list, list_get_count(list));
}

void *list_push_back_impl(void **list, void *value) {
	return list_insert_impl(list, list_get_count(list), value);
}

bool list_pop_back_impl(void **list, void *result) {
	struct list_header *header = list_get_header(list);
	if (header->buckets_count == 0) {
		return false;
	}
	memcpy(result, (char*)*list + (header->buckets_count - 1)*header->bucket_size, header->bucket_size);
	--header->buckets_count;
	return true;
}
