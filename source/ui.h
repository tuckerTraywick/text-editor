#ifndef UI_H

#include <stdint.h>

struct window;

struct window *window_create(uint32_t width, uint32_t height);

void window_destroy(struct window *window);

void button(struct window *window, char *label);

#endif // UI_H
