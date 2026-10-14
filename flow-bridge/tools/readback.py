#!/usr/bin/env python3
"""flow-bridge readback — 설정이 실제로 적용됐는지 툴에게 물어보고 판정한다.

파일을 읽고 추정하는 대신, stage 끝에서 툴이 보고하는 실효값으로 덮어쓰기를 확정한다.
이 도구는 DTCO 항목을 모른다. 카드 frontmatter의 settings(readback / expect)만 사용한다.

사용:
  1) 생성: 2단계 placement와 카드로 stage별 readback tcl + expect.yaml 생성
     python3 tools/readback.py gen --placement placement.yaml --cards <카드 폴더> --out <폴더> [--variant invs_legacy]

  2) 판정: run 로그에서 FB_READBACK 줄을 모아 applied / overridden / missing / not_checkable 판정
     python3 tools/readback.py judge --expect <폴더>/expect.yaml --log <run 로그> [--out result.yaml]

생성된 readback_<stage>.tcl 은 고객 flow의 해당 stage 끝에서 source되어야 한다 (2단계 patch_lines).
로그 줄 형식: FB_READBACK|<item_id>.<setting번호>|<stage>|OK|<값>   또는  ...|ERR|<에러>

종료 코드: 0 = 전부 applied, 1 = overridden/missing 있음, 2 = 사용법/입력 오류
의존성: PyYAML  # TODO(INHOUSE): 사내 python에 PyYAML 설치 여부 확인
"""
import argparse
import glob
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate import split_card  # noqa: E402  (카드 frontmatter 파서 공유)

TAG = "FB_READBACK"
USE_DECISIONS = {"placeable", "already_present"}  # readback 대상이 되는 2단계 판정
SEVERITY = ["applied", "not_checkable", "missing", "overridden"]  # 뒤로 갈수록 나쁨
BOOL_NORM = {"1": "true", "0": "false", "true": "true", "false": "false"}


# ---------------------------------------------------------------- gen

def load_cards(cards_dir):
    cards = {}
    for path in sorted(glob.glob(os.path.join(cards_dir, "DTCO-*.md"))):
        with open(path, encoding="utf-8") as f:
            front, _ = split_card(f.read())
        cards[front["item_id"]] = (front, path)
    return cards


def build_expect(placement, cards, variant):
    """placement + 카드 → readback 대상 목록. 오류는 숨기지 않고 errors로 반환."""
    entries, errors = [], []
    for p in placement.get("placements", []):
        if p.get("decision") not in USE_DECISIONS:
            continue
        item_id = p["item_id"]
        if item_id not in cards:
            errors.append("%s: card not found in cards dir" % item_id)
            continue
        front, path = cards[item_id]
        if front.get("version") != p.get("item_version"):
            errors.append("%s: placement used card v%s but card is now v%s (re-run stage 2)"
                          % (item_id, p.get("item_version"), front.get("version")))
            continue
        stages = p.get("readback_points") or [front["stage"]]
        settings = [s for s in front.get("settings", []) if s.get("variant") == variant]
        if not settings:
            errors.append("%s: no setting for variant %s" % (item_id, variant))
            continue
        for idx, s in enumerate(settings, start=1):
            checkable = bool(s.get("readback")) and bool(s.get("expect"))
            entries.append({
                "key": "%s.%d" % (item_id, idx),
                "item_id": item_id,
                "set": s["set"],
                "readback": s.get("readback", ""),
                "expect": s.get("expect", ""),
                "verified": bool(s.get("verified")),
                "stages": list(stages),
                "checkable": checkable,
            })
    return entries, errors


def render_tcl(stage, entries):
    lines = [
        "# flow-bridge readback (auto-generated, do not edit) stage=%s" % stage,
        "# source this at the END of stage '%s' in the customer flow" % stage,
    ]
    for e in entries:
        if stage not in e["stages"]:
            continue
        if not e["readback"]:
            lines.append("puts \"%s|%s|%s|ERR|no readback command in card\"" % (TAG, e["key"], stage))
            continue
        lines += [
            "# %s : %s" % (e["key"], e["set"]),
            "if {[catch {set ::fb_rb_v [%s]} ::fb_rb_e]} {" % e["readback"],
            "    puts \"%s|%s|%s|ERR|[string map {\"\\n\" \" \"} $::fb_rb_e]\"" % (TAG, e["key"], stage),
            "} else {",
            "    puts \"%s|%s|%s|OK|[string map {\"\\n\" \" \"} $::fb_rb_v]\"" % (TAG, e["key"], stage),
            "}",
        ]
    return "\n".join(lines) + "\n"


