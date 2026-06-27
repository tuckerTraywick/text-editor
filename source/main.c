#include <ctype.h>
#include <stdio.h>
#include <unistd.h>
#include "ui.h"

static const char *const special_key_names[] = {
	['e'] = "esc",
	['i'] = "ins",
	['D'] = "del",
	['l'] = "left",
	['r'] = "right",
	['u'] = "up",
	['d'] = "down",
};

static void print_keypress(struct keypress key) {
	printf("%d ", key.base_key);
	if (key.is_ctrl) {
		printf("ctrl + ");
	}
	if (key.is_alt) {
		printf("alt + ");
	}

	if (key.is_fn) {
		printf("f%d\r\n", key.base_key);
	} else if (key.is_special) {
		printf("%s\r\n", special_key_names[key.base_key]);
	} else if (key.base_key == ' ') {
		printf("space\r\n");
	} else if (key.base_key == '\t') {
		printf("tab\r\n");
	} else if (key.base_key == "\n") {
		printf("ret\r\n");
	} else if (key.base_key == ASCII_DEL) {
		printf("bkspc\r\n");
	} else {
		printf("%c\r\n", key.base_key);
	}
}

int main(void) {
	struct window window = {0};
	if (!window_initialize(&window)) {
		fprintf(stderr, "Error initializing window.");
		goto error1;
	}

	printf("ch = %d\r\n", '\b');
	while (true) {
		struct keypress key = window_get_character(&window);
		if (!key.base_key) {
			continue;
		}
		print_keypress(key);

		if (key.base_key == 'q') {
			break;
		}
	}

	window_destroy(&window);
	return 0;

error1:
	return 1;
}
