---
name: personal-brand-audit
description: Creator Blackbook Personal Brand Audit. Audits one creator's own social account (Instagram, TikTok, YouTube, X or LinkedIn) from numbers they paste, export or screenshot, and returns what to stop, keep and test, plus profile fixes. Use when someone says "audit my page", "audit my account", "personal brand audit", "what's working on my Instagram", "what should I stop posting", "review my profile", or "why isn't my content growing".
license: MIT
---

# Creator Blackbook Personal Brand Audit

Judge the account against **its own median**, never against other creators. Every claim in the report carries the number it came from. Where the data cannot answer, write "not enough signal".

Work through the steps in order. Each step ends when its "Done when" line is true.

## 1. Intake

Ask for these in one message, then wait:

1. The platform and handle.
2. What the account is for: who it should reach and what a visitor should do (follow, DM, sign up, buy).
3. The profile as a visitor sees it: name field, bio, link, pinned posts. Pasted text or a screenshot.
4. The last 30 posts with numbers. Any of: a CSV (see `template.csv`), a pasted table, or screenshots of each post's insights. Fewer than 30 is fine; under 10, say the audit will be thin.
5. Optional: facts they can prove (results, years, clients who agreed to be named).

Per post, take whatever exists of: date, format (reel, carousel, photo, video, text), topic, the first line or opening words, reach, views, saves, shares, comments, likes.

If they only have screenshots, read the numbers into a table yourself and show it back for a yes before using it.

Done when: you hold a table of posts with at least one number column, and the person has confirmed it is right.

## 2. Tag the posts

Add three columns yourself, from the caption or first line:

- `topic`: 3 to 6 topics in the person's own words. Show the list and let them rename.
- `hook_style`: one of number, list, question, how-to, story, claim, none. When two fit, take the one that comes first in that order ("3 pricing mistakes" is number).
- `on_camera`: yes or no, when they have told you or it is visible.

Done when: every post has a topic and a hook_style.

## 3. Run the numbers

Save the table as a CSV and run the script that sits in this skill's folder:

```
python3 <this skill's folder>/scripts/audit.py posts.csv
```

It prints the medians, every post above 2x or under half the median, and the median for each format, topic and hook style. Use `--metric views` when there is no reach column, and add `--by format topic hook_style on_camera` when you filled in on_camera. If Python is unavailable, work the same figures by hand and show the working.

Judge on **reach** when it exists. Views count repeat plays and swipes, so they are not comparable across formats.

Groups with fewer than 3 posts are printed with a warning. Report them as "not enough signal", never as a finding: in the report they go in Test and in section 8.

If no post is under half the median, say so. Name the lowest group that has 3 or more posts as the one to watch, with its multiple.

Also work out, when the columns exist: saves per 1,000 reach and shares per 1,000 reach for the top five and bottom five posts. A post that is shared or saved far above the account's usual rate is worth more than its reach shows.

Done when: you have the median, the outliers, the dead weight and the per-group table, each with n.

## 4. Read the winners and the losers

Put the top five and the bottom five side by side. For each trait (format, topic, hook style, on camera, length if known), state what the winners share that the losers lack. One trait at a time.

Check for a confound before you blame a trait: if every low post is the same format *and* the same topic, say you cannot tell which one caused it.

Then check the first lines. A strong opening names something specific: a number, a price, a named person or a named place. A plain label ("Sunday bake", "New apron") does not count. Count how many of the top five and bottom five do. Report the counts, not a verdict, unless the gap is clear.

Done when: each pattern you will report has its count and its multiple.

## 5. Check the profile in ten seconds

Answer each from what is actually on the profile. Quote the words you are judging.

| Question | Where it should be answered |
|---|---|
| Who is this for? | bio, first line |
| What do they get? | bio, first line |
| Why believe it? | bio second line, or first pinned post |
| What do I do next? | one ask, and a link that matches it |
| Do the pinned posts back it up? | one proof, one offer or giveaway, one best teaching post |
| Does the feed match the purpose? | share of the posts on what the account is for (intake item 2) |

Mark each: clear, unclear, or missing. Unclear and missing become fixes. When there are more than three, report the three highest in the table and list the rest in one line.

Done when: all six rows are marked, each with the quoted evidence.

## 6. One positioning sentence

Write it in this shape, only from facts the person gave you:

> For [specific audience] who need [job], [name] helps them get [outcome] through [how], with [proof].

The job is what the audience is trying to do. The outcome is a result the person can prove they deliver. Put any part you have no fact for in square brackets, like `[missing: one result you can show]`. A bracket is a to-do for them, not a gap for you to fill.

Then test it: could another creator in their niche say this sentence unchanged? If yes, say which part would make it theirs alone.

Done when: one sentence exists, with every unproven part bracketed.

## 7. The report

Keep it to one screen per section. Plain words.

1. **Your numbers**: the medians, and which metric you judged on.
2. **What won**: the outliers and the trait they share, with multiples.
3. **What to stop**: formats or topics that sit under half the median, with n.
4. **Stop / Keep / Test**: three short lists. Test holds the patterns with too few posts to trust.
5. **Profile fixes**: at most three, most important first, each tied to a row in step 5.
6. **Your positioning sentence**, with its brackets.
7. **Your next five posts**: each one justified by a number above.
8. **What this audit could not tell**: every "not enough signal", and what data would settle it.

Done when: every number in the report appears in the step 3 output or the person's own table, or is a count or rate you worked out from that table and showed the working for.

## Rules

- Their median is the only yardstick. Leave industry benchmarks out.
- State findings as what the numbers show for this account in this period. A pattern in 30 posts is a lead to test, so word it that way.
- Use only results, followers and proof the person supplied.
- Offer bio wording only from facts they gave; mark it as a draft for them to edit.
- The audit reads and reports. Posting, editing a profile and messaging stay with the person.
