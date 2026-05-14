#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <ncurses.h>
#include "buffer.h"

void ncurses_setup(void) {
	initscr();
	raw();
	noecho();
	keypad(stdscr, true);
	set_escdelay(0);
}

void ncurses_teardown(void) {
	endwin();
}

// int main(void) {
// 	struct window *window = window_create("hello", 800, 600);
// 	if (!window) {
// 		return 1;
// 	}

// 	widget_id ui = row_begin(window);
// 		label(window, "hi");
// 		button_id button_a = button(window, "button a");
// 		column_begin(window);
// 			label(window, "bye");
// 			button_id button_b = button(window, "button b");
// 		column(window);
// 	row_end(window);

// 	while (window->keep_running) {
// 		draw();
// 		update();

// 		if (button_is_pressed(window, button_a)) {
// 			widget_destroy(window, ui);
// 			rebuild_ui();
// 		}

// 		if (button_is_pressed(window, button_b)) {

// 		}
// 	}
// 	return 0;
// }

int main(void) {
	return 0;
}
