CC = gcc
AS = as
CFLAGS = -m32 -Wall -O0
ASFLAGS = --32

.PHONY: all clean

all: run.o

run.o: run_interceptor.o interceptor.o
	ld -e 0 -melf_i386 $^ -o $@

clean:
	rm -f *.o *~
