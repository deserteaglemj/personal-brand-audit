#!/usr/bin/env python3
"""Creator Blackbook Personal Brand Audit: the arithmetic.

Reads a CSV of your posts and prints your medians, each post's multiple of
your own median, and medians per group (format, topic, hook). Standard
library only. Nothing is sent anywhere.

    python3 audit.py posts.csv
    python3 audit.py posts.csv --by format topic
    python3 audit.py --selftest
"""
import argparse
import csv
import io
import statistics

METRICS = ["reach", "views", "saves", "shares", "comments", "likes"]
MIN_GROUP = 3  # smaller groups are reported, but flagged as too few to trust


def num(value):
    """'12,345' or '12.3K' or '' -> float or None."""
    text = (value or "").strip().replace(",", "").upper()
    if not text:
        return None
    scale = {"K": 1e3, "M": 1e6}.get(text[-1])
    try:
        return float(text[:-1]) * scale if scale else float(text)
    except ValueError:
        return None


def load(handle):
    rows = []
    for n, raw in enumerate(csv.DictReader(handle), 2):
        if None in raw:  # more cells than the header: almost always an unquoted 1,000
            raise SystemExit(f"Line {n} has more cells than the header. Write 1,000 as 1000, or put it in quotes.")
        row = {k.strip().lower().replace(" ", "_"): (v or "").strip() for k, v in raw.items() if k}
        if "saved" in row and "saves" not in row:  # Instagram calls it "saved"
            row["saves"] = row["saved"]
        rows.append(row)
    return rows


def fmt(x):
    return f"{x:,.1f}".rstrip("0").rstrip(".")


def report(rows, primary=None, by=("format", "topic", "hook_style")):
    out = []
    values = {m: [n for n in (num(r.get(m)) for r in rows) if n is not None] for m in METRICS}
    present = [m for m in METRICS if values[m]]
    if not present:
        return "No numbers found. The CSV needs at least one of: " + ", ".join(METRICS)
    # reach wins when present, unless views covers more posts (a half-filled reach column)
    auto = "views" if len(values["views"]) > len(values["reach"]) else present[0]
    primary = (primary or auto).strip().lower().replace(" ", "_")
    if not values.get(primary):
        return f"No values in the '{primary}' column."
    medians = {m: statistics.median(values[m]) for m in present}

    out.append(f"POSTS: {len(rows)}   JUDGED ON: {primary}")
    for m in present:  # a cell that is filled but is not a number must never vanish quietly
        bad = [r[m] for r in rows if r.get(m) and num(r[m]) is None]
        if bad:
            out.append(f"WARNING: {len(bad)} value(s) in '{m}' could not be read and were left out: " + ", ".join(bad[:5]))
    skipped = len(rows) - len(values[primary])
    if skipped:
        out.append(f"WARNING: {skipped} post(s) have no {primary} number and are left out of the lists below.")
    out.append("YOUR MEDIANS: " + "   ".join(f"{m} {fmt(medians[m])}" for m in present))
    base = medians[primary]
    if base == 0:
        return "\n".join(out + [f"Median {primary} is 0, so multiples cannot be worked out."])

    scored = []
    for i, r in enumerate(rows, 1):
        v = num(r.get(primary))
        if v is not None:
            scored.append((v / base, i, v, r))
    scored.sort(key=lambda s: -s[0])

    def line(s):
        mult, i, v, r = s
        label = " | ".join(x for x in (r.get("date"), r.get("format"), r.get("topic"), r.get("hook")) if x)
        return f"  #{i}  {fmt(v)}  {mult:.2f}x  {label[:90]}"

    out.append("\nABOVE 2x YOUR MEDIAN:")
    out += [line(s) for s in scored if s[0] >= 2] or ["  none"]
    out.append("\nUNDER HALF YOUR MEDIAN:")
    out += [line(s) for s in scored if s[0] < 0.5] or ["  none"]

    for trait in by:
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
            out.append(f"  {name}: n={len(vals)}  median {fmt(med)}  {med / base:.2f}x{flag}")
    return "\n".join(out)


def selftest():
    sample = "date,format,topic,reach,saved\n" + "\n".join(
        f"2026-01-{d:02d},{f},{t},{r},{s}"
        for d, (f, t, r, s) in enumerate(
            [("reel", "gym", "100", "0"), ("reel", "gym", "200", "1"), ("reel", "gym", "300", "2"),
             ("carousel", "travel", '"1,000"', "5"), ("carousel", "travel", "2K", "9")], 1))
    text = report(load(io.StringIO(sample)))
    assert "reach 300" in text and "saves 2" in text, text          # medians, with 'saved' mapped
    assert "#5  2,000  6.67x" in text and "#1  100  0.33x" in text, text
    assert "gym: n=3  median 200  0.67x" in text, text
    assert "travel: n=2  median 1,500  5.00x   (too few posts to trust)" in text, text
    assert num("12.3K") == 12300 and num("") is None and num("n/a") is None
    assert report([{"format": "reel"}]).startswith("No numbers found")
    sparse = report(load(io.StringIO("Hook Style,reach,views\nclaim,500,10\nclaim,,20\nclaim,,30\nlist,,2 000\n")))
    assert "JUDGED ON: views" in sparse and "BY HOOK_STYLE" in sparse, sparse
    assert "1 value(s) in 'views' could not be read and were left out: 2 000" in sparse, sparse
    assert "1 post(s) have no views number" in sparse, sparse
    try:
        load(io.StringIO("date,reach\n2026-01-01,1,000\n"))
        raise AssertionError("an unquoted 1,000 must stop the run")
    except SystemExit:
        pass
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="?")
    ap.add_argument("--metric", help="judge posts on this column (default: reach if present, else views)")
    ap.add_argument("--by", nargs="+", default=["format", "topic", "hook_style"], help="columns to group by")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif not a.csv:
        ap.error("give a CSV file, or --selftest")
    else:
        try:
            raw = open(a.csv, "rb").read()
        except OSError as e:
            raise SystemExit(f"Cannot open {a.csv}: {e.strerror}")
        if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
            text = raw.decode("utf-16")
        else:
            try:
                text = raw.decode("utf-8-sig")
            except UnicodeDecodeError:
                text = raw.decode("cp1252", errors="replace")  # Excel on Windows
        print(report(load(io.StringIO(text, newline="")), a.metric, [b.strip().lower().replace(" ", "_") for b in a.by]))