def cmd_gen(args):
    with open(args.placement, encoding="utf-8") as f:
        placement = yaml.safe_load(f)
    variant = args.variant or placement.get("tool_variant")
    if not variant:
        print("ERROR: tool_variant not given (placement.tool_variant or --variant)")
        return 2
    entries, errors = build_expect(placement, load_cards(args.cards), variant)
    for e in errors:
        print("ERROR: " + e)
    if errors:
        return 2
    os.makedirs(args.out, exist_ok=True)
    stages = sorted({s for e in entries for s in e["stages"]})
    for stage in stages:
        with open(os.path.join(args.out, "readback_%s.tcl" % stage), "w", encoding="utf-8") as f:
            f.write(render_tcl(stage, entries))
    with open(os.path.join(args.out, "expect.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump({"tool_variant": variant, "entries": entries}, f, allow_unicode=True, sort_keys=False)
    print("generated %d readback file(s) for stages %s -> %s" % (len(stages), stages, args.out))
    for e in entries:
        if not e["checkable"]:
            print("  note: %s has no readback/expect -> will be not_checkable" % e["key"])
        elif not e["verified"]:
            print("  note: %s readback not verified on in-house tool yet" % e["key"])
    return 0


# ---------------------------------------------------------------- judge

def _norm(v):
    v = " ".join(str(v).split()).lower()
    return BOOL_NORM.get(v, v)


def parse_log(path):
    """FB_READBACK 줄 → {(key, stage): (status, value)}. 같은 키가 여러 번이면 마지막 값."""
    seen = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            pos = line.find(TAG + "|")
            if pos < 0:
                continue
            parts = line[pos:].rstrip("\n").split("|", 4)
            if len(parts) == 5:
                _, key, stage, status, value = parts
                seen[(key, stage)] = (status, value.strip())
    return seen


def judge_entry(entry, stage, seen):
    if not entry["checkable"]:
        return "not_checkable", "card has no readback/expect"
    hit = seen.get((entry["key"], stage))
    if hit is None:
        return "missing", "no readback line (readback file not sourced at this stage?)"
    status, value = hit
    if status != "OK":
        return "not_checkable", "readback error: %s" % value
    if _norm(entry["expect"]) in _norm(value):
        return "applied", value
    return "overridden", value


def judge(expect, seen):
    """항목 × stage 결과 (설정이 여러 개면 가장 나쁜 판정)."""
    results = {}
    for e in expect["entries"]:
        for stage in e["stages"]:
            status, observed = judge_entry(e, stage, seen)
            k = (e["item_id"], stage)
            prev = results.get(k)
            if prev is None or SEVERITY.index(status) > SEVERITY.index(prev["status"]):
                results[k] = {"item_id": e["item_id"], "stage": stage,
                              "status": status, "observed": "%s: %s" % (e["key"], observed)}
    return list(results.values())


def cmd_judge(args):
    with open(args.expect, encoding="utf-8") as f:
        expect = yaml.safe_load(f)
    seen = parse_log(args.log)
    rows = judge(expect, seen)

    stages_in_log = {stage for (_, stage) in seen}
    for stage in sorted({r["stage"] for r in rows} - stages_in_log):
        print("hint: no FB_READBACK lines at all for stage '%s' -> readback_%s.tcl probably not sourced" % (stage, stage))

    print("%-12s %-12s %-14s %s" % ("item", "stage", "status", "observed"))
    for r in rows:
        print("%-12s %-12s %-14s %s" % (r["item_id"], r["stage"], r["status"], r["observed"]))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            yaml.safe_dump({"readback": rows}, f, allow_unicode=True, sort_keys=False)
    bad = [r for r in rows if r["status"] in ("overridden", "missing")]
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="flow-bridge readback")
    sub = ap.add_subparsers(dest="cmd")
    g = sub.add_parser("gen")
    g.add_argument("--placement", required=True)
    g.add_argument("--cards", required=True)
    g.add_argument("--out", required=True)
    g.add_argument("--variant")
    j = sub.add_parser("judge")
    j.add_argument("--expect", required=True)
    j.add_argument("--log", required=True)
    j.add_argument("--out")
    args = ap.parse_args(argv)
    if args.cmd == "gen":
        return cmd_gen(args)
    if args.cmd == "judge":
        return cmd_judge(args)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
