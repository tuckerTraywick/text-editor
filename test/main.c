#define TEST_IMPLEMENTATION
#include "test.h"
#include "editor.c"

// Prints a `Line` to stdout.
#define printLine(line) (log("capacity=%zu, length=%zu, text='%s'\n", line.capacity, line.length, line.text))

static void testAppendCharacter(void) {
    struct Line line = newLine();
    appendCharacter(&line, 'a');
    test(line.text != NULL);
    test(line.length == 1);
    //printLine(line);
    appendCharacter(&line, 'b');
    test(line.length == 2);
    test(line.text[1] == '\0');
    //log("'%s'\n", line.text[2]);
    test(line.text[line.capacity] == '\0');
}

int main(void) {
    beginTesting();
        testAppendCharacter();
    endTesting();
    return 0;
}
