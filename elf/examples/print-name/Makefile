CC = gcc
CFLAGS = -Wall -Os -fno-stack-protector -nostdlib
CPPFLAGS = -iquote ../../gen/include

.PHONY: all clean

all: print-name.o

clean:
	rm -f *.o *~
