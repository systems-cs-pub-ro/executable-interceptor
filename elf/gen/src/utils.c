#include <stddef.h>

size_t e_strlen(const char *s)
{
	const char *p;

	for (p = s; *p != '\0'; p++)
		;

	return p - s;
}
