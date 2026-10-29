# 1. Format String Vulnerability in greet()

* **The Bug and Its Danger:** The original code uses printf(buf);, which evaluates user input as a format string. Attackers can input format specifiers (like %p) to dump stack values and leak the randomized stack canary needed to bypass stack protections.


* **The Fix:** Changed the output call to printf("%s", buf);.


* **Why it stops the bug:** Hardcoding the %s format specifier explicitly defines the user's input as a string literal data rather than executable instructions. This forces printf to safely print the raw characters without attempting to read from the stack.



# 2. Buffer Overflow Vulnerability in check_request()

* **The Bug and Its Danger:** The program uses memcpy(note, input, len); to copy up to 512 bytes of user input into a fixed 48-byte buffer with zero boundary checks. An attacker can supply an oversized length to overflow the buffer, smash the stack to overwrite the canary and return address, and redirect execution flow to the win() function.


* **The Fix:** Added a mandatory bounds check immediately before the memory copy operation:
```c
if (len > sizeof(note)) {
    len = sizeof(note); 
}
memcpy(note, input, len);
```
* **Why it closes the bug:** By clamping the len variable to the maximum capacity of sizeof(note) (48 bytes), memcpy will never write out of bounds. The program can still safely process large inputs by truncating them, preserving the integrity of the stack canary and the saved return address.

# 3. The Four Values and Discovery

* **WIN (0x401296):** The static, non-PIE address of win(), found via print &win.
* **OFF_CANARY (56):** The offset from the note buffer (0x7fffffffd810) to the canary (0x7fffffffd848), calculated as 0x38 (56 bytes).
* **OFF_RETADDR (72):** The offset from note to the saved return address ($rbp+8). Calculated via (char*)($rbp+8) - (char*)note.
* **LEAK_INDEX (25):** Supplying %25$p in phase 1 successfully leaked the randomized, 8-byte canary ending in 00.

**Debugger Transcript:**

```gdb
(gdb) print &win
$1 = (void (*)(void)) 0x401296 <win>
(gdb) break check_request
(gdb) run < tests/accept.bin
(gdb) print &note
$2 = (char (*)[48]) 0x7fffffffd810
(gdb) print $rbp
$3 = (void *) 0x7fffffffd850
(gdb) print (char*)($rbp+8) - (char*)note
$4 = 72
(gdb) x/16gx note
...
0x7fffffffd840: 0x0000000000403e00      0x00007ffff7ffd000
...

```

```bash
pedro@Pedro-Laptop:~/Cs165-labs/graded_lab2$ ./vault %25$p
vault build adc3ee5f
hello, 0xb45aa04f08219f00

```

# 4. Defeating the Stack Protector

The stack protector places a randomized canary before the saved return address to detect overflows. We defeat this by first exploiting the format string bug to leak the live canary value. We then construct our buffer overflow payload to write this exact leaked value back into the canary slot. Because the value is unaltered, the security check passes, allowing the program to safely jump to our overwritten return address (WIN).