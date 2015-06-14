Introduction: what is elf_injector.py?
----------------------------------------

Simple application that injects a given library function interceptor
into an ELF executable.

Pre-requisites
--------------

In order to use this script you have to download the [pyelftools
library](https://github.com/eliben/pyelftools) and put it into the
`PYTHONPATH` environment variable.

    $ export PYTHONPATH=<path-to-pyelftools-library>:$PYTHONPATH

How to use it?
--------------

    $ ./elf_injector.py elf-file interceptor-obj

*elf-file* is the ELF executable file and *intcerp-obj* is the
object file containing the definitions of the `interceptor`
and `init` functions whose prototypes are declared in *interceptor.h*.

Examples
--------

You can use the code from the *test* directory that defines a simple
program and an interceptor that displays the intercepted function's name
to stderr via a write syscall.

Limitations
-----------

Right now only i386 ELF executables are supported.  The program is
not supposed to run on a 64-bit system.  The result is undefined,
probably a segmentation fault will arise.  x86-64 and ARM architectures will
be supported in the future.
