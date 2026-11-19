/*
 * CS 165 Ungraded Lab 4: intentionally vulnerable note writer.
 *
 * Security policy:
 *   - update a regular file directly inside work/inbox;
 *   - do not follow symbolic links; and
 *   - never modify work/gradebook.txt.
 *
 * The --pause option is a deterministic teaching hook. It exposes an existing
 * check/use window; it is not the cause of the vulnerability.
 */
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#define INBOX_DIR "work/inbox"

static void usage(const char *program) {
    fprintf(stderr, "usage: %s [--pause] NAME MESSAGE\n", program);
}

static int valid_name(const char *name) {
    return name[0] != '\0' && strcmp(name, ".") != 0 &&
           strcmp(name, "..") != 0 && strchr(name, '/') == NULL;
}

static void announce_and_pause(const char *name, int should_pause) {
    printf("CHECKED %s\n", name);
    fflush(stdout);

    if (should_pause) {
        char byte;
        while (read(STDIN_FILENO, &byte, 1) < 0 && errno == EINTR) {
        }
    }
}

static int write_all(int fd, const char *data, size_t length) {
    size_t offset = 0;
    while (offset < length) {
        ssize_t written = write(fd, data + offset, length - offset);
        if (written < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        if (written == 0) {
            errno = EIO;
            return -1;
        }
        offset += (size_t)written;
    }
    return 0;
}

static int update_note(const char *name, const char *message, int should_pause) {
    char path[512];
    struct stat checked;

    int path_length = snprintf(path, sizeof(path), "%s/%s", INBOX_DIR, name);
    if (path_length < 0 || (size_t)path_length >= sizeof(path)) {
        fprintf(stderr, "note name is too long\n");
        return -1;
    }

    /*
     * INTENTIONAL BUG: lstat() validates the object currently named by path,
     * but open() later resolves the pathname again. An attacker can replace
     * the directory entry between these calls.
     */
    if (lstat(path, &checked) < 0) {
        perror("lstat");
        return -1;
    }
    if (!S_ISREG(checked.st_mode)) {
        fprintf(stderr, "refusing non-regular note\n");
        return -1;
    }

    announce_and_pause(name, should_pause);

    int fd = open(path, O_WRONLY | O_TRUNC | O_CLOEXEC);
    if (fd < 0) {
        perror("open");
        return -1;
    }

    int result = 0;
    if (write_all(fd, message, strlen(message)) < 0 ||
        write_all(fd, "\n", 1) < 0) {
        perror("write");
        result = -1;
    }
    if (close(fd) < 0) {
        perror("close");
        result = -1;
    }
    return result;
}

int main(int argc, char **argv) {
    int should_pause = 0;
    int argument = 1;

    if (argc > 1 && strcmp(argv[1], "--pause") == 0) {
        should_pause = 1;
        argument++;
    }
    if (argc - argument != 2) {
        usage(argv[0]);
        return 2;
    }
    if (!valid_name(argv[argument])) {
        fprintf(stderr, "invalid note name\n");
        return 2;
    }

    return update_note(argv[argument], argv[argument + 1], should_pause) == 0
               ? EXIT_SUCCESS
               : EXIT_FAILURE;
}

