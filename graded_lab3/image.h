#ifndef CS165_IMAGE_H
#define CS165_IMAGE_H

#include <stddef.h>
#include <stdint.h>

/* Return 1 for an accepted image message and 0 for a rejected message. */
int parse_image_message(const uint8_t *data, size_t size);

#endif
