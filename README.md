# Creator Blackbook Personal Brand Audit

A free Claude skill that audits your own social account. You give it your last 30 posts and your profile. It tells you what to stop, what to keep, what to test, and what to fix on your profile.

It judges you against your own median, not against other creators. Every finding comes with the number behind it.

Works for Instagram, TikTok, YouTube, X and LinkedIn. No API key, no connected account, no login. Your numbers stay on your computer.

## What you get

1. Your medians (reach, views, saves, shares, comments).
2. The posts that beat your median, and what they have in common.
3. The formats and topics that sit under half your median.
4. Stop, Keep and Test lists.
5. Up to three profile fixes.
6. One positioning sentence, with the missing proof marked.
7. Your next five posts, each tied to a number.

## Install

**Claude Code**

```bash
git clone https://github.com/deserteaglemj/personal-brand-audit ~/.claude/skills/personal-brand-audit
```

Then start a new chat and say: `audit my page`.

**Claude on the web or phone**

Open `SKILL.md`, copy all of it into a chat, and say: `Follow this. Audit my page.` Claude will do the arithmetic by hand, since the script cannot run there.

## What to have ready

- Your profile: name, bio, link and pinned posts (text or a screenshot).
- Your last 30 posts with their numbers. Three ways to give them:
  - Fill in `template.csv`.
  - Paste a table into the chat.
  - Screenshot each post's insights. Claude reads them into a table and shows it back to you first.

In a CSV, write `1000`, not `1,000`, or put the number in quotes.

## Run the arithmetic yourself

```bash
python3 scripts/audit.py template.csv
```

```bash
python3 scripts/audit.py --selftest
```

Python 3.9 or newer. Standard library only.

## Limits

- Thirty posts is a small sample. The audit gives you leads to test, not proof.
- Groups with fewer than three posts are marked "too few posts to trust".
- It reads and reports. It does not post, edit your profile or send anything.

## Credits

Written by Creator Blackbook. The method draws on ideas from these MIT-licensed projects, rewritten in our own words:

- [Ootto-AI/claude-content-skills](https://github.com/Ootto-AI/claude-content-skills): auditing the last 30 posts against your own median; the profile visitor check; the positioning sentence.
- [Jakeschincariol/instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill): outlier multiples, shares against reach, and checking a hook for something specific.
- [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills): a median baseline for finding outlier posts.

## License

MIT. See `LICENSE`.
