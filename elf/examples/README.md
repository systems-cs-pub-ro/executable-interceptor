Test example
------------

Print the intercepted function's name to stdout via a write syscall.

Directory content
-----------------

* **hellob.c** Program whose functions will be intercepted
* **print-name/print-name.c** Interceptor code that prints function's name

How to run the example
----------------------

1. Compile the program (*hellob.c*) and the interceptor:

    $ make
    $ cd print-name && make

2. Run the injector:

    $ ./elf_injector.py hellob print-name.o

3. Run the executable and observe the names of the intercepted functions:

    $ ./hellob
