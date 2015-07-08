CC = gcc
CFLAGS = -Wall -Os -fno-stack-protector -nostdlib
CPPFLAGS = -iquote ../include

.PHONY: all clean

all: utils.o syscalls.o

clean:
	rm -f *.o *~
