#include <unistd.h>
#include <sys/syscall.h>

#if defined(__x86_64__)

int e_write(int fd, const void *buf, size_t count)
{
	int rc;

	asm volatile("syscall\n"
				 : "=a" (rc)
				 : "a" (0x1), "D" (fd), "S" (buf), "d" (count)
				 : "cc", "rcx", "r11", "memory");

	return rc;
}

#elif defined(__i386__)

int e_write(int fd, const void *buf, size_t count)
{
	int rc;

	asm volatile("int	$0x80\n"
				 : "=a" (rc)
				 : "a" (0x4), "b" (fd), "c" (buf), "d" (count)
				 : "cc", "edi", "esi", "memory");

	return rc;
}

void *e_mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset)
{
	void *ret_addr;

    asm volatile("int	$0x80\n"
    			 : "=a" (ret_addr)
				 : "a" (0xc0), "b" (addr), "c" (length), "d" (prot), "S" (flags), "D" (fd)
				 : "cc", "memory");

    return ret_addr;
}

#endif
