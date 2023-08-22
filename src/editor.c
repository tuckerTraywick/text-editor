#include <assert.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdio.h>


#define DEFAULT_LINE_CAPACITY 100


// A single node in the linked list of lines.
// Stores the text of one line.
struct Line {
	struct Line *previous;
	struct Line *next;
	char *text;
	size_t length;
	size_t capacity;
};


// A single node in the linked list of buffers.
// Represents a buffer of text that can be edited.
struct Buffer {
	struct Buffer *previous;
	struct Buffer *next;
	struct Line *firstLine;
	struct Line *lastLine;
	struct Line *currentLine;
	size_t numberOfLines;
	size_t currentLineNumber;
	size_t cursorPosition;
};


static struct Buffer *firstBuffer;
static struct Buffer *lastBuffer;
static struct Buffer *currentBuffer;
static size_t currentBufferIndex;
static size_t numberOfBuffers;


// Opens a new buffer and appends it to the list of buffers.
void openBuffer() {
	// Allocate and initialize a new buffer and the first line of that buffer.
	char *text = malloc((sizeof *text)*DEFAULT_LINE_CAPACITY);
	struct Line *firstLine = malloc(sizeof *firstLine);
	struct Buffer *newBuffer = malloc(sizeof *newBuffer);
	assert(text != NULL && firstLine != NULL && newBuffer != NULL);
	*firstLine = (struct Line) {
		.text = text,
		.capacity = DEFAULT_LINE_CAPACITY,
	};
	*newBuffer = (struct Buffer) {
		.firstLine = firstLine,
		.lastLine = firstLine,
		.numberOfLines = 1,
		.currentLine = firstLine,
		.currentLineNumber = 0,
		.cursorPosition = 0,
	};

	// Append the new buffer to the list of buffers.
	if (numberOfBuffers == 0) {
		firstBuffer = newBuffer;
		lastBuffer = newBuffer;
	} else {
		lastBuffer->next = newBuffer;
		newBuffer->previous = lastBuffer;
	}
}


// Clears the text of the current buffer and frees most of its memory.
void clearBuffer(struct Buffer *buffer) {
	assert(buffer != NULL);
	// Free each line.
	struct Line *currentLine = buffer->firstLine;
	while (currentLine != NULL) {
		struct Line *nextLine = currentLine->next;
		free(currentLine->text);
		free(currentLine);
		currentLine = nextLine;
	}
	*buffer = (struct Buffer) {};
}


// Frees a buffer's memory.
void destroyBuffer(struct Buffer *buffer) {
	clearBuffer(buffer);
	free(buffer);
}


// Closes the current buffer and removes it from the list of buffers.
void closeBuffer() {
	if (numberOfBuffers == 0) {
		return;
	} else if (currentBuffer->previous == NULL) {
		firstBuffer = currentBuffer->next;
		destroyBuffer(currentBuffer);
		currentBuffer = firstBuffer;
	} else if (currentBuffer->next == NULL) {
		lastBuffer = currentBuffer->previous;
		destroyBuffer(currentBuffer);
		currentBuffer = lastBuffer;
	} else {
		struct Buffer *bufferToDestroy = currentBuffer;
		currentBuffer->previous->next = currentBuffer->next->next;
		currentBuffer->next->previous = currentBuffer->previous;
		currentBuffer = currentBuffer->next;
		destroyBuffer(currentBuffer);
	}
}


// Closes all buffers.
void closeAllBuffers() {
	while (currentBuffer != NULL)
		closeBuffer();
}


// Reads the file at `path` into the current buffer.
void readFromFile(char *path) {
	FILE *file = fopen(path, "r+");
	assert(file != NULL);
	assert(currentBuffer != NULL);
	clearBuffer(currentBuffer);

	// Append each line of the file to the buffer.
	while (getline(&lineText, lineLength, file) != -1) {
		char *text = malloc((sizeof *text)*DEFAULT_LINE_CAPACITY);
		assert(text != NULL);
	}
}


void writeTofile(char *path);


void saveBuffer();


void saveAllBuffers();


// Sets up the state for the editor.
void initialize() {
	openBuffer();
}


void cleanup() {
	closeAllBuffers();
}


int main(void) {
	initialize();
	cleanup();
	return 0;
}

