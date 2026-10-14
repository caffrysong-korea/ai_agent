#!/usr/bin/env python3
"""flow-bridge tools 테스트 (가상 예시 기반). 실행: python3 tests/test_tools.py

의존성: PyYAML. tclsh가 있으면 생성된 readback tcl을 실제로 실행하는 테스트도 돈다.
"""
import argparse
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
FB_ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FB_ROOT, "tools"))

import yaml  # noqa: E402
import validate  # noqa: E402
import readback  # noqa: E402

EX = os.path.join(FB_ROOT, "examples")
FIX = os.path.join(HERE, "fixtures")
CARD = os.path.join(EX, "cards", "DTCO-0001_useful_skew.md")
PLACEMENT = os.path.join(EX, "placement.example.yaml")


def quiet(fn, *a, **kw):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = fn(*a, **kw)
    return rc, buf.getvalue()


class TempDirCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="fbtest_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, name, text):
        path = os.path.join(self.tmp, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path


# ---------------------------------------------------------------- validate

class TestValidateExamples(unittest.TestCase):
    """가상 예시는 전부 통과해야 한다."""

    def test_flow_profile(self):
        self.assertEqual(validate.validate("flow_profile", os.path.join(EX, "flow_profile.example.yaml")), [])

    def test_design_profile(self):
        self.assertEqual(validate.validate("design_profile", os.path.join(EX, "design_profile.example.yaml")), [])

    def test_card(self):
        self.assertEqual(validate.validate("card", CARD), [])

    def test_stage2(self):
        root = os.path.join(EX, "synthetic_flow")
        self.assertEqual(validate.validate("stage2", PLACEMENT, root=root), [])


class TestValidateCatchesErrors(TempDirCase):

    def _flow_profile_with(self, old, new):
        with open(os.path.join(EX, "flow_profile.example.yaml"), encoding="utf-8") as f:
            text = f.read()
        self.assertIn(old, text)
        text = text.replace(old, new, 1).replace(
            "flow_root: examples/synthetic_flow", "flow_root: %s" % os.path.join(EX, "synthetic_flow"))
        return self.write("fp.yaml", text)

    def _card_with(self, old, new):
        with open(CARD, encoding="utf-8") as f:
            text = f.read()
        self.assertIn(old, text)
        return self.write("card.md", text.replace(old, new, 1))

    def test_hallucinated_citation_line(self):
        # useful skew 설정은 settings.tcl:12 에 있다. 13으로 주장하면 거짓 인용.
        path = self._flow_profile_with(
            'line: 12, excerpt: "-usefulSkew true"', 'line: 13, excerpt: "-usefulSkew true"')
        errors = validate.validate("flow_profile", path)
        self.assertTrue(any("excerpt" in e and "not found" in e for e in errors), errors)

    def test_cited_file_missing(self):
        path = self._flow_profile_with("file: stages/03_place.tcl, line: 3", "file: stages/99_nope.tcl, line: 3")
        errors = validate.validate("flow_profile", path)
        self.assertTrue(any("cited file not found" in e for e in errors), errors)

    def test_schema_enum_violation(self):
        path = self._flow_profile_with("ui_mode: legacy", "ui_mode: classic")
        errors = validate.validate("flow_profile", path)
        self.assertTrue(any("ui_mode" in e for e in errors), errors)

    def test_card_section_order(self):
        path = self._card_with("## 해석", "## 해석X")
        errors = validate.validate("card", path)
        self.assertTrue(any("sections must be" in e for e in errors), errors)

    def test_card_row_not_sequential(self):
        path = self._card_with("| R-002 |", "| R-005 |")
        errors = validate.validate("card", path)
        self.assertTrue(any("id must be R-002" in e for e in errors), errors)

    def test_card_interpretation_cites_unknown_row(self):
        path = self._card_with("(유효 결과 행 1개: R-001)", "(유효 결과 행 1개: R-009)")
        errors = validate.validate("card", path)
        self.assertTrue(any("R-009" in e for e in errors), errors)

    def test_card_unknown_frontmatter_field(self):
        path = self._card_with("stage: post_cts\n", "stage: post_cts\nmagic: 1\n")
        errors = validate.validate("card", path)
        self.assertTrue(any("unexpected field 'magic'" in e for e in errors), errors)

    def test_card_invalid_row_needs_reason(self):
        path = self._card_with("| confounded: place_global_cong_effort medium→high 동시 변경 |", "|  |")
        errors = validate.validate("card", path)
        self.assertTrue(any("needs a reason" in e for e in errors), errors)

    def test_unsupported_schema_keyword_fails_fast(self):
        store = validate.SchemaStore()
        errors = validate.check_schema("x", {"type": "string", "minLength": 3}, store, "inline")
        self.assertTrue(any("unsupported schema keyword" in e for e in errors), errors)


# ---------------------------------------------------------------- readback

class TestReadback(TempDirCase):

    def _gen(self, placement=PLACEMENT, cards=os.path.join(EX, "cards")):
        out = os.path.join(self.tmp, "rb")
        args = argparse.Namespace(
            placement=placement, cards=cards, out=out, variant=None)
        rc, _ = quiet(readback.cmd_gen, args)
        return rc, out

    def _judge(self, out, log):
        result = os.path.join(self.tmp, "result.yaml")
        rc, text = quiet(readback.main, ["judge", "--expect", os.path.join(out, "expect.yaml"),
                                         "--log", log, "--out", result])
        with open(result, encoding="utf-8") as f:
            rows = yaml.safe_load(f)["readback"]
        return rc, {r["stage"]: r["status"] for r in rows}, text

    def test_gen_creates_stage_files(self):
        rc, out = self._gen()
        self.assertEqual(rc, 0)
        for stage in ("post_cts", "route", "post_route"):
            self.assertTrue(os.path.isfile(os.path.join(out, "readback_%s.tcl" % stage)))
        with open(os.path.join(out, "expect.yaml"), encoding="utf-8") as f:
            exp = yaml.safe_load(f)
        self.assertEqual(exp["entries"][0]["key"], "DTCO-0001.1")
        self.assertEqual(exp["entries"][0]["expect"], "true")

    def test_override_detected(self):
        """핵심 케이스: post_cts/route에서는 켜져 있다가 post_route에서 design override로 꺼짐."""
        _, out = self._gen()
        rc, status, _ = self._judge(out, os.path.join(FIX, "run_blkA_override.txt"))
        self.assertEqual(status, {"post_cts": "applied", "route": "applied", "post_route": "overridden"})
        self.assertEqual(rc, 1)

    def test_missing_stage_and_bool_normalization(self):
        _, out = self._gen()
        rc, status, text = self._judge(out, os.path.join(FIX, "run_missing_stage.txt"))
        self.assertEqual(status["post_cts"], "applied")  # "1" == "true"
        self.assertEqual(status["route"], "missing")
        self.assertEqual(status["post_route"], "missing")
        self.assertIn("probably not sourced", text)
        self.assertEqual(rc, 1)

    def test_readback_error_is_not_checkable(self):
        _, out = self._gen()
        rc, status, _ = self._judge(out, os.path.join(FIX, "run_readback_error.txt"))
        self.assertEqual(status["post_route"], "not_checkable")
        self.assertEqual(rc, 0)

    def test_stale_card_version_rejected(self):
        with open(PLACEMENT, encoding="utf-8") as f:
            text = f.read().replace("item_version: 1", "item_version: 2")
        rc, _ = self._gen(placement=self.write("placement_v2.yaml", text))
        self.assertEqual(rc, 2)

    @unittest.skipUnless(shutil.which("tclsh"), "tclsh not available")
    def test_generated_tcl_runs_end_to_end(self):
        """생성된 tcl을 실제 Tcl로 실행 → 로그 → judge 까지 한 번에."""
        _, out = self._gen()
        driver = self.write("drive.tcl", "\n".join([
            "set ::uskew true",
            "proc getOptMode {opt} { return $::uskew }",
            "source %s/readback_post_cts.tcl" % out,
            "source %s/readback_route.tcl" % out,
            "set ::uskew false",
            "source %s/readback_post_route.tcl" % out,
        ]) + "\n")
        log = os.path.join(self.tmp, "run.txt")
        with open(log, "w") as f:
            subprocess.check_call(["tclsh", driver], stdout=f)
        _, status, _ = self._judge(out, log)
        self.assertEqual(status, {"post_cts": "applied", "route": "applied", "post_route": "overridden"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
