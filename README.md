Introduction: what is executable-interceptor?
---------------------------------------------
Library function interceptor for multiple executable formats (ELF, PE, Mach-O) and architectures (i386, x86--64, ARM).  Basically, the application injects a given code (i.e. the interceptor) into some executable.  The code will be executed whenever a call from inside the executable is initiated and has access to the name of the function that is being called and its parameters as well.

**Limitation:** The application is under development, so undefined behavior may appear.  Right now only ELF executables are supported (i386, x86--64 and ARM).  The program is not supposed to handle other executable formats.  PE and Mach-O will be supported in the future.

Pre-requisites
--------------
In order to use this script you have to download the [pyelftools library](https://github.com/eliben/pyelftools) and put it into the `PYTHONPATH` environment variable.

```sh
$ export PYTHONPATH=<path-to-pyelftools-library>:$PYTHONPATH
```

How to use it?
--------------
```sh
$ ./elfpatcher.py elf-file interceptor-obj
```

where *elf-file* is the ELF executable file and *intcerp-obj* is the object file containing the definitions of the `interceptor` and `init` functions whose prototypes are declared in *interceptor.h*.  As the name suggests, these functions are executed at the beginning of the corresponding process and at each external library call respectively.

Examples
--------
You can use the code from the *examples* directory that defines a simple program and an interceptor that displays the name of each function it intercepts, to stderr via a write syscall.