// TODO: Finish insert()
// TODO: Finish expandLine()
#include <assert.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>


#define DEFAULT_LINE_CAPACITY 100
#define LINE_CAPACITY_INCREMENT 50
#define DEFAULT_BUFFER_CAPACITY 100
#define BUFFER_CAPACITY_INCREMENT 20


// Stores the text of one line.
struct Line {
	char *text;
	size_t length;
	size_t capacity;
};


// Represents a buffer of text that can be edited.
struct Buffer {
	struct Line *lines;
	size_t length; // The number of lines in the buffer.
	size_t capacity; // The maximum number of lines the buffer can store.
	size_t currentLine;
	size_t cursorIndex;
};


// Stores the state of the editor.
struct Editor {
	struct Buffer *buffers;
	size_t numberOfBuffers;
	size_t maxNumberOfBuffers;
	size_t currentBufferIndex;
};


// Initializes a Line and allocates memory for its text.
void initializeLine(struct Line *line) {
	char *text = malloc((sizeof *text)*(DEFAULT_LINE_CAPACITY + 1));
	assert(text != NULL);
	text[0] = '\0';
	*line = (struct Line) {
		.text = text,
		.capacity = DEFAULT_LINE_CAPACITY,
	};
}


// Destroys a Line and frees its text.
void destroyLine(struct Line *line) {
	free(line->text);
	line->text = NULL;
}


// Prints the contents of `line` to the console.
void printLine(struct Line line) {
	assert(line.text != NULL);
	fputs(line.text, stdout);
}


// TODO
// Resizes `text`'s buffer to fit `capacity`.
void expandLine(struct Line *line, size_t capacity);


// TODO
// Inserts `text` into the line starting at `index`.
void insert(struct Line *line, char *text, size_t length, size_t index) {
	if (line->capacity < line->length + length) {
		expandLine(line, line->capacity - line->length + length);
	} else {
		memmove(line->text + index + length, line->text + index, length);
		memcpy(line->text + index, text, length);
	}
}


// Initializes a Buffer and allocates memory for its lines.
void initializeBuffer(struct Buffer *buffer) {
	struct Line *lines = malloc((sizeof *lines)*DEFAULT_BUFFER_CAPACITY);
	assert(lines != NULL);
	*buffer = (struct Buffer) {
		.lines = lines,
		.capacity = DEFAULT_BUFFER_CAPACITY,
	};
}


// Destroys a Buffer and frees its lines.
void destroyBuffer(struct Buffer *buffer) {
	for (size_t i = 0; i < buffer->length; ++i)
		destroyLine(&buffer->lines[i]);
	free(buffer->lines);
	buffer->lines = NULL;
}


// Appends a new line containing the text of `lineText` to `buffer`.
void appendLineToBuffer(struct Buffer *buffer, struct Line line) {
	if (buffer->length < buffer->capacity) {
		buffer->lines[buffer->length] = line;
	} else {
		buffer->capacity += BUFFER_CAPACITY_INCREMENT;
		buffer->lines = realloc(buffer->lines, buffer->capacity);
		assert(buffer->lines);
	}
	++buffer->length;
}


// Reads the contents of the file at `path` into `buffer` line by line.
void readFileIntoBuffer(struct Buffer *buffer, char *path) {
	// Make sure the buffer is empty.
	destroyBuffer(buffer);
	initializeBuffer(buffer);
	// Open the file.
	FILE *file = fopen(path, "r+"); // r+ to check that the file can be written to.
	assert(file != NULL);
	char *lineText = NULL;
	ssize_t lineLength = 0;
	size_t lineCapacity = 0;
	// Loop through each line and append it to the buffer.
	while ((lineLength = getline(&lineText, &lineCapacity, file)) >= 0) {
		if (lineText[lineLength - 1] == '\n') {
			lineText[lineLength] = '\0';
			lineLength -= 1;
		}
		struct Line line = {
			.text = lineText,
			.length = lineLength,
			.capacity = lineCapacity,
		};
		appendLineToBuffer(buffer, line);
		lineText = NULL;
		lineLength = 0;
		lineCapacity = 0;
	}
	fclose(file);
}


// Writes the contents of `buffer` into the file at `path` line by line.
void writeBufferToFile(struct Buffer *buffer, char *path) {
	FILE *file = fopen(path, "w");
	assert(file != NULL);
	if (buffer->length != 0) {
		for (size_t i = 0; i < buffer->length - 1; ++i) {
			fputs(buffer->lines[i].text, file);
			//fputc('\n', file);
		}
		fputs(buffer->lines[buffer->length - 1].text, file);
	}
	fclose(file);
}


// Prints the contents of `buffer` to the console.
void printBuffer(struct Buffer *buffer) {
	for (size_t i = 0; i < buffer->length; ++i) {
		printLine(buffer->lines[i]);
	}
}


// Returns a pointer to the line the `buffer`'s cursor is on.
struct Line *currentLine(struct Buffer *buffer) {
	return &buffer->lines[buffer->currentLine];
}


// Inserts `text` to the left of `buffer`'s cursor.
void insertBeforeCursor(struct Buffer *buffer, char *text, size_t length) {
	insert(currentLine(buffer), text, length, buffer->cursorIndex);
}


void deleteBeforeCursor(struct Buffer *buffer, size_t amount);


void deleteAfterCursor(struct Buffer *buffer, size_t amount);


void cursorLineUp(struct Buffer *buffer, size_t amount) {}


void cursorLineDown(struct Buffer *buffer, size_t amount) {}


void cursorCharacterLeft(struct Buffer *buffer, size_t amount) {}


void cursorCharacterRight(struct Buffer *buffer, size_t amount) {}


void cursorWordLeft(struct Buffer *buffer, size_t amount) {}


void cursorWordRight(struct Buffer *buffer, size_t amount) {}


void initializeEditor(struct Editor *editor) {}


void destroyEditor(struct Editor *editor) {}


void draw(struct Editor *editor) {}


void processInput(struct Editor *editor) {}


int main(void) {
	struct Buffer buffer;
	initializeBuffer(&buffer);
	printBuffer(&buffer);
	destroyBuffer(&buffer);
	return 0;
}

