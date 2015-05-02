Introduction: what is elf32_injector.py?
----------------------------------------

Simple application that injects a given library function interceptor
into an ELF32 executable.

Pre-requisites
--------------

In order to use this script you have to download the [pyelftools
library](https://github.com/eliben/pyelftools) and put it into the
`PYTHONPATH` environment variable.

    > export PYTHONPATH=<path-to-pyelftools-library>:$PYTHONPATH

How to use it?
--------------

    > ./elf32_injector.py elf32-file intcerp-file

*elf32-file* is the ELF32 executable file and *intcerp-file* contains
the binary code to be used as interceptor.

As an example, you can use the code from the *test* directory that
prints the intercepted function ID to stdout via a write syscall.

Limitations
-----------

Right now only 32-bit ELF executables are supported.  The program is
not supposed to run on a 64-bit system.  The result is undefined,
probably a segmentation fault will arise.  64-bit ELF executables will
be supported in the future.
