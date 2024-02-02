#include <stdio.h>
#include "ncurses.h"

int main(void) {
	initscr();
	raw();
	keypad(stdscr, TRUE);
	noecho();

	endwin();
	return 0;
}
