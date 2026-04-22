#include <stdint.h>
#include <stdio.h>
#include <ncurses.h>
#include "buffer.h"

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
	return 0;
}
