#!/usr/bin/env python3
"""Creator Blackbook Personal Brand Audit: the arithmetic.

Reads a CSV of your posts and prints your medians, each post's multiple of
your own median, save and share rates, and medians per group (format, topic,
hook style). Standard library only. Reads the one file you name, writes
nothing, sends nothing anywhere.

    python3 audit.py posts.csv
    python3 audit.py posts.csv --metric views --by format topic on_camera
    python3 audit.py --selftest
"""
import argparse
import csv
import io
import math
import re
import statistics

METRICS = ["reach", "views", "saves", "shares", "comments", "likes"]
RATES = ["saves", "shares"]  # shown per 1,000 of the judged metric
MIN_GROUP = 3  # smaller groups are reported, but flagged as too few to trust


def key(name):
    return name.strip().lower().replace(" ", "_")


def show(cell, limit=90):
    """A cell made safe to print: no control characters, capped length."""
    return re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", cell)[:limit]


def num(value):
    """'12,345' or '12.3K' or '' -> float or None."""
    text = (value or "").strip().upper()
    if not text or re.fullmatch(r"\d+,\d{1,2}[KM]?", text):  # '1,5' is a decimal comma: refuse to guess
        return None
    text = text.replace(",", "")
    scale = {"K": 1e3, "M": 1e6}.get(text[-1])
    try:
        n = float(text[:-1]) * scale if scale else float(text)
    except ValueError:
        return None
    return n + 0.0 if math.isfinite(n) and n >= 0 else None  # + 0.0 turns -0 into 0


def load(text):
    header = text.split("\n", 1)[0]
    # Excel in much of Europe saves with semicolons; judge by the header line only
    delimiter = max(",;\t", key=header.count)
    names = [key(h) for h in next(csv.reader([header], delimiter=delimiter), [])]
    twice = sorted({h for h in names if h and names.count(h) > 1})
    if twice:
        raise SystemExit("These column names appear more than once: " + ", ".join(map(show, twice)))
    rows = []
    reader = csv.DictReader(io.StringIO(text.replace("\x00", ""), newline=""), delimiter=delimiter)
    for n, raw in enumerate(reader, 2):
        if None in raw:  # more cells than the header: almost always an unquoted 1,000
            raise SystemExit(f"Line {n} has more cells than the header. Write 1,000 as 1000, or put it in quotes.")
        row = {key(k): (v or "").strip() for k, v in raw.items() if k}
        if "saved" in row and "saves" not in row:  # Instagram calls it "saved"
            row["saves"] = row["saved"]
        if any(row.values()):
            rows.append(row)
    return rows


def load_or_exit(text):
    try:
        return load(text)
    except csv.Error as e:  # an open quote in a big file, or one enormous cell
        raise SystemExit(f"This file is not a readable CSV: {e}")


def fmt(x):
    return f"{x:,.1f}".rstrip("0").rstrip(".")


def report(rows, primary=None, by=("format", "topic", "hook_style")):
    out = []
    values = {m: [n for n in (num(r.get(m)) for r in rows) if n is not None] for m in METRICS}
    present = [m for m in METRICS if values[m]]
    if not present:
        return "No numbers found. The CSV needs at least one of these columns: " + ", ".join(METRICS)
    # reach wins when present, unless views covers more posts (a half-filled reach column)
    auto = "views" if len(values["views"]) > len(values["reach"]) else present[0]
    primary = key(primary or auto)
    if not values.get(primary):
        return f"No values in the '{primary}' column."
    medians = {m: statistics.median(values[m]) for m in present}

    out.append(f"POSTS: {len(rows)}   JUDGED ON: {primary}")
    for m in present:  # a cell that is filled but is not a number must never vanish quietly
        bad = [r[m] for r in rows if r.get(m) and num(r[m]) is None]
        if bad:
            out.append(f"WARNING: {len(bad)} value(s) in '{m}' could not be read and were left out: "
                       + ", ".join(show(b, 40) for b in bad[:5]))
    skipped = len(rows) - len(values[primary])
    if skipped:
        out.append(f"WARNING: {skipped} post(s) have no {primary} number and are left out of the lists below.")
    out.append("YOUR MEDIANS: " + "   ".join(f"{m} {fmt(medians[m])}" for m in present))
    base = medians[primary]
    if base == 0:
        return "\n".join(out + [f"Median {primary} is 0, so multiples cannot be worked out."])

    def rate(r, m):
        top, bottom = num(r.get(m)), num(r.get(primary))
        return top / bottom * 1000 if top is not None and bottom else None

    rated = [m for m in RATES if m in present and m != primary]
    typical = {m: [x for x in (rate(r, m) for r in rows) if x is not None] for m in rated}
    if any(typical.values()):
        out.append(f"YOUR USUAL RATES per 1,000 {primary}: "
                   + "   ".join(f"{m} {fmt(statistics.median(typical[m]))}" for m in rated if typical[m]))

    scored = []
    for i, r in enumerate(rows, 1):
        v = num(r.get(primary))
        if v is not None:
            scored.append((v / base, i, v, r))
    scored.sort(key=lambda s: -s[0])

    def line(s):
        mult, i, v, r = s
        rates = "  ".join(f"{m}/1k {fmt(rate(r, m))}" for m in rated if rate(r, m) is not None)
        label = " | ".join(x for x in (r.get("date"), r.get("format"), r.get("topic"), r.get("hook")) if x)
        return f"  #{i}  {fmt(v)}  {mult:.2f}x  {rates}  {show(label)}".rstrip()

    out.append("\nABOVE 2x YOUR MEDIAN:")
    out += [line(s) for s in scored if s[0] >= 2] or ["  none"]
    out.append("\nUNDER HALF YOUR MEDIAN:")
    out += [line(s) for s in scored if s[0] < 0.5] or ["  none"]

    for trait in map(key, by):
        groups = {}
        for _, i, v, r in scored:
            if r.get(trait):
                groups.setdefault(r[trait].lower(), []).append(v)
        if not groups:
            continue
        out.append(f"\nBY {trait.upper()}:")
        for name, vals in sorted(groups.items(), key=lambda g: -statistics.median(g[1])):
            med = statistics.median(vals)
            flag = "" if len(vals) >= MIN_GROUP else "   (too few posts to trust)"
            out.append(f"  {show(name, 40)}: n={len(vals)}  median {fmt(med)}  {med / base:.2f}x{flag}")
    return "\n".join(out)


