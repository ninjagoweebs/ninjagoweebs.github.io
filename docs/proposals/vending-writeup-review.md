# Presentation review: Awakened Vending Machine writeup

This is a review of how the original `NOTES.md` was turned into a published post.
It is intentionally separate from the notes so the raw notes stay raw.

Published post:
`site/_posts/2026-11-27-tryhards-awakened-vending-machine.md`

## What worked well in the original notes

- The win function was identified immediately.
- `checksec` output was included and interpreted.
- The format string test was documented with real output.
- The source code was quoted next to the observation.
- The debugging session showed the stack layout and the crash.
- The offset was found with a cyclic pattern.
- The final flag was already censored.

That is a strong base. The main problem was presentation, not content.

## What was changed for the published post

1. **Added a challenge overview table** so readers can see the platform, binary,
   protections, and key bug before the details.
2. **Added a short TL;DR** for readers who want the solution quickly.
3. **Split the writeup into clear stages**:
   - hidden win function,
   - protections,
   - program behavior,
   - format string lead,
   - source analysis,
   - stack overflow,
   - debugging,
   - offset,
   - flag.
4. **Converted raw output into fenced code blocks** with `text`, `c`, and shell
   languages.
5. **Collapsed the long stack dumps** with `<details>` so the page stays
   readable.
6. **Kept the important crash lines visible** (RIP, RBP, backtrace) before the
   collapsed full dump.
7. **Added a payload layout diagram**:

   ```text
   [ 168 bytes of padding ] [ address of maintenance_hatch() ]
   ```

8. **Attached the full source and disassembly** instead of pasting 16 KB of
   assembly into the post.
9. **Added a “Lessons learned” section** so the post ends with transferable
   takeaways.
10. **Changed the path** `folder-kuwin` to `ctf` in the post and in
    `NOTES.md`.
11. **Lightly copyedited** obvious typos and unclear sentences without changing
    the technical findings.

## Suggested structure for future writeups

```text
Challenge overview
TL;DR
Initial analysis
  - Hidden win function
  - Binary protections
Program behavior
Vulnerability discovery
  - Format string lead
  - Source analysis
  - Stack overflow
Debugging
Exploit
  - Offset
  - Payload layout
  - Result
Lessons learned
Attachments / references
```

## Optional improvements for this post

These are not required, but would make it even stronger:

### 1. Add a short “root cause” callout

Right after the source analysis:

> The root cause is `read(STDIN_FILENO, note, 256)` writing up to 256 bytes into
> a 64-byte stack buffer. With no canary, the saved return address is reachable.
{: .prompt-info }

### 2. Add a “tools used” line

```text
checksec, pwndbg, cyclic, pwntools
```

This helps readers reproduce the setup.

### 3. Explain the payload construction

Even without publishing the full solver, a short explanation helps:

```python
payload = b"A" * 168
payload += p64(win_address)
```

Only publish the actual address if it is safe to do so; the notes do not include
it, so the post currently describes the layout instead.

### 4. Add a “what I would try next” note

For example:

- test the format string leak more systematically,
- confirm whether the leak is stable enough for a GOT overwrite,
- compare the ret2win path with a libc-based approach.

This turns a dead end into a learning point.

### 5. Add one diagram

A simple Mermaid diagram would make the flow obvious:

```mermaid
flowchart LR
  A[Menu] --> B[Buy a snack]
  B --> C[read 256 bytes into 64-byte note]
  C --> D[Overwrite saved RIP]
  D --> E[maintenance_hatch]
  E --> F[Flag]
```

### 6. Add references

- pwndbg documentation
- pwntools documentation
- a good explanation of ret2win
- the TryHards challenge page, if public

## What not to change

- Do not publish the real flag.
- Do not publish a solver if the challenge is still active and the platform
  forbids it.
- Do not add screenshots of code; text is better.
- Do not remove the failed format string path. It is part of the learning story.

## Bottom line

The post now reads like a walkthrough rather than a scratchpad. The next step in
quality would be a short root-cause callout and a payload-construction paragraph,
not more raw output.
