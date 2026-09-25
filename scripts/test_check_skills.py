"""Tests for publication-boundary checks."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.check_skills import (
    DOCS_BASE_URL,
    ROOT,
    check,
    doc_link_resolves,
    load_docs_site,
    repository_is_allowed,
    repository_sources,
)

# The build's own site_url - deliberately NOT DOCS_BASE_URL. A local build publishes
# llms.txt under its own site_url; skills always link to DOCS_BASE_URL regardless. The
# checker must resolve one against the other rather than requiring them to match.
BUILD_SITE_URL = "https://example.github.io/entlearn-build/"
VERSION = "0.1.0"


def build_site(root: Path, site_url: str = BUILD_SITE_URL) -> Path:
    """Write a minimal built doc site (one page, one llms.txt) under ``root``."""
    page = root / "guide" / "estimators"
    page.mkdir(parents=True)
    (page / "index.html").write_text(
        '<html><h2 id="refit-and-reuse">Refit and reuse</h2></html>', encoding="utf-8"
    )
    (root / "llms.txt").write_text(
        f"# Entlearn\n\n- [Estimators]({site_url}guide/estimators/index.md)\n"
        f"- [Concepts]({site_url}concepts/index.md)\n",
        encoding="utf-8",
    )
    return root


def doc_link(relative: str, version: str = VERSION) -> str:
    """Build a public doc-site link, as a skill would write one."""
    return f"{DOCS_BASE_URL}{version}/{relative}"


class RepositorySourceTests(unittest.TestCase):
    """Exercise accepted and rejected source-control URL forms."""

    def test_approved_public_repository(self) -> None:
        """Accept every common URL form for an approved repository."""
        repository = "EntropicLearning/" + "entlearn"
        sources = (
            "https://" + "github.com/" + repository,
            "http://www." + "github.com/" + repository,
            "git@" + "github.com:" + repository + ".git",
            "ssh://git@" + "github.com/" + repository + ".git",
        )
        for text in sources:
            with self.subTest(text=text):
                found = repository_sources(text)
                self.assertEqual(len(found), 1)
                self.assertTrue(repository_is_allowed(found.pop()))

    def test_private_repository_forms_are_rejected(self) -> None:
        """Reject common URL forms for a repository outside the allowlist."""
        repository = "private-" + "owner/private-" + "repo"
        sources = (
            "http://" + "github.com/" + repository,
            "https://www." + "github.com/" + repository,
            "git@" + "github.com:" + repository + ".git",
            "ssh://git@" + "github.com/" + repository + ".git",
            "https://" + "gitlab.com/" + repository,
            "git@" + "internal.example:" + repository + ".git",
            "https://dev." + "azure.com/private-owner/project/_git/private-repo",
        )
        for text in sources:
            with self.subTest(text=text):
                found = repository_sources(text)
                self.assertEqual(len(found), 1)
                self.assertFalse(repository_is_allowed(found.pop()))
                with patch(
                    "scripts.check_skills.text_files",
                    return_value=[(ROOT / "negative-fixture.txt", text)],
                ):
                    self.assertTrue(any("unapproved repository" in error for error in check()))


class DocLinkTests(unittest.TestCase):
    """Exercise doc-link resolution against a built site and its llms.txt."""

    def test_page_link_resolves(self) -> None:
        """A link to a page the site actually built resolves."""
        with tempfile.TemporaryDirectory() as tmp:
            site = load_docs_site(build_site(Path(tmp)), version=None)
            self.assertTrue(
                doc_link_resolves(doc_link("guide/estimators/index.md"), site, VERSION)
            )

    def test_llms_txt_only_entry_resolves(self) -> None:
        """A link with no built HTML page but an llms.txt entry still resolves."""
        with tempfile.TemporaryDirectory() as tmp:
            site = load_docs_site(build_site(Path(tmp)), version=None)
            self.assertTrue(doc_link_resolves(doc_link("concepts/index.md"), site, VERSION))

    def test_broken_link_does_not_resolve(self) -> None:
        """A link to neither a built page nor an llms.txt entry fails."""
        with tempfile.TemporaryDirectory() as tmp:
            site = load_docs_site(build_site(Path(tmp)), version=None)
            self.assertFalse(doc_link_resolves(doc_link("guide/nonexistent/"), site, VERSION))

    def test_direct_file_link_resolves(self) -> None:
        """A link straight to a built file (e.g. llms.txt itself) resolves."""
        with tempfile.TemporaryDirectory() as tmp:
            site = load_docs_site(build_site(Path(tmp)), version=None)
            self.assertTrue(doc_link_resolves(doc_link("llms.txt"), site, VERSION))

    def test_wrong_version_segment_does_not_resolve(self) -> None:
        """A link pinned to a version other than the one targeted fails, not skips."""
        with tempfile.TemporaryDirectory() as tmp:
            site = load_docs_site(build_site(Path(tmp)), version=None)
            link = doc_link("guide/estimators/", version="9.9.9")
            self.assertFalse(doc_link_resolves(link, site, VERSION))

    def test_build_site_url_need_not_match_public_docs_base(self) -> None:
        """Reproduces the reported bug: a build's own site_url differs from the
        public docs base the skills link to, so base_url-matching silently skipped
        every doc link. A doc-site link must still be checked - and rejected here,
        since the site never built this page - against the built site's pages,
        independent of what site_url the build itself used.
        """
        with tempfile.TemporaryDirectory() as tmp:
            site = load_docs_site(build_site(Path(tmp), site_url=BUILD_SITE_URL), version=None)
            self.assertFalse(
                doc_link_resolves(doc_link("guide/no-such-page/"), site, VERSION)
            )
            self.assertTrue(
                doc_link_resolves(doc_link("guide/estimators/"), site, VERSION)
            )

    def test_check_is_red_then_green_on_a_doc_link(self) -> None:
        """check() fails on a broken doc link and passes once it is fixed - and does
        so even though the built site's own site_url differs from the public docs
        base the link uses (the reported bug: this used to be silently skipped)."""
        with tempfile.TemporaryDirectory() as tmp:
            site_dir = build_site(Path(tmp), site_url=BUILD_SITE_URL)
            skill = ROOT / "skills" / "using-entlearn" / "SKILL.md"
            broken = (skill, f"[bad]({doc_link('guide/no-such-page/')})")
            fixed = (skill, f"[ok]({doc_link('guide/estimators/')})")
            with patch("scripts.check_skills.text_files", return_value=[broken]):
                errors = check(site_dir=site_dir, docs_version=VERSION)
                self.assertTrue(
                    any("does not exist on the built site" in error for error in errors)
                )
            with patch("scripts.check_skills.text_files", return_value=[fixed]):
                errors = check(site_dir=site_dir, docs_version=VERSION)
                self.assertFalse(
                    any("does not exist on the built site" in error for error in errors)
                )

    def test_missing_anchor_fails(self) -> None:
        """A link to a built page whose #fragment names no element on it fails."""
        with tempfile.TemporaryDirectory() as tmp:
            site_dir = build_site(Path(tmp))
            skill = ROOT / "skills" / "using-entlearn" / "SKILL.md"
            link = (skill, f"[bad]({doc_link('guide/estimators/#no-such-anchor')})")
            with patch("scripts.check_skills.text_files", return_value=[link]):
                errors = check(site_dir=site_dir, docs_version=VERSION)
            self.assertTrue(any("#no-such-anchor" in error for error in errors))

    def test_present_anchor_passes(self) -> None:
        """A link whose #fragment names an element id on the built page passes."""
        with tempfile.TemporaryDirectory() as tmp:
            site_dir = build_site(Path(tmp))
            skill = ROOT / "skills" / "using-entlearn" / "SKILL.md"
            link = (skill, f"[ok]({doc_link('guide/estimators/#refit-and-reuse')})")
            with patch("scripts.check_skills.text_files", return_value=[link]):
                errors = check(site_dir=site_dir, docs_version=VERSION)
            self.assertFalse(any("#refit-and-reuse" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
