#include "image.h"

#include <stdint.h>
#include <stdio.h>

int main(void) {
    uint8_t input[8192];
    size_t size = fread(input, 1, sizeof(input), stdin);

    if (ferror(stdin)) {
        fputs("input error\n", stderr);
        return 2;
    }

    puts(parse_image_message(input, size) ? "accepted" : "rejected");
    return 0;
}
