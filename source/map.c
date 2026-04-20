#include <stdio.h>

#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include "map.h"

#define max(a, b) (((a) >= (b)) ? (a) : (b))

struct map_header {
	size_t keys_capacity;
	size_t keys_size;
	char *keys;
	size_t buckets_capacity;
	size_t buckets_count;
	size_t bucket_size;
	size_t *key_indices; // Same capacity as `buckets`.
	char buckets[];
};

// Returned by `probe` to indicate the status of a key in a map.
enum probe_result {
	PROBE_RESULT_KEY_FOUND,
	PROBE_RESULT_MAP_NOT_FULL,
	PROBE_RESULT_MAP_FULL,
};

static const size_t initial_keys_capacity = 1024;

const size_t buckets_growth_factor = 2;

const size_t keys_growth_factor = 2;

static struct map_header *get_header(void **map) {
	return (struct map_header*)*map - 1;
}

// FNV-1a hash, copied from Wikipedia:
// https://en.wikipedia.org/wiki/Fowler%E2%80%93Noll%E2%80%93Vo_hash_function
static size_t hash(char *key) {
	size_t hash = 14695981039346656037ull;
	size_t prime = 1099511628211ull;
	while (*key) {
		hash = (hash^*key)*prime;
		++key;
	}
	return hash;
}

// Finds the corresponding bucket for `key` in `map` and places its index in `bucket_index`. Returns a
// status indicating whether the key was found, the key was not found and the map has an empty
// bucket, or the key was not found and the map is full.
static enum probe_result probe(void **map, char *key, size_t *bucket_index) {
	struct map_header *header = get_header(map);
	size_t start_index = hash(key)%header->buckets_capacity;
	size_t index = start_index;
	size_t next_empty_index = 0;

	// Look for a matching key or an empty bucket.
	do {
		if (header->key_indices[index] == 0) {
			if (next_empty_index == 0) {
				next_empty_index = index;
			}
		// If the bucket is full and the key matches, we found the bucket.
		} else if (strcmp(key, header->keys + header->key_indices[index] - 1) == 0) { // Subtracting 1 because key indices are offset by +1.
			*bucket_index = index;
			return PROBE_RESULT_KEY_FOUND;
		}
		// Linear probing.
		index = (index + 1)%header->buckets_capacity;
	} while (index != start_index);

	if (header->buckets_count < header->buckets_capacity) {
		*bucket_index = next_empty_index;
		return PROBE_RESULT_MAP_NOT_FULL;
	}
	*bucket_index = SIZE_MAX;
	return PROBE_RESULT_MAP_FULL;
}

// Returns the index of the key in the string pool if successful, 0 otherwise.
static size_t add_key(void **map, char *key) {
	struct map_header *header = get_header(map);
	size_t length = strlen(key) + 1; // Adding 1 to account for null terminator.
	if (header->keys_size + length > header->keys_capacity) {
		// Reallocate the keys if the given key is too big to fit.
		size_t new_capacity = max(header->keys_size + length, keys_growth_factor*header->keys_capacity);
		if (!map_set_keys_capacity(map, new_capacity)) {
			return 0;
		}
		header = get_header(map);
	}
	strcpy(header->keys + header->keys_size, key);
	size_t previous_size = header->keys_size;
	header->keys_size += length;
	return previous_size + 1; // Adding 1 because 0 is a sentinal value meaning an empty bucket.
}

void *map_create(size_t buckets_capacity, size_t bucket_size, size_t keys_capacity) {
	struct map_header *header = malloc(sizeof *header + buckets_capacity*bucket_size);
	if (!header) {
		return NULL;
	}
	*header = (struct map_header){
		.keys_capacity = keys_capacity,
		.keys = malloc(keys_capacity),
		.buckets_capacity = buckets_capacity,
		.bucket_size = bucket_size,
	};
	if (!header->keys) {
		free(header);
		return NULL;
	}
	header->key_indices = calloc(buckets_capacity, sizeof *header->key_indices);
	if (!header->key_indices) {
		free(header->keys);
		free(header->key_indices);
		return NULL;
	}
	return &header->buckets;
}

void map_destroy_impl(void **map) {
	struct map_header *header = get_header(map);
	free(header->keys);
	free(header->key_indices);
	free(header);
	*map = NULL;
}

size_t map_get_buckets_capacity_impl(void **map) {
	struct map_header *header = get_header(map);
	return header->buckets_capacity;
}

