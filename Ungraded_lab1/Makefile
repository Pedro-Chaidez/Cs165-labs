CC     = gcc
CFLAGS = -g -O0 -fsanitize=address -fno-omit-frame-pointer -Wall

all: demo practice

demo: demo.c
	$(CC) $(CFLAGS) -o demo demo.c

practice: practice.c
	$(CC) $(CFLAGS) -o practice practice.c

# without the sanitizer (to show undefined behavior is unpredictable)
plain:
	$(CC) -g -O0 -Wall -o demo demo.c
	$(CC) -g -O0 -Wall -o practice practice.c

clean:
	rm -f demo practice
.PHONY: all plain clean
