#include <stddef.h>
#include <stdio.h>
#include <ncurses.h>
#include "list.h"

// Represents a line in a buffer. Stores a length. Not null-terminated and does not include an '\r'
// or '\n'.
struct Line {
	size_t length; // The current number of characters in the line.
	size_t capacity; // The number of characters allocated for the line.
	char text[1]; // The text of the line. `capacity` characters long.
};
typedef struct List LineList;

// Represents an open file in the editor. Stores a dynamic array of lines.
struct Buffer {
	size_t linesLength; // The current number of lines in the buffer.
	size_t linesCapacity; // The number of lines allocated for the buffer.
	LineList lines; // The lines of the buffer.
};
typedef struct List BufferList;

// Represnts a selection of text being edited.
struct Cursor {
	size_t startY; // The first (lowest index) line selected by the cursor.
	size_t startX; // The first character of the first line selected by the cursor.
	size_t endY; // The last (highest index) line selected by the cursor.
	size_t endX; // The last character of the last line selected by the cursor.
};
typedef struct List CursorList;

struct Tab {
	char *name;
	size_t scrollY;
	size_t scrollX;
	struct Buffer buffer;
	CursorList cursors;
	size_t mainCursorIndex;
};
typedef struct List TabList;

struct Editor {
	size_t tabsLength;
	size_t tabsCapacity;
	TabList tabs;
	size_t currentTabIndex;
};

int main(void) {
	initscr();
	raw();
	keypad(stdscr, TRUE);
	noecho();

	printw("hi");
	getch();

	endwin();
	return 0;
}