bool map_set_buckets_capacity_impl(void **map, size_t capacity) {
	struct map_header *header = get_header(map);
	if (capacity < header->buckets_count) {
		return false;
	}
	if (capacity == header->buckets_capacity) {
		return true;
	}
	
	void *new_map = map_create(capacity, header->bucket_size, initial_keys_capacity);
	if (!new_map) {
		return false;
	}

	// Rehash all of the values from the old map.
	for (size_t i = 0; i < header->buckets_capacity; ++i) {
		if (header->key_indices[i]) {
			char *key = header->keys + header->key_indices[i] - 1; // Subtracting 1 because key indices are offset by +1.
			void *value = header->buckets + i*header->bucket_size;
			if (!map_add(&new_map, key, value)) {
				map_destroy(&new_map);
				return false;
			}
		}
	}

	void *old_map = *map;
	*map = new_map;
	map_destroy(&old_map);
	return true;
}

size_t map_get_buckets_count_impl(void **map) {
	struct map_header *header = get_header(map);
	return header->buckets_count;
}

size_t map_get_bucket_size_impl(void **map) {
	struct map_header *header = get_header(map);
	return header->bucket_size;
}

size_t map_get_keys_capacity_impl(void **map) {
	struct map_header *header = get_header(map);
	return header->keys_capacity;
}

bool map_set_keys_capacity_impl(void **map, size_t capacity) {
	struct map_header *header = get_header(map);
	if (capacity < header->keys_size) {
		return false;
	}
	char *new_keys = realloc(header->keys, capacity);
	if (!new_keys) {
		return false;
	}
	header->keys_capacity = capacity;
	header->keys = new_keys;
	return true;
}

size_t map_get_keys_size_impl(void **map) {
	struct map_header *header = get_header(map);
	return header->keys_size;
}

bool map_is_empty_impl(void **map) {
	struct map_header *header = get_header(map);
	return header->buckets_count == 0;
}

void *map_get_impl(void **map, char *key) {
	struct map_header *header = get_header(map);
	size_t bucket_index = 0;
	enum probe_result result = probe(map, key, &bucket_index);
	if (result == PROBE_RESULT_KEY_FOUND) {
		return header->buckets + bucket_index*header->bucket_size;
	}
	return NULL;
}

bool map_set_impl(void **map, char *key, void *value) {
	struct map_header *header = get_header(map);
	size_t bucket_index = 0;
	enum probe_result result = probe(map, key, &bucket_index);
	if (result == PROBE_RESULT_KEY_FOUND) {
		memcpy(header->buckets + bucket_index*header->bucket_size, value, header->bucket_size);
		++header->buckets_count;
		return true;
	}
	return false;
}

bool map_add_impl(void **map, char *key, void *value) {
	struct map_header *header = get_header(map);
	size_t bucket_index = 0;
	enum probe_result result = probe(map, key, &bucket_index);
	if (result == PROBE_RESULT_MAP_FULL) {
		if (!map_set_buckets_capacity_impl(map, header->buckets_capacity*buckets_growth_factor)) {
			return false;
		}
		header = get_header(map);
		result = probe(map, key, &bucket_index);
		if (result != PROBE_RESULT_MAP_NOT_FULL) {
			return false;
		}
	}
	// Not an else because this needs to run if the map was full.
	if (result == PROBE_RESULT_MAP_NOT_FULL) {
		size_t key_index = add_key(map, key);
		if (key_index == 0) {
			return false;
		}
		header->key_indices[bucket_index] = key_index;
	}
	memcpy(header->buckets + bucket_index*header->bucket_size, value, header->bucket_size);
	++header->buckets_count;
	return true;
}

bool map_remove_impl(void **map, char *key) {
	struct map_header *header = get_header(map);
	size_t bucket_index = 0;
	enum probe_result result = probe(map, key, &bucket_index);
	if (result == PROBE_RESULT_KEY_FOUND) {
		header->key_indices[bucket_index] = 0;
		--header->buckets_count;
		if (header->buckets_count && header->buckets_count <= header->buckets_capacity/buckets_growth_factor) {
			return map_set_buckets_capacity(map, header->buckets_count);
		}
		return true;
	}
	return false;
}

char *map_get_key_impl(void **map, void *bucket) {
	struct map_header *header = get_header(map);
	ptrdiff_t bucket_index = ((char*)bucket - header->buckets)/header->bucket_size;
	size_t key_index = header->key_indices[bucket_index];
	if (!key_index) {
		return NULL;
	}
	return header->keys + key_index - 1; // Subtracting 1 because key indices are offset by +1.
}

bool map_index_is_full_impl(void **map, size_t bucket_index) {
	struct map_header *header = get_header(map);
	return bucket_index < header->buckets_capacity && header->key_indices[bucket_index];
}

#undef max
