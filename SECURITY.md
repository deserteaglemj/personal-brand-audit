# Security

## What this skill does with your data

- `scripts/audit.py` reads the one CSV file you name. It writes no files, runs no other programs and makes no network connection. It uses only Python's standard library.
- `SKILL.md` is a set of instructions for Claude. It asks Claude to read what you paste, save your table as a new CSV in a temporary folder, run `scripts/audit.py` on it and report. It does not ask Claude to post, message, log in or change anything on your account.
- Your numbers go wherever your Claude conversation goes, under your own Claude account and its settings. This project receives nothing.

## What to check before you install any skill

A skill is instructions an AI will follow, so read it first. This one is short: `SKILL.md` and one script of about 220 lines.

## Reporting a problem

Open a private report from the repository's Security tab ("Report a vulnerability"), or open an issue if the problem is not sensitive. Please include the input that caused it.
