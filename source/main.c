#include <ctype.h>
#include <stdio.h>
#include <unistd.h>
#include "ui.h"

static const char *const special_key_codes[] = {
	[ASCII_ESC] = "27",
	['2'] = "27 91 50 126",
	['3'] = "27 91 51 126",
	['A'] = "27 91 65",
	['B'] = "27 91 66",
	['C'] = "27 91 67",
	['D'] = "27 91 68",
};

static const char *const special_key_names[] = {
	[ASCII_ESC] = "esc",
	['2'] = "ins",
	['3'] = "del",
	['A'] = "up",
	['B'] = "down",
	['C'] = "right",
	['D'] = "left",
};

static void print_keypress(struct keypress key) {
	if (key.is_ctrl) {
		printf("ctrl + ");
	}
	if (key.is_alt) {
		printf("alt + ");
	}

	if (key.is_fn) {
		printf("f%d", key.base_key);
	} else if (key.is_special) {
		printf("%s", special_key_names[key.base_key]);
	} else if (key.base_key == ' ') {
		printf("space");
	} else if (key.base_key == '\t') {
		printf("tab");
	} else if (key.base_key == '\n') {
		printf("ret");
	} else if (key.base_key == ASCII_DEL) {
		printf("bkspc");
	} else {
		printf("%c", key.base_key);
	}

	printf("\r\n");
	// if (key.is_alt) {
	// 	printf("%d ", ASCII_ESC);
	// }
	
	// if (key.is_special) {
	// 	printf("%s\r\n", special_key_codes[key.base_key]);
	// } else {
	// 	printf("%d\r\n", key.base_key);
	// }
}

int main(void) {
	struct window window = {0};
	if (!window_initialize(&window)) {
		fprintf(stderr, "Error initializing window.");
		goto error1;
	}

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
