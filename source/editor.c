#define _POSIX_C_SOURCE 200809L // For `getline()`.
#include <assert.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <ncurses.h>

#define ESC 27
#define LINE_INITIAL_CAPACITY 200
#define BUFFER_INITIAL_CAPACITY 200

#define min(a, b) (((a) <= (b)) ? (a) : (b))

// Represents a line in a buffer.
struct Line {
	size_t capacity; // The maximum length of the line.
	size_t length; // The current length of the line.
	char *text; // The buffer that holds the text of the line.
};

// Represents an open file in the editor.
struct Buffer {
	size_t capacity; // The maximum number of lines.
	size_t length; // The current number of lines.
	struct Line *lines; // The buffer that holds the lines.
};

// Represents the cursor the user controls.
struct Cursor {
	size_t y; // The index of the row the cursor points to.
	size_t x; // The index of the column the cursor points to.
};

// Represents what mode the editor is in.
enum EditorMode {
	NORMAL, EDIT,
};

// Represents the state of the text editor.
struct Editor {
	char *filePath; // The path of the file being edited.
	struct Buffer buffer; // The buffer being edited.
	size_t cursorY; // The line the cursor points to.
	size_t cursorX; // The character the cursor points to.
	size_t scrollY; // The line the screen starts at.
	size_t scrollX; // The character the screen starts at.
	enum EditorMode mode; // What mode the editor is in.
	bool keepRunning; // Flag to keep running.
	bool hasUnsavedChanges; // Whether the buffer has unsaved changes.
};

// Returns a new line.
struct Line lineCreate(void) {
	char *text = malloc(LINE_INITIAL_CAPACITY);
	assert(text && "`malloc()` failed."); // TODO: Handle failed `malloc()`.
	return (struct Line){
		.capacity = LINE_INITIAL_CAPACITY,
		.text = text,
	};
}

// Destroys `line` and zeros its memory.
void lineDestroy(struct Line *line) {
	assert(line);

	free(line->text);
	*line = (struct Line){0};
}

// Returns a new buffer.
struct Buffer bufferCreate(void) {
	struct Line *lines = malloc((sizeof (struct Line))*BUFFER_INITIAL_CAPACITY);
	assert(lines && "`malloc()` failed."); // TODO: Handle failed `malloc()`.
	lines[0] = lineCreate();
	return (struct Buffer){
		.capacity = BUFFER_INITIAL_CAPACITY,
		.length = 1,
		.lines = lines,
	};
}

// Destroys `buffer` and zeros its memory.
void bufferDestroy(struct Buffer *buffer) {
	assert(buffer);

	for (size_t i = 0; i < buffer->length; ++i) {
		lineDestroy(buffer->lines + i);
	}
	free(buffer->lines);
	*buffer = (struct Buffer){0};
}

// Appends `line` to `buffer`.
void bufferAppendLine(struct Buffer *buffer, struct Line *line) {
	assert(buffer);
	assert(line);

	// Expand the buffer if needed.
	if (buffer->length == buffer->capacity) {
		buffer->capacity *= 2;
		buffer->lines = realloc(buffer->lines, buffer->capacity);
		assert(buffer->lines && "`realloc()` failed."); // TODO: Handle failed `realloc()`.
	}
	buffer->lines[buffer->length] = *line;
	++buffer->length;
}

// Empties `buffer`. Does not change its capacity.
void bufferClear(struct Buffer *buffer) {
	assert(buffer);

	for (size_t i = 0; i < buffer->length; ++i) {
		lineDestroy(buffer->lines + i);
	}
	buffer->length = 0;
}

// Reads `file` into `buffer` line by line..
void bufferReadFile(struct Buffer *buffer, FILE *file) {
	assert(file);
	assert(buffer);

	bufferClear(buffer);
	while (!feof(file)) {
		struct Line line = {0};
		line.length = getline(&line.text, &line.capacity, file);
		// TODO: Handle failed `getline()`.
		assert(line.text && "`getline()` failed.");
		
		// If `line.text` is not null and `getline()` returns -1, then the file ends in a trailing
		// newline and there is no more text to read, so we can exit early.
		if (line.length == -1) {
			free(line.text);
			return;
		}

		// Remove the '\n' if necessary.
		if (line.text[line.length - 1] == '\n') {
			--line.length;
			line.text[line.length] = '\0';
		}
		bufferAppendLine(buffer, &line);
	}
}

// Returns a new editor.
struct Editor editorCreate(void) {
	return (struct Editor){
		.filePath = "untitled",
		.buffer = bufferCreate(),
		.keepRunning = true,
		.hasUnsavedChanges = true,
	};
}

// Destroys `editor` and zeros its memory.
void editorDestroy(struct Editor *editor) {
	assert(editor);

	bufferDestroy(&editor->buffer);
	*editor = (struct Editor){0};
}

