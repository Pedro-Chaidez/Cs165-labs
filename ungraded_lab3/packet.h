#ifndef CS165_PACKET_H
#define CS165_PACKET_H

#include <stddef.h>
#include <stdint.h>

/* Return 1 for a recognized packet and 0 for a rejected packet. */
int parse_packet(const uint8_t *data, size_t size);

#endif
