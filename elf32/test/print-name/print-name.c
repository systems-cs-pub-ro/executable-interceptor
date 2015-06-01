#include <stddef.h>
#include "interceptor.h"

#define STDOUT_FILENO 1

static int write(int fd, const void *buf, size_t size)
{
	int rc;

	asm("movl    $0x04, %%eax\n"
	    "int     $0x80\n"
	    : "=a" (rc)
	    : "b" (fd),
	      "c" (buf),
	      "d" (size));

	return rc;
}

static size_t strlen(const char *s)
{
	const char *p;

	for (p = s; *p != '\0'; p++)
		;

	return p - s;
}

int interceptor(const char *const fname, const int fid)
{
	char nl = '\n';

	write(STDOUT_FILENO, fname, strlen(fname));
	write(STDOUT_FILENO, &nl, 1);

	return 0;
}
