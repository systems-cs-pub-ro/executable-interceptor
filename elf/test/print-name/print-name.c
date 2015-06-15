#include <stddef.h>
#include <sys/mman.h>
#include "interceptor.h"

#define STDERR_FILENO 2

static int my_write(int fd, const void *buf, size_t size)
{
	int rc;

	asm("int     $0x80\n"
	    : "=a" (rc)
	    : "a" (0x4),
		  "b" (fd),
	      "c" (buf),
	      "d" (size));

	return rc;
}

static void *my_mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset)
{
	void *ret_addr;

    asm("int     $0x80\n"
		: "=a" (ret_addr)
		: "a" (0xc0),
		  "b" (addr),
		  "c" (length),
		  "d" (prot),
		  "S" (flags),
		  "D" (fd));

    return ret_addr;
}

static size_t my_strlen(const char *s)
{
	const char *p;

	for (p = s; *p != '\0'; p++)
		;

	return p - s;
}

int init(void *data)
{
	void **data_ptr = data;
	*data_ptr = my_mmap(NULL,
					 	4096,
						PROT_READ | PROT_WRITE,
						MAP_PRIVATE | MAP_ANONYMOUS,
						-1,
						0);
	return 0;
}

int interceptor(void *data, const char *fname, const int fid)
{
	const char nl = '\n';

	my_write(STDERR_FILENO, fname, my_strlen(fname));
	my_write(STDERR_FILENO, &nl, 1);

	return 0;
}
