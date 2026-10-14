#!/usr/bin/env python3
"""flow-bridge validate — LLM이 쓴 파일이 스키마/인용/카드 규칙을 지켰는지 기계적으로 검사한다.

이 도구는 DTCO 항목이나 고객 flow 구조를 모른다. 스키마와 카드 규격에 적힌 규칙만 확인한다.
새 항목/새 flow 때문에 이 파일을 고쳐야 한다면 설계가 틀린 것이다.

사용:
    python3 tools/validate.py flow_profile   <file.yaml>
    python3 tools/validate.py design_profile <file.yaml>
    python3 tools/validate.py card           <card.md>
    python3 tools/validate.py stage1|stage2|stage3|stage4 <file.yaml> [--root DIR]
        --root: contract 안 citation의 기준 디렉토리 (stage2는 flow_root)

종료 코드: 0 = 통과, 1 = 위반 있음, 2 = 사용법/파일 오류
의존성: PyYAML  # TODO(INHOUSE): 사내 python에 PyYAML 설치 여부 확인
"""
import argparse
import os
import re
import sys

import yaml

FB_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_DIR = os.path.join(FB_ROOT, "schema")

SCHEMAS = {
    "flow_profile": "flow_profile.schema.yaml",
    "design_profile": "design_profile.schema.yaml",
    "card": "item_card.schema.yaml",
    "stage1": "contract/stage1_mapping.schema.yaml",
    "stage2": "contract/stage2_placement.schema.yaml",
    "stage3": "contract/stage3_selection.schema.yaml",
    "stage4": "contract/stage4_ablation.schema.yaml",
}

ALLOWED_KEYWORDS = {
    "type", "required", "properties", "additionalProperties", "enum", "items",
    "pattern", "minimum", "maximum", "oneOf", "$ref", "const", "description", "$defs",
}

CARD_SECTIONS = ["요약", "설정", "평가 결과", "해석", "고객 flow 이식 주의", "질문", "이력"]
RESULT_COLUMNS = ["id", "날짜", "ver", "출처", "디자인", "조건", "fmax%", "WNS", "TNS",
                  "power%", "area%", "판정", "run", "비고"]
RESULT_SOURCES = {"eval", "bridge"}
RESULT_VERDICTS = {"positive", "neutral", "negative", "inconclusive", "invalid"}
NUMERIC_COLUMNS = ["fmax%", "WNS", "TNS", "power%", "area%"]
NUM_RE = re.compile(r"^[+-]?\d+(\.\d+)?$")


# ---------------------------------------------------------------- schema subset

class SchemaStore:
    """schema/ 아래 YAML 스키마를 읽고 $ref를 해석한다."""

    def __init__(self):
        self._cache = {}

    def load(self, path):
        path = os.path.normpath(path)
        if path not in self._cache:
            with open(path, encoding="utf-8") as f:
                self._cache[path] = yaml.safe_load(f)
        return self._cache[path]

    def resolve(self, ref, base_path):
        file_part, _, frag = ref.partition("#")
        target = os.path.join(os.path.dirname(base_path), file_part) if file_part else base_path
        target = os.path.normpath(target)
        node = self.load(target)
        for key in [k for k in frag.split("/") if k]:
            if not isinstance(node, dict) or key not in node:
                raise KeyError("unresolvable $ref: %s (from %s)" % (ref, base_path))
            node = node[key]
        return node, target


def _type_ok(value, t):
    if t == "string":
        return isinstance(value, str)
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if t == "boolean":
        return isinstance(value, bool)
    if t == "object":
        return isinstance(value, dict)
    if t == "array":
        return isinstance(value, list)
    raise ValueError("unsupported type keyword value: %s" % t)