// Loads the file at `path` into `editor`.
void editorLoadFile(struct Editor *editor, char *path) {
	assert(editor);
	assert(path);

	// TODO: Check if editor has unsaved changes before loading the file.
	FILE *file = fopen(path, "r");
	assert(file && "`fopen()` failed."); // Handle failed `fopen()`.
	editor->filePath = path;
	editor->hasUnsavedChanges = false;
	bufferReadFile(&editor->buffer, file);
	fclose(file);
}

// Draws the buffer.
void editorDrawBuffer(struct Editor *editor) {
	assert(editor);

	size_t linesOnScreen = min(LINES - 1, editor->buffer.length - editor->scrollY);
	for (size_t y = 0; y < linesOnScreen; ++y) {
		size_t lineNumber = editor->scrollY + y + 1;
		printw("%3.zu %s\n", lineNumber, editor->buffer.lines[y + editor->scrollY].text);
	}
}

// Draws the status bar.
void editorDrawStatusBar(struct Editor *editor) {
	assert(editor);

	size_t linesOnScreen = min(LINES - 1, editor->buffer.length - editor->scrollY);
	for (size_t y = 0; y < LINES - linesOnScreen - 1; ++y) {
		printw("\n");
	}
	
	static char *modes[] = {
		[NORMAL] = "NORMAL",
		[EDIT]   = "EDIT  ",
	};
	char star = (editor->hasUnsavedChanges) ? '*' : ' ';
	printw("%s %c%s", modes[editor->mode], star, editor->filePath);
}

// Draws the cursor.
void editorDrawCursor(struct Editor *editor) {
	assert(editor);

	int y = editor->cursorY - editor->scrollY;
	int x = editor->cursorX + 4;
	move(y, x);
}

// Draws the editor's ui.
void editorDraw(struct Editor *editor) {
	assert(editor);

	clear();
	editorDrawBuffer(editor);
	editorDrawStatusBar(editor);
	editorDrawCursor(editor);
	refresh();
}

// Returns the line the cursor points to.
struct Line *editorCurrentLine(struct Editor *editor) {
	assert(editor);
	
	return editor->buffer.lines + editor->cursorY;
}

// Moves the cursor up one line.
void editorCursorLineUp(struct Editor *editor) {
	assert(editor);

	if (editor->cursorY > 0) {
		--editor->cursorY;
		editor->cursorX = min(editor->cursorX, editorCurrentLine(editor)->length);
	} else {
		editor->cursorX = 0;
	}
}

// Moves the cursor down one line.
void editorCursorLineDown(struct Editor *editor) {
	assert(editor);

	if (editor->cursorY < editor->buffer.length - 1) {
		++editor->cursorY;
		editor->cursorX = min(editor->cursorX, editorCurrentLine(editor)->length);
	} else {
		editor->cursorX = editorCurrentLine(editor)->length;
	}
}

// Moves the cursor left one character.
void editorCursorChracterLeft(struct Editor *editor) {
	assert(editor);

	if (editor->cursorX > 0) {
		--editor->cursorX;
	} else if (editor->cursorY > 0) {
		editorCursorLineUp(editor);
		editor->cursorX = editorCurrentLine(editor)->length;
	}
}

// Moves the cursor right one character.
void editorCursorChracterRight(struct Editor *editor) {
	assert(editor);

	if (editor->cursorX < editorCurrentLine(editor)->length) {
		++editor->cursorX;
	} else if (editor->cursorY < editor->buffer.length - 1) {
		editorCursorLineDown(editor);
		editor->cursorX = 0;
	}
}

// Processes a keypress and updates the editor's state.
void editorProcessKeypress(struct Editor *editor) {
	assert(editor);

	int ch = getch();
	switch (editor->mode) {
		case NORMAL:
			switch (ch) {
				case 'q':
					editor->keepRunning = false;
					break;	
				case 'e':
					editor->mode = EDIT;
					break;
				case 'i':
				case KEY_UP:
					editorCursorLineUp(editor);
					break;				
				case 'k':
				case KEY_DOWN:
					editorCursorLineDown(editor);
					break;
				case 'j':
				case KEY_LEFT:
					editorCursorChracterLeft(editor);
					break;
				case 'l':
				case KEY_RIGHT:
					editorCursorChracterRight(editor);
					break;
			}
			break;

		case EDIT:
			switch (ch) {
				case 'q':
					editor->keepRunning = false;
					break;
				case ESC:
					editor->mode = NORMAL;
					break;
			}
			break;
	}
}

// Runs the main event loop.
void editorRun(struct Editor *editor) {
	assert(editor);

	initscr();
	raw();
	keypad(stdscr, TRUE);
	set_escdelay(0);
	noecho();

	while (editor->keepRunning) {
		editorDraw(editor);
		editorProcessKeypress(editor);
	}

	endwin();
}

int main(void) {
	struct Editor editor = editorCreate();
	editorLoadFile(&editor, "example.txt");
	editorRun(&editor);

	editorDestroy(&editor);
	return 0;
}
