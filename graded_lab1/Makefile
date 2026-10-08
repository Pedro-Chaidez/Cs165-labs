CC      = gcc
CFLAGS  = -g -O0 -fsanitize=address -fno-omit-frame-pointer -Wall
TARGET  = recman
SRC     = recman.c

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC)

# build without the sanitizer (closer to the course VM's default build)
plain: $(SRC)
	$(CC) -g -O0 -Wall -o $(TARGET) $(SRC)

clean:
	rm -f $(TARGET)

# bundle your submission: patched source, triggers, and writeup
tar:
	tar czf lab1-submission.tgz recman.c triggers writeup.md
.PHONY: all plain clean tar
