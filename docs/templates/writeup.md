---
title: "HTB: ExampleBox — Short Descriptive Subtitle"
date: 2026-11-22 19:00:00 +0700
categories: [Writeups, HackTheBox]
tags: [linux, web, privilege-escalation]
description: "One or two sentences describing the box, the path, and what the reader will learn."
image:
  path: cover.png
  alt: "ExampleBox cover"
media_subpath: /assets/img/posts/htb-examplebox/
toc: true
comments: true
pin: false
---

> This post contains spoilers for **ExampleBox**. Replace this with the platform's
> writeup policy and confirm the box is retired before publishing.
{: .prompt-warning }

## Box information

| Field | Value |
| --- | --- |
| Platform | Hack The Box |
| Difficulty | Medium |
| OS | Linux |
| Topics | Web enumeration, Tomcat, systemd |

## Summary

Describe the full path in one short paragraph: initial access, privilege
escalation, and the key weakness. A reader should understand the shape of the
solution before diving into the details.

## Reconnaissance

Explain what you knew before scanning and what you tried first.

```bash
nmap -sC -sV -oA nmap/initial 10.10.10.10
```

Summarize the important results. Do not paste the entire scan output unless it
adds value; put long output in a collapsible block.

<details markdown="1">
<summary>Full nmap output</summary>

```text
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH ...
80/tcp open  http    Apache httpd ...
```

</details>

## Enumeration

Walk through the services you investigated and why.

```bash
ffuf -u http://10.10.10.10/FUZZ -w /usr/share/wordlists/dirb/common.txt
```

What did you find? What did you try next?

## Dead ends

Document approaches that failed and what they taught you. This section is often
the most useful part for readers.

## Foothold

Explain how you got initial access. Include the commands and the reasoning
behind them.

```bash
# Example command
```

> Explain why the vulnerability or misconfiguration worked.
{: .prompt-info }

## Privilege escalation

Explain how you moved from the initial user to the final objective.

```bash
# Enumeration or exploit command
```

Explain what you noticed, why it mattered, and how you confirmed it.

## Lessons learned

- Key takeaway 1
- Key takeaway 2
- Key takeaway 3

## References

- [Tool or documentation](https://example.com)
- [Related post](/posts/related-post/)
