LIBRARIES := -lncurses
CFLAGS := -g3 -Wall -pedantic -std=c99
VALGRIND_FLAGS := --leak-check=yes
CC := gcc

default: binary/runeditor binary/runkeylogger

editor: binary/runeditor

keylogger: binary/runkeylogger

binary/runeditor: build/editor.o
	@mkdir -p ./binary
	@$(CC) $(CFLAGS) $(LIBRARIES) $^ -o $@

build/editor.o: source/editor.c
	@mkdir -p ./build
	@$(CC) $(CFLAGS) $(LIBRARIES) -c $^ -o $@

binary/runkeylogger: build/keylogger.o
	@mkdir -p ./binary
	@$(CC) $(CFLAGS) $(LIBRARIES) $^ -o $@

build/keylogger.o: source/keylogger.c
	@mkdir -p ./build
	@$(CC) $(CFLAGS) $(LIBRARIES) -c $^ -o $@

.PHONY: clean
clean:
	@rm -rf build binary
