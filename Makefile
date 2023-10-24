ARGS :=
LIBRARIES := -lncurses
CFLAGS := -g -Wall -pedantic -std=c17
VALGRIND_FLAGS := --leak-check=yes
CC := gcc

SRC_FILES := $(shell find source -name '*.c')
OBJ_FILES := $(SRC_FILES:%=build/%.o)
D_FILES := $(SRC_FILES:%=build/%.d)

TEST_SRC_FILES := $(shell find test -name '*.c' 2> /dev/null)
TEST_OBJ_FILES := $(TEST_SRC_FILES:%=build/%.o)
TEST_D_FILES := $(TEST_SRC_FILES:%=build/%.d)

# .PRECIOUS: build/%.d

.PHONY: all
all: source newline tests

.PHONY: source
source: sourcemessage binary/run

.PHONY: tests
tests: testsmessage binary/test

.PHONY: run
run: source
	@echo
	@echo "--- RUNNING ---" && binary/run $(ARGS)

.PHONY: valgrind
valgrind: source
	@echo
	@echo "--- RUNNING IN VALGRIND ---" && valgrind $(VALGRIND_FLAGS) binary/run $(ARGS)

.PHONY: test
test: tests
	@echo
	@echo "--- TESTING ---" && binary/test

.PHONY: testinvalgrind
testinvalgrind: tests
	@echo
	@echo "--- TESTING IN VALGRIND ---" && valgrind $(VALGRIND_FLAGS) binary/test

.PHONY: testandrun
testandrun: test run

.PHONY: testandvalgrind
testandvalgrind: test valgrind

.PHONY: clean
clean:
	@rm -rf build binary

.PHONY: sourcemessage
sourcemessage:
	@echo "--- BUILDING SOURCE ---"

.PHONY: testsmessage
testsmessage:
	@echo "--- BUILDING TESTS ---"

.PHONY: newline
newline:
	@echo

binary/run: $(OBJ_FILES)
	@mkdir -p binary
	$(CC) $(LDFLAGS) $(LIBRARIES) $^ -o $@

binary/test: $(TEST_OBJ_FILES)
	@mkdir -p binary
	$(CC) $(LDFLAGS) $(LIBRARIES) $^ -o $@

build/source/%.o: source/%
	@mkdir -p $(dir $@)
	$(CC) -c -MMD -MP -MT $@ -MF build/source/$*.d -Iinclude $(CFLAGS) $(LIBRARIES) source/$* -o $@

build/test/%.o: test/%
	@mkdir -p $(dir $@)
	$(CC) -c -MMD -MP -MT $@ -MF build/test/$*.d -Iinclude -Isource -Itest $(CFLAGS) $(LIBRARIES) test/$* -o $@

-include $(D_FILES) $(TEST_D_FILES)
