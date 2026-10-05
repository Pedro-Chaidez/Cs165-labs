#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void greet(const char *name) {
    char buf[16];                 
    strcpy(buf, name);            
    printf("Hello, %s!\n", buf);
}

static void note_demo(void) {
    char *note = malloc(32);
    strcpy(note, "remember to free me");
                    
    printf("note = %s\n", note); 
		free(note);   //was on line 14, moved to line 16 to avoid memory leak
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s greet <name> | note\n", argv[0]);
        return 2;
    }
    if (strcmp(argv[1], "greet") == 0 && argc >= 3) greet(argv[2]);
    else if (strcmp(argv[1], "note") == 0)          note_demo();
    else fprintf(stderr, "unknown subcommand\n");
    return 0;
}
