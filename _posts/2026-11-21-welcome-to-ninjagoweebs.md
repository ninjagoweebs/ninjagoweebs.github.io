---
title: Welcome to NinjagoWeebs
date: 2026-11-21 12:00:00 +0700
categories: [Announcements]
tags: [welcome, security, blogging]
pin: true
---

Welcome to my corner of the internet! This site is a place for security writeups, CTF walkthroughs, and educational posts about the tools and techniques I pick up along the way.

<!--more-->

## What to expect

I plan to publish three kinds of content:

1. **CTF writeups** — how I approached a challenge, what failed, and what finally worked.
2. **Lab walkthroughs** — step-by-step notes for boxes and practice environments.
3. **Learning notes** — explanations of concepts, commands, and tooling.

## Why write things down?

Writing forces me to slow down and check whether I actually understand something. It also creates a reference I can come back to later — and hopefully helps someone else who is stuck on the same problem.

> The best writeup is the one that explains *why*, not just *what*.
{: .prompt-tip }

## A tiny example

Here is the kind of quick snippet you can expect in future posts:

```bash
# Find SUID binaries on a Linux host
find / -perm -4000 -type f 2>/dev/null
```

And a short Python example:

```python
import requests

response = requests.get("https://example.com", timeout=10)
print(response.status_code)
```

## Stay tuned

New posts will appear on the [home page](/), and you can browse them by [category](/categories/) or [tag](/tags/). If you want to follow along, the [RSS feed](/feed.xml) is available too.

Thanks for stopping by — happy hacking!
