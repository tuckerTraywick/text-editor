#ifndef MAP_H
#define MAP_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#define map_destroy(map) (map_destroy_impl((void**)(map)))

#define map_get_buckets_capacity(map) (map_get_buckets_capacity_impl((void**)(map)))

// If you pass a capacity smaller than the map's current count, this function does nothing and
// returns false.
#define map_set_buckets_capacity(map, capacity) (map_set_buckets_capacity_impl((void**)(map), (capacity)))

#define map_get_buckets_count(map) (map_get_buckets_count_impl((void**)(map)))

#define map_get_bucket_size(map) (map_get_bucket_size_impl((void**)(map)))

#define map_get_keys_capacity(map) (map_get_keys_capacity_impl((void**)(map)))

// If you pass a capacity smaller than the current size of the map's key buffer, this function does
// nothing and returns false.
#define map_set_keys_capacity(map, capacity) (map_set_keys_capacity_impl((void**)(map), (capacity)))

#define map_get_keys_size(map) (map_get_keys_size_impl((void**)(map)))

#define map_is_empty(map) (map_is_empty_impl((void**)(map)))

#define map_get(map, key) (map_get_impl((void**)(map), (key)))

#define map_set(map, key, value) (map_set_impl((void**)(map), (key), (value)))

#define map_add(map, key, value) (map_add_impl((void**)(map), (key), (value)))

#define map_remove(map, key) (map_remove_impl((void**)(map), (key)))

#define map_get_key(map, bucket) (map_get_key_impl((void**)(map), (bucket)))

// Returns true if the map has a value in the bucket at the index. Used for iterating over a map's
// buckets.
#define map_index_is_full(map, bucket_index) (map_index_is_full_impl((void**)(map), (bucket_index)))

extern const size_t buckets_growth_factor;

extern const size_t keys_growth_factor;

void *map_create(size_t buckets_capacity, size_t bucket_size, size_t keys_capacity);

void map_destroy_impl(void **map);

size_t map_get_buckets_capacity_impl(void **map);

bool map_set_buckets_capacity_impl(void **map, size_t capacity);

size_t map_get_buckets_count_impl(void **map);

size_t map_get_bucket_size_impl(void **map);

size_t map_get_keys_capacity_impl(void **map);

bool map_set_keys_capacity_impl(void **map, size_t capacity);

size_t map_get_keys_size_impl(void **map);

bool map_is_empty_impl(void **map);

void *map_get_impl(void **map, char *key);

bool map_set_impl(void **map, char *key, void *value);

bool map_add_impl(void **map, char *key, void *value);

bool map_remove_impl(void **map, char *key);

char *map_get_key_impl(void **map, void *bucket);

bool map_index_is_full_impl(void **map, size_t bucket_index);

#endif // MAP_H