def read_text(path):
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except OSError as e:
        raise SystemExit(f"Cannot open {path}: {e.strerror}")
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1252", errors="replace")  # Excel on Windows


def selftest():
    sample = "date,format,topic,reach,saved\n" + "\n".join(
        f"2026-01-{d:02d},{f},{t},{r},{s}"
        for d, (f, t, r, s) in enumerate(
            [("reel", "gym", "100", "0"), ("reel", "gym", "200", "1"), ("reel", "gym", "300", "2"),
             ("carousel", "travel", '"1,000"', "5"), ("carousel", "travel", "2K", "9")], 1))
    text = report(load(sample))
    assert "reach 300" in text and "saves 2" in text, text          # medians, with 'saved' mapped
    assert "YOUR USUAL RATES per 1,000 reach: saves 5" in text, text  # 0, 5, 6.67, 5, 4.5 -> 5
    assert "#5  2,000  6.67x  saves/1k 4.5" in text and "#1  100  0.33x  saves/1k 0" in text, text
    assert "gym: n=3  median 200  0.67x" in text, text
    assert "travel: n=2  median 1,500  5.00x   (too few posts to trust)" in text, text
    assert num("12.3K") == 12300 and num("") is None and num("n/a") is None
    assert num("inf") is None and num("-5") is None and num("1,5") is None and num("1,5K") is None
    assert num("1,234") == 1234 and str(num("-0")) == "0.0"
    assert show("a\x1b[31mb\x00") == "a [31mb " and len(show("x" * 200, 40)) == 40
    for broken in ("reach,reach\n1,2\n", ):
        try:
            load(broken)
            raise AssertionError("a repeated column name must stop the run")
        except SystemExit:
            pass
    try:
        load_or_exit('reach\n"' + "x" * 200000)
        raise AssertionError("an unreadable CSV must stop the run cleanly")
    except SystemExit:
        pass
    assert "reach 5" in report(load("reach\n5\x00\n"))
    assert report([{"format": "reel"}]).startswith("No numbers found")
    # semicolons, a spaced header, a half-filled reach column, an unreadable cell, a blank line
    sparse = report(load("Hook Style;reach;views\nclaim;500;10\nclaim;;20\n;;\nclaim;;30\nlist;;2 000\n"))
    assert "POSTS: 4   JUDGED ON: views" in sparse and "BY HOOK_STYLE" in sparse, sparse
    assert "1 value(s) in 'views' could not be read and were left out: 2 000" in sparse, sparse
    assert "1 post(s) have no views number" in sparse, sparse
    try:
        load("date,reach\n2026-01-01,1,000\n")
        raise AssertionError("an unquoted 1,000 must stop the run")
    except SystemExit:
        pass
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="?")
    ap.add_argument("--metric", help="judge posts on this column (default: reach, or views when it covers more posts)")
    ap.add_argument("--by", nargs="+", default=["format", "topic", "hook_style"], help="columns to group by")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif not a.csv:
        ap.error("give a CSV file, or --selftest")
    else:
        print(report(load_or_exit(read_text(a.csv)), a.metric, a.by))
