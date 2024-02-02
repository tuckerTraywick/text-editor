LIBRARIES := -lncurses
CFLAGS := -g3 -Wall -pedantic -std=c17
VALGRIND_FLAGS := --leak-check=yes
CC := gcc

default: binary/run

binary/run: build/editor.o
	@mkdir -p ./binary
	@$(CC) $(CFLAGS) $(LIBRARIES) $^ -o $@

build/editor.o: source/editor.c
	@mkdir -p ./build
	@$(CC) $(CFLAGS) $(LIBRARIES) -c $^ -o $@

.PHONY: clean
clean:
	@rm -rf build binary
