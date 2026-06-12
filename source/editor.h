#ifndef EDITOR_H
#define EDITOR_H

#include <stddef.h>
#include <stdbool.h>

typedef size_t keycode;

struct editor;

bool editor_initialize(struct editor *editor);

void editor_destroy(struct editor *editor);

keycode editor_read_key(struct editor *editor);

void editor_process_key(struct editor *editor, keycode key);

void editor_print(struct editor *editor, char *text);

void editor_draw(struct editor *editor);

void editor_update(struct editor *editor);

#endif // EDITOR_H
