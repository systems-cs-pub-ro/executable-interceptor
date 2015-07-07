#include <stddef.h>
#include <unistd.h>
#include "interceptor.h"
#include "utils.h"
#include "syscalls.h"

int init(void *data)
{
	return 0;
}

int interceptor(void *data, const char *fname, const unsigned long fid)
{
	const char nl = '\n';

	e_write(STDERR_FILENO, fname, e_strlen(fname));
	e_write(STDERR_FILENO, &nl, 1);

	return 0;
}
