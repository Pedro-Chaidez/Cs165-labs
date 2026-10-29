/* Provided libFuzzer harness for the ungraded demonstration. */
#include "packet.h"

#include <stddef.h>
#include <stdint.h>

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    (void)parse_packet(data, size);
    return 0;
}
