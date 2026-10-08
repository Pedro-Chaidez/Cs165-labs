CS 165 Lab 1: Bug Analysis Writeup

Bug 1: Stack Buffer Overflow (CWE 121)

A stack buffer overflow occurs when a program writes more data to a stack-allocated buffer than it is designed to hold. In cmd_name, the line strcpy(tmp, arg); blindly copies user input into the char tmp[NAMELEN] array. My script triggers this by passing a string of 52 characters, which overflows the build-specific NAMELEN of 40 bytes, corrupting adjacent stack memory.

Bug 2: Heap Buffer Overflow (CWE 122)

A heap buffer overflow happens when data is written past the boundary of a dynamically allocated heap space. In cmd_app, the line strcpy(r->str + r->slen, arg); appends text without allocating more memory to the existing string buffer. My script triggers this because it appends the letter "h" to the string "hello", writing beyond the original 6-byte heap allocation (5 letters + 1 null terminator).

Bug 3: Use After Free (CWE 416)

Use-after-free occurs when a program dereferences a pointer to a memory location that has already been deallocated. This stems from cmd_del freeing a record without nullifying links to it from other records. My script triggers this by linking record 2 to record 1, deleting record 1, and then calling show 2, which forces cmd_show to read the freed memory via r->link->name.

Bug 4: Integer Overflow to Heap Overflow (CWE 190 / CWE 122)

An integer overflow happens when arithmetic creates a value too large for its data type, which in this case leads to an undersized allocation and a heap overflow. In cmd_grow, the calculation unsigned int bytes = (unsigned int)n * sizeof(int); lacks bounds checking. My script triggers this by passing 10000000000, which overflows the 32-bit integer limit, resulting in a tiny memory allocation that is immediately overrun by the subsequent for loop.

Bug 5: NULL Pointer Dereference (CWE 476)

A NULL pointer dereference happens when a program attempts to read from memory using a pointer that is set to NULL. In cmd_show, the line printf("id=%d name=%s\n", r->id, r->name); unconditionally accesses properties of the pointer r. My script triggers a crash by simply running show 1 before record 1 is ever created, causing lookup(1) to return NULL which cmd_show immediately tries to dereference.