/* CS 165 Lab 2 (ungraded prep): Controlled Buffer Overflow
 * Build 4a44dc15.  This program is INTENTIONALLY vulnerable, for teaching only.
 *
 * vault reads a binary "request" from stdin and checks it in check_request().
 * That function has one deliberate stack-buffer-overflow bug.  It also has a
 * harmless win() function that prints a build-specific token but is never
 * called by the program.  The exercise is to reach win() by overflowing the
 * buffer and overwriting the saved return address.
 */
#include <stdio.h>
#include <string.h>

#define NOTE_SIZE 56
#define PAD_WORDS 1
#define MAX_REQUEST 512

/* The target.  'used' keeps it in the binary even though nothing calls it. */
static void win(void) __attribute__((noinline, used));

static void win(void) {
    puts("LAB2-WIN:vault-4a44dc15");
    fflush(stdout);
}

static void check_request(const unsigned char *input, size_t len) {
    volatile unsigned long padding[PAD_WORDS];
    char note[NOTE_SIZE];

    memset((void *)padding, 0, sizeof(padding));
    if (len < 4) { puts("(malformed request)"); return; }

    memcpy(note, input, len);          /* BUG: len is unchecked, note is 56 bytes */

    if (memcmp(note, "OPEN", 4) == 0) puts("request accepted");
    else puts("request rejected");
}

int main(void) {
    unsigned char input[MAX_REQUEST];
    size_t len = fread(input, 1, sizeof(input), stdin);
    printf("vault build 4a44dc15\n");
    check_request(input, len);
    return 0;
}
