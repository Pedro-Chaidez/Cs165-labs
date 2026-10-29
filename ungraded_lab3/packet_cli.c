#include "packet.h"

#include <stdint.h>
#include <stdio.h>

int main(void) {
    uint8_t input[4096];
    size_t size = fread(input, 1, sizeof(input), stdin);

    if (ferror(stdin)) {
        fputs("input error\n", stderr);
        return 2;
    }

    puts(parse_packet(input, size) ? "accepted" : "rejected");
    return 0;
}
