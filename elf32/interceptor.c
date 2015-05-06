#include <stddef.h>
#include "interceptor.h"

int write(int fd, const void *buf, size_t size)
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

int interceptor(const int fid)
{
	write(1, &fid, sizeof(int));
	return 0;
}
