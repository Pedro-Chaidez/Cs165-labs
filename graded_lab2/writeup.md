# 1. Format String Vulnerability in greet()

* **The Bug and Its Danger:** The original code uses printf(buf);, which evaluates user input as a format string. Attackers can input format specifiers (like %p) to dump stack values and leak the randomized stack canary needed to bypass stack protections.


* **The Fix:** Changed the output call to printf("%s", buf);.


* **Why it stops the bug:** Hardcoding the %s format specifier explicitly defines the user's input as a string literal data rather than executable instructions. This forces printf to safely print the raw characters without attempting to read from the stack.



# 2. Buffer Overflow Vulnerability in check_request()

* **The Bug and Its Danger:** The program uses memcpy(note, input, len); to copy up to 512 bytes of user input into a fixed 48-byte buffer with zero boundary checks. An attacker can supply an oversized length to overflow the buffer, smash the stack to overwrite the canary and return address, and redirect execution flow to the win() function.


* **The Fix:** Added a mandatory bounds check immediately before the memory copy operation:

if (len > sizeof(note)) {
    len = sizeof(note); 
}
memcpy(note, input, len);

* **Why it closes the bug:** By clamping the len variable to the maximum capacity of sizeof(note) (48 bytes), memcpy will never write out of bounds. The program can still safely process large inputs by truncating them, preserving the integrity of the stack canary and the saved return address.