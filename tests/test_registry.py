"""Registry integrity + CLI smoke tests (pure stdlib, no network)."""

from __future__ import annotations

import json

import data
import report
import main as cli


def test_registry_nonempty():
    # Focused space — curated for accuracy, not padded.
    assert len(data.TOOLS) >= 7


def test_unique_names():
    names = [t.name for t in data.TOOLS]
    assert len(names) == len(set(names)), "duplicate names"


def test_every_entry_has_link_and_fields():
    for t in data.TOOLS:
        assert t.url.startswith("http"), f"{t.name} has no url"
        assert isinstance(t.category, data.Category)
        assert t.org.strip() and t.license.strip() and t.note.strip()


def test_oss_has_real_license():
    for t in data.TOOLS:
        if t.open_source:
            assert t.license != "Proprietary", f"{t.name} marked OSS but Proprietary license"


def test_report_generates_markdown():
    md = report.generate()
    assert md.startswith("<!-- AUTO-GENERATED")
    assert "# 🚦 LLM Gateways & Routers Directory" in md
    for label in {t.category.label for t in data.TOOLS}:
        assert f"### {label}" in md


def test_export_json_roundtrips():
    rows = [cli._to_dict(t) for t in data.TOOLS]
    back = json.loads(json.dumps(rows))
    assert len(back) == len(data.TOOLS)
    assert all("name" in r and "category" in r for r in back)


def test_cli_parser_builds():
    parser = cli.build_parser()
    ns = parser.parse_args(["list", "--open-source"])
    assert ns.func is cli.cmd_list and ns.open_source
    ns = parser.parse_args(["list", "--category", "managed_router_gateway"])
    assert ns.category == "managed_router_gateway"
    ns = parser.parse_args(["search", "litellm"])
    assert ns.func is cli.cmd_search
