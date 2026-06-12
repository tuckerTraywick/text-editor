#include <stddef.h>
#include <stdbool.h>
#include "ui.h"

struct character_format {
	char foreground_color : 8;
	char background_color : 8;
	bool bold : 1;
	bool italic : 1;
	bool highlight : 1;
};

struct window {
	char *text; // Points to a list. Not null terminated.
	struct character_format *format; // The format for each character of the window. Has the same dimensions as `text`.
};
