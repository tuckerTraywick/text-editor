#include <stdio.h>
#include "ncurses.h"

int main(void) {
	initscr();
	raw();
	keypad(stdscr, TRUE);
	nonl();
	noecho();

	char ch;
	do {
		ch = getch();
		printw("name: %s   value: %d\n", keyname(ch), ch);
		if (ch == 'C') {
			clear();
			refresh();
		}
	} while (ch != 'q');

	endwin();
	return 0;
}
