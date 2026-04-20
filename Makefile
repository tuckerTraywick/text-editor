args :=
libraries := $(shell pkg-config --libs ncurses)
cflags := -std=gnu99 -Wall -Wpedantic -Wextra -g3 $(shell pkg-config --cflags ncurses)
cc := gcc
main_file = editor.c

source_files := $(shell find source -name '*.c' -not -name "main_file")
object_files := $(source_files:%=build/%.o)
d_files := $(source_files:%=build/%.d)

# test_source_files := $(shell find tests -name '*.c')
# test_object_files := $(test_source_files:%=build/%.o)
# test_d_files := $(test_source_files:%=build/%.d)

.PHONY: all
all: build/run # build/test

build/run: $(object_files) build/source/$(main_file).o
	@mkdir -p build
	@$(cc) $(libraries) $^ -o $@

# build/test: $(test_object_files) $(object_files)
# 	@mkdir -p build
# 	@$(cc) $(libraries) $^ -o $@

build/source/%.o: source/%
	@mkdir -p $(dir $@)
	@$(cc) -c -MMD -MP -MT $@ -MF build/source/$*.d -Iinclude $(cflags) $(libraries) source/$* -o $@

# build/tests/%.o: tests/%
# 	@mkdir -p $(dir $@)
# 	@$(cc) -c -MMD -MP -MT $@ -MF build/tests/$*.d -Iinclude -Isource -Itests $(cflags) $(libraries) tests/$* -o $@

-include $(d_files) # $(test_d_files)

.PHONY: clean
clean:
	@rm -rf build
