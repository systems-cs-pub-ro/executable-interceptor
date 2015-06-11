Test example
------------

Print the intercepted function's ID or name to stdout via a write
syscall.

Directory content
-----------------

* **hellob.c** Program whose functions will be intercepted
* **print-id/print-id.s** Interceptor code that prints the function's ID
* **print-name/print-name.c** Interceptor code that prints the function's name

How to run the example which prints the ID
------------------------------------------

1. Compile the program (*hellob.c*) and the interceptor:

    > make
    > cd print-id && make

2. Extract the actual code bytes of the interceptor:

    > ./extract-code.sh print-id.o print-id.hex

3. Run the injector:

    > ./elf32_injector.py --direct hellob print-id.hex

4. Run the executable and observe the first 4 printed words (the
output is in binary form).  These represent the IDs of the intercepted
functions.

    > ./hellob | hexdump -C

How to run the example which prints the name
--------------------------------------------

1. Compile the program (*hellob.c*) and the interceptor:

    > make
    > cd print-name && make

2. Run the injector:

    > ./elf32_injector.py hellob print-name.o

3. Run the executable and observe the names of the intercepted
functions:

    > ./hellob
