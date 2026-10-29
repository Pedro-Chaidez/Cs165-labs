/*
 * CS 165 Ungraded Lab 3: intentionally vulnerable packet parser.
 *
 * Packet example:
 *   PKT1;TYPE=TEXT;ACTION=SHOW;AUTH=NO;DATA=hello;
 *
 * This file contains one deliberate heap overflow for a local fuzzing lab.
 */
#include "packet.h"

#include <ctype.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define SLOT_CAPACITY 16

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

static void observe_number(struct slice data) {
    unsigned long value = 0;
    if (!data.found || data.len == 0) return;

    for (size_t i = 0; i < data.len; i++) {
        if (!isdigit((unsigned char)data.ptr[i])) return;
        value = value * 10 + (unsigned long)(data.ptr[i] - '0');
        if (value > 1000000UL) break;
    }

    if (value == 165) observation_sink ^= 0x165U;
    if (value > 1000) observation_sink ^= 0x1000U;
}

int parse_packet(const uint8_t *data, size_t size) {
    static const uint8_t header[] = {'P', 'K', 'T', '1', ';'};

    if (size < sizeof(header) || memcmp(data, header, sizeof(header)) != 0) {
        return 0;
    }

    struct slice type = find_field(data, size, "TYPE");
    struct slice action = find_field(data, size, "ACTION");
    struct slice auth = find_field(data, size, "AUTH");
    struct slice payload = find_field(data, size, "DATA");

    if (slice_equals(type, "TEXT")) {
        observation_sink ^= 0x01U;
    } else if (slice_equals(type, "NUMBER")) {
        observation_sink ^= 0x02U;
        observe_number(payload);
    } else if (slice_equals(type, "META")) {
        observation_sink ^= 0x04U;
        if (payload.found && payload.len >= 5 &&
            memcmp(payload.ptr, "CS165", 5) == 0) {
            observation_sink ^= 0x08U;
        }
    } else {
        return 0;
    }

    if (slice_equals(action, "SHOW")) {
        observation_sink ^= 0x10U;
        return payload.found;
    }

    if (slice_equals(action, "COUNT")) {
        observation_sink ^= (uint32_t)payload.len;
        return payload.found;
    }

    if (slice_equals(action, "STORE") &&
        slice_equals(auth, "YES") &&
        slice_equals(type, "TEXT") && payload.found) {
        observation_sink ^= 0x20U;

        char *slot = malloc(SLOT_CAPACITY);
        if (slot == NULL) return 0;

        /* INTENTIONAL BUG: payload.len is not checked against SLOT_CAPACITY. */
        memcpy(slot, payload.ptr, payload.len);

        if (payload.len > 0) observation_sink ^= (uint8_t)slot[0];
        free(slot);
        return 1;
    }

    return 0;
}
