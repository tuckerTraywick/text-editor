#define _POSIX_C_SOURCE 200809L // For `getline()`.
#include <assert.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
#include <ncurses.h>
#include "list.h"

// Represents a line in a buffer. Must be destroyed with `lineDestroy()`.
struct Line {
	size_t capacity; // The number of characters allocated for the line including the '\0'.
	size_t length; // The current number of characters in the line, excluding the '\0'.
	char *text; // The text of the line. Does not include '\n', but does include a '\0'.
};
typedef struct List LineList;

// Represents an open file in the editor.
struct Buffer {
	LineList lines; // The lines of the buffer.
};
typedef struct List BufferList;

// Represents a selection of text being edited.
struct Cursor {
	size_t startY; // The first (lowest index) line selected by the cursor.
	size_t startX; // The first character of the first line selected by the cursor.
	size_t endY; // The last (highest index) line selected by the cursor.
	size_t endX; // The last character of the last line selected by the cursor.
};
typedef struct List CursorList;

// Represents a tab in the editor. Stores all of the information the editor needs to know about a
// buffer.
struct Tab {
	char *name; // The name of the tab in the tab list.
	size_t scrollY; // The line number the screen starts at.
	size_t scrollX; // The character the screen starts at.
	struct Buffer buffer; // The buffer being edited in the tab.
	CursorList cursors; // The cursors in the tab.
	size_t mainCursorIndex; // The index of the main cursor the user is controlling.
};
typedef struct List TabList;

// Represents the state of the text editor.
struct Editor {
	TabList tabs; // The open tabs.
	size_t currentTabIndex; // The index of the currently focused tab.
};

// Destroys a line and zeros its memory.
void lineDestroy(struct Line *line) {
	free(line->text);
	*line = (struct Line){0};
}

// Returns a new buffer. Must be destroyed with `bufferDestroy()`.
static struct Buffer bufferCreate(void) {
	return (struct Buffer){.lines = listCreate(1, sizeof (struct Line))};
}

// Deallocates a buffer's lines and zeroes its memory.
static void bufferDestroy(struct Buffer *buffer) {
	for (size_t i = 0; i < buffer->lines.length; ++i) {
		lineDestroy(listGet(&buffer->lines, i));
	}
	listDestroy(&buffer->lines);
	*buffer = (struct Buffer){0};
}

// Reads a file into a buffer.
static void bufferReadFile(FILE *file, struct Buffer *buffer) {
	assert(file);
	assert(buffer);

	while (!feof(file)) {
		struct Line line = {0};
		line.length = getline(&line.text, &line.capacity, file);
		// TODO: Handle failed `getline()`.
		assert(line.text && "`getline()` failed.");
		
		// If `line.text` is not null and `getline()` returns -1, then the file ends in a trailing
		// newline and there is no more text to read, so we can exit early.
		if (line.length == -1) {
			return;
		}

		// Remove the '\n' if necessary.
		if (line.text[line.length - 1] == '\n') {
			line.text[line.length - 1] = '\0';
			--line.length;
		}
		listAppend(&buffer->lines, &line);
	}
}

// Returns a new tab. Must be destroyed with `tabDestroy()`.
struct Tab tabCreate(char *name) {
	assert(name);

	CursorList cursors = listCreate(1, sizeof (struct Cursor));
	struct Cursor cursor = {0};
	listAppend(&cursors, &cursor);
	return (struct Tab){
		.name = name,
		.buffer = bufferCreate(),
		.cursors = cursors,
	};
}

// Destroys a tab and zeroes its memory.
void tabDestroy(struct Tab *tab) {
	assert(tab);

	bufferDestroy(&tab->buffer);
	listDestroy(&tab->cursors);
	*tab = (struct Tab){0};
}

// Returns a new editor.
struct Editor editorCreate(void) {
	return (struct Editor){
		.tabs = listCreate(10, sizeof (struct Tab)),
	};
}

// Destroys an editor and zeroes its memory.
void editorDestroy(struct Editor *editor) {
	assert(editor);


	listDestroy(&editor->tabs);
}

int main(void) {
	struct Tab tab = tabCreate("example.txt");


	tabDestroy(&tab);

	return 0;
}

// int main(void) {
// 	FILE *file = fopen("example.txt", "r");
// 	assert(file && "`fopen()` failed.");
// 	struct Buffer buffer = bufferCreate();

// 	bufferReadFile(file, &buffer);
// 	printf("buffer length = %zu\n", buffer.lines.length);
// 	for (size_t i = 0; i < buffer.lines.length; ++i) {
// 		struct Line *line = listGet(&buffer.lines, i);
// 		printf("%.2zu (length = %.2zu) %s\n", i + 1, line->length, line->text);
// 	}

// 	fclose(file);
// 	bufferDestroy(&buffer);

// 	return 0;
// }

// int main(void) {
// 	struct List list = listCreate(10, sizeof(int));
// 	int a = 1;
// 	int b = 2;
// 	int c = 3;
// 	listAppend(&list, &a);
// 	listAppend(&list, &b);
// 	listAppend(&list, &c);
// 	listSwap(&list, 0, 1);
// 	int x = 7;
// 	listSet(&list, 1, &x);
// 	x = 100;
// 	listInsert(&list, 2, &x);

// 	for (size_t i = 0; i < list.length; ++i) {
// 		printf("list[%zu] = %d\n", i, *(int*)listGet(&list, i));
// 	}

// 	listDestroy(&list);

// 	return 0;
// }
