#include <stdio.h>
#include "ncurses.h"

int main(void) {
	initscr();
	raw();
	keypad(stdscr, TRUE);
	nonl();
	noecho();

    printw("Press Shift+q to quit.\nPress Shift+c to clear the screen.\n");
	char ch = getch();
    clear();
    refresh();

	do {
		printw("name: %s   value: %d\n", keyname(ch), ch);
		if (ch == 'C') {
			clear();
			refresh();
		}
		ch = getch();
	} while (ch != 'Q');

	endwin();
	return 0;
}
