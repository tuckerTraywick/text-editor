#include <ncurses.h>
#include "editor.h"

void setup_ncurses(void) {
	initscr();
	raw();
	noecho();
	keypad(stdscr, TRUE);
	set_escdelay(0);
}

void teardown_ncurses(void) {
	endwin();
}

int main(void) {
	setup_ncurses();
	teardown_ncurses();
	return 0;
}
