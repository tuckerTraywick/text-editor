#include <stddef.h> // size_t
#include <stdbool.h> // bool
#include <stdlib.h> // malloc(), calloc(), realloc(), free()
#include <string.h> // memset()
#include <stdio.h> // FILE, fopen(), ftell(), fseek()
#include <assert.h> // assert()
#include <ncurses.h>

#define lineStartingCapacity 2 // The initial number of characters allocated for a line.
#define lineCapacityIncrement 1 // The number of characters allocated when a line runs out of space.
#define bufferStartingCapacity 100 // The initial number of lines allocated for a buffer.
#define bufferCapacityIncrement 100 // The number of lines allocated when a buffer runs out of space.

// A line of text in a buffer.
struct Line {
	size_t capacity; // The number of characters allocated for the line.
	size_t length; // The number of characters currently in the line (EXCLUDING the null terminator).
	char *text; // The text of the line (null terminated).
};

// A buffer of lines that can be edited.
struct Buffer {
	size_t capacity; // The number of lines allocated for the buffer.
	size_t length; // The number of lines currently in the buffer.
	struct Line *lines; // The array of lines in the buffer.
};

// Returns a new line.
static struct Line newLine() {
	struct Line line = {0};
	line.capacity = lineStartingCapacity;
	line.length = 0;
	line.text = calloc(line.capacity, sizeof *line.text);
	assert("calloc() failed." && line.text != NULL);
	return line;
}

// Gets a character from a line.
static char getCharacter(struct Line *line, size_t index) {
	assert("Index out of bounds." && index <= line->length);
	return line->text[index];
}

// Sets a character in a line.
static void setCharacter(struct Line *line, size_t index, char ch) {
	assert("Index out of bounds." && index <= line->length);
	line->text[index] = ch;
}

// Appends a character to a line.
static void appendCharacter(struct Line *line, char ch) {
	assert("Length incremented too much." && line->length <= line->capacity - 1);
	if (line->length == line->capacity - 1) {
		line->capacity += lineCapacityIncrement;
		char *newText = realloc(line->text, line->capacity);
		assert("realloc() failed." && newText != NULL);
		line->text = newText;
		// Zero out the rest of the line after the new character so it is null terminated.
		memset(line->text + line->length + 1, '\0', line->capacity - line->length - 1);
	}
	setCharacter(line, line->length, ch);
	++line->length;
}

// Returns one line of text from a file.
static bool readLine(struct Line *line, FILE *file) {
	while (1) {
		char ch = fgetc(file);
		if (ch == EOF || ch == '\n') {
			return TRUE;
		}
	}
}

// Initializes and returns a buffer containing the text of a file.
static struct Buffer readFile(const char *path) {
	// Open the file.
	FILE *file = fopen(path, "r");
	assert("fopen() failed." && file != NULL);
	
	// Read each line of the file into the buffer.
	struct Buffer buffer = {0};
	struct Line line = {0};
	while (readLine(&line, file)) {

	}

	fclose(file);
}

// int main(void) {
// 	initscr();
// 	cbreak();
// 	noecho();
// 	keypad(stdscr, TRUE);

// 	// Set up buffer.
// 	struct Buffer buffer = readFile("source/example.txt");

// 	getch();

// 	endwin();
// 	return 0;
// }
