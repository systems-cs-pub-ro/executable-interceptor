Test example
------------

Print the intercepted function ID to stdout via a write syscall.

Directory content
-----------------

* **hellob.c**           Code whose functions will be intercepted
* **print_id_intcerp.s** Interceptor code that prints the ID
* **Makefile**           Compiles/assembles the first two files
* **extract-code.sh**    Extracts the code bytes from an object file

How to run the example
----------------------

1. Compile the code:

    > make

You will see two result files: hellob, the binary ELF, and
print_id_intcerp.o, the object file representing the interceptor.

2. Extract the actual code bytes of the interceptor:

    > ./extract-code.sh print_id_intcerp.o print_id_intcerp.hex

3. Run the injector:

    > ./elf32_injector.py hellob print_id_intcerp.hex

4. Run the executable and observe the first 3 printed words (the
output is in binary form).  These represent the IDs of the intercepted
functions.

    > ./hellob | hexdump -C

5. Clean up:

    > make clean
