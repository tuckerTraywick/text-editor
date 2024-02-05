INCLUDE := -Iinclude
LIBRARIES := -lncurses
CFLAGS := -g3 -Wall -pedantic -std=c99
VALGRIND_FLAGS := --leak-check=yes
CC := gcc

default: binary/run

binary/run: build/editor.o build/list.o
	@mkdir -p ./binary
	@$(CC) $(CFLAGS) $(INCLUDE) $(LIBRARIES) $^ -o $@

build/%.o: source/%.c
	@mkdir -p ./build
	@$(CC) $(CFLAGS) $(INCLUDE) $(LIBRARIES) -c $^ -o $@

source/editor.c: list.h

source/list.c: list.h

list.h:

.PHONY: clean
clean:
	@rm -rf build binary