def check_schema(value, schema, store, base_path, where="$"):
    """value를 schema 부분집합으로 검사해 오류 문자열 목록을 반환한다."""
    errors = []
    if not isinstance(schema, dict):
        return ["%s: schema node is not a mapping" % where]
    unknown = set(schema) - ALLOWED_KEYWORDS
    if unknown:
        # 지원하지 않는 키워드는 조용히 무시하지 않는다 (fail-fast)
        return ["%s: unsupported schema keyword(s) %s in %s" % (where, sorted(unknown), base_path)]

    if "$ref" in schema:
        target, target_path = store.resolve(schema["$ref"], base_path)
        return check_schema(value, target, store, target_path, where)

    if "oneOf" in schema:
        matches = [opt for opt in schema["oneOf"]
                   if not check_schema(value, opt, store, base_path, where)]
        if len(matches) != 1:
            errors.append("%s: value %r matches %d of oneOf options (need exactly 1)"
                          % (where, _short(value), len(matches)))
        return errors

    if "const" in schema and value != schema["const"]:
        return ["%s: expected const %r, got %r" % (where, schema["const"], _short(value))]

    if "type" in schema and not _type_ok(value, schema["type"]):
        return ["%s: expected %s, got %s" % (where, schema["type"], type(value).__name__)]

    if "enum" in schema and value not in schema["enum"]:
        errors.append("%s: %r not in %s" % (where, _short(value), schema["enum"]))

    if "pattern" in schema and isinstance(value, str) and not re.search(schema["pattern"], value):
        errors.append("%s: %r does not match pattern %s" % (where, value, schema["pattern"]))

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append("%s: %r < minimum %r" % (where, value, schema["minimum"]))
        if "maximum" in schema and value > schema["maximum"]:
            errors.append("%s: %r > maximum %r" % (where, value, schema["maximum"]))

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append("%s: missing required field '%s'" % (where, key))
        props = schema.get("properties", {})
        for key, sub in value.items():
            if key in props:
                errors += check_schema(sub, props[key], store, base_path, "%s.%s" % (where, key))
            elif schema.get("additionalProperties") is False:
                errors.append("%s: unexpected field '%s'" % (where, key))

    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            errors += check_schema(item, schema["items"], store, base_path, "%s[%d]" % (where, i))

    return errors


def _short(v):
    s = repr(v)
    return s if len(s) <= 60 else s[:57] + "..."


# ---------------------------------------------------------------- citations

def iter_citations(node, where="$"):
    if isinstance(node, dict):
        if {"file", "line", "excerpt"} <= set(node):
            yield where, node
        for k, v in node.items():
            for item in iter_citations(v, "%s.%s" % (where, k)):
                yield item
    elif isinstance(node, list):
        for i, v in enumerate(node):
            for item in iter_citations(v, "%s[%d]" % (where, i)):
                yield item


def _norm_ws(s):
    return " ".join(str(s).split())


def check_citations(data, root):
    """citation의 line 줄에 excerpt가 실제로 있는지 대조한다."""
    errors = []
    if not root:
        return ["citation root is not set (profile root field or --root)"]
    file_cache = {}
    for where, c in iter_citations(data):
        path = os.path.join(root, str(c["file"]))
        if path not in file_cache:
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    file_cache[path] = f.read().split("\n")
            except OSError:
                file_cache[path] = None
        lines = file_cache[path]
        if lines is None:
            errors.append("%s: cited file not found: %s" % (where, c["file"]))
            continue
        line_no = c["line"]
        if not isinstance(line_no, int) or line_no < 1 or line_no > len(lines):
            errors.append("%s: line %r out of range for %s (%d lines)"
                          % (where, line_no, c["file"], len(lines)))
            continue
        if _norm_ws(c["excerpt"]) not in _norm_ws(lines[line_no - 1]):
            errors.append("%s: excerpt %r not found at %s:%d (line is %r)"
                          % (where, c["excerpt"], c["file"], line_no,
                             lines[line_no - 1].strip()[:80]))
    return errors


def _resolve_root(root, data_file):
    """상대 root는 현재 디렉토리 → 데이터 파일 위치 → flow-bridge 루트 순으로 찾는다."""
    if not root:
        return None
    if os.path.isabs(root) or os.path.isdir(root):
        return root
    for base in (os.path.dirname(os.path.abspath(data_file)), FB_ROOT):
        alt = os.path.join(base, root)
        if os.path.isdir(alt):
            return alt
    return root


# ---------------------------------------------------------------- card

def split_card(text):
    """'---' frontmatter와 본문을 분리한다."""
    if not text.startswith("---"):
        raise ValueError("card must start with '---' frontmatter")
    parts = text.split("\n---", 1)
    if len(parts) != 2:
        raise ValueError("frontmatter closing '---' not found")
    front = yaml.safe_load(parts[0][3:])
    body = parts[1].split("\n", 1)[1] if "\n" in parts[1] else ""
    return front, body


def _sections(body):
    """'## 제목' 단위로 본문을 나눈다. (제목, 내용) 목록."""
    out, title, buf = [], None, []
    for line in body.split("\n"):
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m and not line.startswith("###"):
            if title is not None:
                out.append((title, "\n".join(buf)))
            title, buf = m.group(1), []
        elif title is not None:
            buf.append(line)
    if title is not None:
        out.append((title, "\n".join(buf)))
    return out


def _table_rows(section_text):
    rows = []
    for line in section_text.split("\n"):
        line = line.strip()
        if line.startswith("|") and line.endswith("|"):
            rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows


def check_card_body(front, body):
    errors = []
    item_id = front.get("item_id", "")
    h1 = re.search(r"^#\s+(\S+)", body, re.M)
    if not h1 or h1.group(1) != item_id:
        errors.append("body: first '# ' heading must start with item_id %s" % item_id)

    sections = _sections(body)
    titles = [t for t, _ in sections]
    if titles != CARD_SECTIONS:
        errors.append("body: sections must be exactly %s in order, got %s" % (CARD_SECTIONS, titles))
    content = dict(sections)

    rows = _table_rows(content.get("평가 결과", ""))
    if not rows:
        errors.append("평가 결과: result table not found")
        return errors
    if rows[0] != RESULT_COLUMNS:
        errors.append("평가 결과: columns must be %s, got %s" % (RESULT_COLUMNS, rows[0]))
        return errors
    data_rows = [r for r in rows[1:] if not all(set(c) <= set("-: ") for c in r)]

    valid_ids, all_ids = set(), set()
    version = front.get("version", 0)
    for n, r in enumerate(data_rows, start=1):
        tag = "평가 결과 row %d" % n
        if len(r) != len(RESULT_COLUMNS):
            errors.append("%s: expected %d cells, got %d" % (tag, len(RESULT_COLUMNS), len(r)))
            continue
        row = dict(zip(RESULT_COLUMNS, r))
        expected_id = "R-%03d" % n
        if row["id"] != expected_id:
            errors.append("%s: id must be %s (sequential, append-only), got %s" % (tag, expected_id, row["id"]))
        all_ids.add(row["id"])
        if not row["ver"].isdigit() or int(row["ver"]) > version:
            errors.append("%s: ver %r must be an integer <= card version %s" % (tag, row["ver"], version))
        if row["출처"] not in RESULT_SOURCES:
            errors.append("%s: 출처 %r not in %s" % (tag, row["출처"], sorted(RESULT_SOURCES)))
        if row["판정"] not in RESULT_VERDICTS:
            errors.append("%s: 판정 %r not in %s" % (tag, row["판정"], sorted(RESULT_VERDICTS)))
        for col in NUMERIC_COLUMNS:
            if row[col] != "-" and not NUM_RE.match(row[col]):
                errors.append("%s: %s %r must be a signed number or '-'" % (tag, col, row[col]))
        if row["판정"] not in ("invalid",):
            valid_ids.add(row["id"])
        if row["판정"] == "invalid" and not row["비고"]:
            errors.append("%s: invalid row needs a reason in 비고" % tag)

    interp = content.get("해석", "")
    cited = set(re.findall(r"R-\d{3}", interp))
    for rid in sorted(cited - all_ids):
        errors.append("해석: cites %s which is not in the result table" % rid)
    if valid_ids and not (cited & valid_ids):
        errors.append("해석: must cite at least one valid result row id (%s)" % ", ".join(sorted(valid_ids)))
    return errors


# ---------------------------------------------------------------- main

def validate(kind, path, root=None):
    store = SchemaStore()
    schema_path = os.path.join(SCHEMA_DIR, SCHEMAS[kind])
    schema = store.load(schema_path)
    with open(path, encoding="utf-8") as f:
        text = f.read()

    if kind == "card":
        try:
            data, body = split_card(text)
        except ValueError as e:
            return [str(e)]
        errors = check_schema(data, schema, store, schema_path)
        if not errors:
            errors += check_card_body(data, body)
        return errors

    data = yaml.safe_load(text)
    errors = check_schema(data, schema, store, schema_path)
    if kind == "flow_profile":
        root = root or data.get("flow_root")
    elif kind == "design_profile":
        root = root or data.get("design_root")
    if any(True for _ in iter_citations(data)):
        errors += check_citations(data, _resolve_root(root, path))
    return errors


def main(argv=None):
    ap = argparse.ArgumentParser(description="flow-bridge validator")
    ap.add_argument("kind", choices=sorted(SCHEMAS))
    ap.add_argument("file")
    ap.add_argument("--root", help="citation 기준 디렉토리 (contract용)")
    args = ap.parse_args(argv)
    if not os.path.isfile(args.file):
        print("ERROR: file not found: %s" % args.file)
        return 2
    try:
        errors = validate(args.kind, args.file, args.root)
    except (yaml.YAMLError, KeyError, ValueError) as e:
        print("ERROR: %s" % e)
        return 2
    if errors:
        print("FAIL %s (%s): %d issue(s)" % (args.file, args.kind, len(errors)))
        for e in errors:
            print("  - " + e)
        return 1
    print("PASS %s (%s)" % (args.file, args.kind))
    return 0


if __name__ == "__main__":
    sys.exit(main())
