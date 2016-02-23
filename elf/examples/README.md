Test example
------------
Print the name of each intercepted function to stdout via a write syscall.

Directory content
-----------------
* **hellob.c** Program whose functions will be intercepted
* **print-name/print-name.c** Interceptor code that prints the name of each intercepted function

How to run the example
----------------------
1. Compile the program and the interceptor:
```sh
$ make
$ cd print-name && make
```

2. Instrument the executable:
```sh
$ ./elf_injector.py hellob print-name.o
```

3. Run the executable and observe the name of the intercepted functions:
```sh
$ ./hellob
```
