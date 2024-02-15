#include <stdio.h>
#include <ncurses.h>

int main(void) {
	initscr();
	raw();
	keypad(stdscr, TRUE);
	noecho();

    printw("Press Shift+q to quit.\nPress Shift+c to clear the screen.\n");
	char ch = getch();
    clear();
    refresh();

	do {
		if (ch == 'C') {
			clear();
			refresh();
		} else if (ch == '\n') {
			printw("newline\n");
		} else {
			printw("name: %s   value: %d\n", keyname(ch), ch);
		}
		ch = getch();
	} while (ch != 'Q');

	endwin();
	return 0;
}
