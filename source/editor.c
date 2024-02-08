#define _POSIX_C_SOURCE 200809L // For `getline()`.
#include <assert.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
#include <ncurses.h>
#include "list.h"

// Represents a line in a buffer.
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

// Returns a new buffer. Must be destroyed with `bufferDestroy()`.
static struct Buffer bufferCreate(void) {
	return (struct Buffer){.lines = listCreate(1, sizeof (struct Line))};
}

// Deallocates a buffer's lines and zeroes its memory.
static void bufferDestroy(struct Buffer *buffer) {
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
		
		if (line.length == -1) {
			// Reached the end of the file.
			return;
		}

		// Remove the '\n' if necessary.
		if (line.text[line.length - 1] == '\n') {
			line.text[line.length - 1] = '\0'; // Remove the '\n'.
			--line.length;
		}
		listAppend(&buffer->lines, &line);
	}
}

int main(void) {
	// initscr();
	// raw();
	// keypad(stdscr, TRUE);
	// noecho();

	FILE *file = fopen("example.txt", "r");
	assert(file && "`fopen()` failed.");
	struct Buffer buffer = bufferCreate();
	bufferReadFile(file, &buffer);
	printf("buffer length = %zu\n", buffer.lines.length);
	for (size_t i = 0; i < buffer.lines.length; ++i) {
		struct Line *line = listGet(&buffer.lines, i);
		printf("%zu(%zu) %s\n", i, line->length, line->text);
	}

	bufferDestroy(&buffer);

	// endwin();
	return 0;
}

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
