/*
 * CS 165 Graded Lab 3: image-message parser.
 *
 * Example message:
 *   IMG2;FMT=GRAY;OP=INFO;AUTH=NO;W=2;H=3;DATA=abcdef;
 *
 * Fields may appear in any order after the IMG2 header. Each field ends with
 * a semicolon. The parser accepts three formats (GRAY, RGB, and META) and
 * three operations (INFO, CHECK, and THUMB).
 */
#include "image.h"

#include <ctype.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

struct slice {
    const uint8_t *ptr;
    size_t len;
    int found;
};

static volatile uint32_t observation_sink;

static int slice_equals(struct slice value, const char *text) {
    size_t text_len = strlen(text);
    return value.found && value.len == text_len &&
           memcmp(value.ptr, text, text_len) == 0;
}

static int slice_starts_with(struct slice value, const char *text) {
    size_t text_len = strlen(text);
    return value.found && value.len >= text_len &&
           memcmp(value.ptr, text, text_len) == 0;
}

static struct slice find_field(const uint8_t *data, size_t size,
                               const char *key) {
    struct slice missing = {NULL, 0, 0};
    size_t key_len = strlen(key);

    for (size_t start = 0; start < size;) {
        size_t end = start;
        while (end < size && data[end] != ';') end++;

        if (end - start > key_len + 1 &&
            memcmp(data + start, key, key_len) == 0 &&
            data[start + key_len] == '=') {
            struct slice result = {
                data + start + key_len + 1,
                end - start - key_len - 1,
                1,
            };
            return result;
        }

        if (end == size) break;
        start = end + 1;
    }

    return missing;
}

static int parse_dimension(struct slice text, size_t *result) {
    size_t value = 0;

    if (!text.found || text.len == 0) return 0;

    for (size_t i = 0; i < text.len; i++) {
        if (!isdigit((unsigned char)text.ptr[i])) return 0;
        value = value * 10 + (size_t)(text.ptr[i] - '0');
        if (value > 64) return 0;
    }

    if (value == 0) return 0;
    *result = value;
    return 1;
}

static int multiply_size(size_t left, size_t right, size_t *result) {
    if (right != 0 && left > SIZE_MAX / right) return 0;
    *result = left * right;
    return 1;
}

static int format_channels(struct slice format, size_t *channels) {
    if (slice_equals(format, "GRAY")) {
        *channels = 1;
        observation_sink ^= 0x01U;
        return 1;
    }

    if (slice_equals(format, "RGB")) {
        *channels = 3;
        observation_sink ^= 0x02U;
        return 1;
    }

    if (slice_equals(format, "META")) {
        *channels = 1;
        observation_sink ^= 0x04U;
        return 1;
    }

    return 0;
}

static int create_thumbnail(size_t width, size_t height, size_t channels,
                            struct slice payload) {
    size_t pixel_count = 0;
    size_t bytes_needed = 0;

    if (!multiply_size(width, height, &pixel_count) ||
        !multiply_size(pixel_count, channels, &bytes_needed) ||
        !payload.found || payload.len < bytes_needed) {
        return 0;
    }

    uint8_t allocation_size = (uint8_t)bytes_needed;
    uint8_t *thumbnail = malloc(allocation_size);
    if (thumbnail == NULL) return 0;

    memcpy(thumbnail, payload.ptr, bytes_needed);
    observation_sink ^= thumbnail[0];
    observation_sink ^= thumbnail[bytes_needed - 1];
    free(thumbnail);
    return 1;
}

int parse_image_message(const uint8_t *data, size_t size) {
    static const uint8_t header[] = {'I', 'M', 'G', '2', ';'};

    if (size < sizeof(header) || memcmp(data, header, sizeof(header)) != 0) {
        return 0;
    }

    struct slice format = find_field(data, size, "FMT");
    struct slice operation = find_field(data, size, "OP");
    struct slice auth = find_field(data, size, "AUTH");
    struct slice width_text = find_field(data, size, "W");
    struct slice height_text = find_field(data, size, "H");
    struct slice payload = find_field(data, size, "DATA");

    size_t width = 0;
    size_t height = 0;
    size_t channels = 0;
    size_t pixel_count = 0;
    size_t bytes_needed = 0;

    if (!format_channels(format, &channels) ||
        !parse_dimension(width_text, &width) ||
        !parse_dimension(height_text, &height) ||
        !multiply_size(width, height, &pixel_count) ||
        !multiply_size(pixel_count, channels, &bytes_needed)) {
        return 0;
    }

    if (slice_equals(operation, "INFO")) {
        observation_sink ^= (uint32_t)(width + height + channels);
        return 1;
    }

    if (slice_equals(operation, "CHECK")) {
        observation_sink ^= 0x10U;

        if (slice_equals(format, "META")) {
            if (slice_starts_with(payload, "CS165:")) {
                observation_sink ^= 0x20U;
                return 1;
            }
            return 0;
        }

        return payload.found && payload.len == bytes_needed;
    }

    if (slice_equals(operation, "THUMB") &&
        slice_equals(auth, "YES") &&
        !slice_equals(format, "META")) {
        observation_sink ^= 0x40U;
        return create_thumbnail(width, height, channels, payload);
    }

    return 0;
}
