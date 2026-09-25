"""Check deterministic packaging rules for the entlearn skill collection."""

from __future__ import annotations

import argparse
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

# Every skill directory that must exist, and the references each still requires.
REQUIRED_REFERENCES = {
    "using-entlearn": set(),
    "tuning-entlearn": set(),
    "interpreting-entlearn": set(),
    "debugging-entlearn": set(),
    "using-entlearn-advanced": set(),
}
DOCS_SITE_ENV = "ENTLEARN_DOCS_SITE"
DOCS_VERSION_ENV = "ENTLEARN_DOCS_VERSION"
# The public doc site the skills link to. This is fixed by where the site is published
# (GitHub Pages on the public code repo), never by the site_url a particular build used:
# a locally built site has a different site_url, and a doc link must still be checked
# against it.
DOCS_BASE_URL = "https://entropiclearning.github.io/entlearn/"
REFERENCE_PATTERN = re.compile(r"(?<![\w/])(references/[A-Za-z0-9._/-]+\.md)")
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
WEB_REPOSITORY_PATTERN = re.compile(
    r"(?:https?|git|ssh)://(?:git@)?(?:www[.])?"
    r"(?P<host>github[.]com|gitlab[.]com|bitbucket[.]org)/"
    r"(?P<owner>[A-Za-z0-9_.-]+)/(?P<repository>[A-Za-z0-9_.-]+)",
    re.IGNORECASE,
)
SSH_REPOSITORY_PATTERN = re.compile(
    r"(?:ssh://)?git@(?P<host>[A-Za-z0-9.-]+)[:/]"
    r"(?P<owner>[A-Za-z0-9_.-]+)/(?P<repository>[A-Za-z0-9_.-]+)",
    re.IGNORECASE,
)
AZURE_REPOSITORY_PATTERN = re.compile(
    r"https?://dev[.]azure[.]com/(?P<owner>[A-Za-z0-9_.-]+)/"
    r"(?P<project>[A-Za-z0-9_.-]+)/_git/(?P<repository>[A-Za-z0-9_.-]+)",
    re.IGNORECASE,
)
ALLOWED_REPOSITORIES = {
    ("github.com", "entropiclearning/entlearn"),
    ("github.com", "entropiclearning/entlearn_skills"),
    ("github.com", "entropiclearning/espa.jl"),
}
SENSITIVE_PATTERNS = {
    "absolute user-home path": re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+/"),
    "Delta-local URI": re.compile(r"(?:delta|worktree|scratch)(?:://)", re.IGNORECASE),
    "development branch name": re.compile(r"\bredesign-\d[A-Za-z0-9._-]*\b", re.IGNORECASE),
    "persisted thread identifier": re.compile(r"\bksQ[A-Za-z0-9_-]{20,}\b"),
    "private wiki-style identifier": re.compile(r"\b[A-Za-z0-9._-]+-wiki\b", re.IGNORECASE),
}


def frontmatter(path: Path) -> dict[str, str]:
    """Parse the small frontmatter subset used by this collection."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening YAML frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("missing closing YAML frontmatter delimiter") from error

    values: dict[str, str] = {}
    current: str | None = None
    for line in lines[1:end]:
        if line.startswith((" ", "\t")) and current is not None:
            values[current] = f"{values[current]} {line.strip()}".strip()
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        current = key.strip()
        values[current] = value.strip().strip("\"'")
    return values


def text_files() -> list[tuple[Path, str]]:
    """Return every UTF-8 text file under the repository root."""
    files: list[tuple[Path, str]] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        files.append((path, text))
    return files


def repository_sources(text: str) -> set[tuple[str, str]]:
    """Return normalised source-control repositories named in text."""
    sources: set[tuple[str, str]] = set()
    for pattern in (WEB_REPOSITORY_PATTERN, SSH_REPOSITORY_PATTERN):
        for match in pattern.finditer(text):
            repository = match.group("repository").removesuffix(".git")
            sources.add(
                (
                    match.group("host").casefold(),
                    f"{match.group('owner')}/{repository}".casefold(),
                )
            )
    for match in AZURE_REPOSITORY_PATTERN.finditer(text):
        repository = match.group("repository").removesuffix(".git")
        sources.add(
            (
                "dev.azure.com",
                f"{match.group('owner')}/{match.group('project')}/{repository}".casefold(),
            )
        )
    return sources


def repository_is_allowed(source: tuple[str, str]) -> bool:
    """Return whether a source-control repository is approved for publication."""
    return source in ALLOWED_REPOSITORIES


class DocsSite(NamedTuple):
    """A built mkdocs site: its on-disk root and the relative page paths it serves."""

    root: Path
    llms_relative: frozenset[str]


def _relative_page_path(path: str) -> str:
    """Strip a trailing ``index.md``/``index.html``/``/`` from a page path."""
    for suffix in ("index.md", "index.html"):
        if path.endswith(suffix):
            path = path[: -len(suffix)]
            break
    return path.rstrip("/")


def load_docs_site(site_dir: Path, version: str | None) -> DocsSite:
    """Load a built doc site's llms.txt.

    ``site_dir`` is a plain ``mkdocs build`` output, or a `mike`-deployed root holding
    one subdirectory per version; ``version`` selects the latter when present. The
    build's own ``site_url`` (which llms.txt's links are absolute under) need not match
    ``DOCS_BASE_URL`` - only the relative page paths below it matter here.
    """
    root = site_dir / version if version and (site_dir / version).is_dir() else site_dir
    llms_path = root / "llms.txt"
    if not llms_path.is_file():
        raise ValueError(
            f"{llms_path} is missing; build the doc site with mkdocs-llmstxt first"
        )
    urls = {
        url
        for url in MARKDOWN_LINK_PATTERN.findall(llms_path.read_text(encoding="utf-8"))
        if url.startswith(("http://", "https://"))
    }
    if not urls:
        raise ValueError(f"{llms_path} contains no page links")
    site_base = os.path.commonprefix(sorted(urls))
    site_base = site_base[: site_base.rfind("/") + 1]
    llms_relative = frozenset(_relative_page_path(url[len(site_base) :]) for url in urls)
    return DocsSite(root=root, llms_relative=llms_relative)


def doc_link_remainder(url: str, expected_version: str | None) -> str | None:
    """Strip ``DOCS_BASE_URL`` and its version segment from a public doc link.

    Returns ``None`` when ``url`` does not target the public docs base, or names a
    version other than ``expected_version`` (when one is given). Both cases are
    unresolved, not "not a doc link": a caller that already confirmed ``url`` starts
    with ``DOCS_BASE_URL`` must still treat a ``None`` result as a failure to resolve,
    never silently skip it.
    """
    if not url.startswith(DOCS_BASE_URL):
        return None
    rest = url[len(DOCS_BASE_URL) :]
    segment, _, remainder = rest.partition("/")
    if not segment or (expected_version is not None and segment != expected_version):
        return None
    return remainder


def doc_link_resolves(url: str, site: DocsSite, expected_version: str | None) -> bool:
    """Return whether a public doc link resolves to a built page or an llms.txt entry."""
    remainder = doc_link_remainder(url, expected_version)
    if remainder is None:
        return False
    if remainder and (site.root / remainder).is_file():
        return True  # a direct link to a built file, e.g. llms.txt itself
    relative = _relative_page_path(remainder)
    if relative in site.llms_relative:
        return True
    page = site.root / relative / "index.html" if relative else site.root / "index.html"
    return page.is_file()


class _AnchorParser(HTMLParser):
    """Collect the fragment targets of an HTML page: every ``id``, and ``<a name>``."""

    def __init__(self) -> None:
        super().__init__()
        self.anchors: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if value and (key == "id" or (tag == "a" and key == "name")):
                self.anchors.add(value)


def doc_anchor_resolves(url: str, site: DocsSite, expected_version: str | None) -> bool:
    """Return whether a doc link's ``#fragment`` names an element on its built HTML page.

    An llms.txt-only entry has no HTML page, so an anchor on it never resolves.
    """
    page_url, _, fragment = url.partition("#")
    remainder = doc_link_remainder(page_url, expected_version)
    if remainder is None:
        return False
    page = site.root / _relative_page_path(remainder) / "index.html"
    if not page.is_file():
        return False
    parser = _AnchorParser()
    parser.feed(page.read_text(encoding="utf-8"))
    return fragment in parser.anchors


def check(site_dir: Path | None = None, docs_version: str | None = None) -> list[str]:
    """Return every deterministic repository-rule and doc-link violation.

    ``site_dir`` and ``docs_version`` locate a built doc site (see ``load_docs_site``);
    when ``site_dir`` is omitted, doc links are left unchecked, as in CI for this repo,
    which does not build the code repo's site.
    """
    errors: list[str] = []
    descriptions: dict[str, str] = {}

    docs_site: DocsSite | None = None
    if site_dir is not None:
        try:
            docs_site = load_docs_site(site_dir, docs_version)
        except ValueError as error:
            errors.append(str(error))

    actual = {path.name for path in SKILLS.iterdir() if path.is_dir()}
    if actual != set(REQUIRED_REFERENCES):
        errors.append(
            f"skill directories differ: expected {sorted(REQUIRED_REFERENCES)}, "
            f"found {sorted(actual)}"
        )

    for name, expected_references in REQUIRED_REFERENCES.items():
        directory = SKILLS / name
        skill_file = directory / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"{skill_file.relative_to(ROOT)} is missing")
            continue

        try:
            metadata = frontmatter(skill_file)
        except ValueError as error:
            errors.append(f"{skill_file.relative_to(ROOT)}: {error}")
            continue

        if metadata.get("name") != name:
            errors.append(f"{skill_file.relative_to(ROOT)}: frontmatter name must be {name!r}")
        description = metadata.get("description", "").strip(" >|-")
        if not description:
            errors.append(f"{skill_file.relative_to(ROOT)}: description is missing")
        elif description in descriptions:
            errors.append(
                f"{skill_file.relative_to(ROOT)}: description duplicates "
                f"{descriptions[description]}"
            )
        else:
            descriptions[description] = str(skill_file.relative_to(ROOT))

        for relative in expected_references:
            if not (directory / relative).is_file():
                errors.append(f"{directory.relative_to(ROOT) / relative} is missing")

    repository_text = text_files()
    for path, text in repository_text:
        for label, pattern in SENSITIVE_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{path.relative_to(ROOT)} contains {label}")
        for host, repository in repository_sources(text):
            if not repository_is_allowed((host, repository)):
                errors.append(
                    f"{path.relative_to(ROOT)} links to unapproved repository {host}/{repository}"
                )

    markdown_files = [(path, text) for path, text in repository_text if path.suffix == ".md"]
    for path, text in markdown_files:
        if path.name == "SKILL.md":
            for reference in REFERENCE_PATTERN.findall(text):
                if not (path.parent / reference).is_file():
                    errors.append(
                        f"{path.relative_to(ROOT)} points to missing local reference {reference}"
                    )
        for target in MARKDOWN_LINK_PATTERN.findall(text):
            local_target, _, fragment = target.partition("#")
            if not local_target or local_target.startswith("mailto:"):
                continue
            if "://" in local_target:
                if not (docs_site and local_target.startswith(DOCS_BASE_URL)):
                    continue
                if not doc_link_resolves(local_target, docs_site, docs_version):
                    errors.append(
                        f"{path.relative_to(ROOT)} links to a doc page that does not "
                        f"exist on the built site: {target}"
                    )
                elif fragment and not doc_anchor_resolves(target, docs_site, docs_version):
                    errors.append(
                        f"{path.relative_to(ROOT)} links to an anchor that does not "
                        f"exist on the built page: {target}"
                    )
                continue
            if not (path.parent / local_target).is_file():
                errors.append(f"{path.relative_to(ROOT)} points to missing local link {target}")

    readme = ROOT / "README.md"
    if not readme.is_file():
        errors.append("README.md is missing")
    elif "entlearn-v" not in readme.read_text(encoding="utf-8"):
        errors.append("README.md does not state the compatibility-tag convention")
    if not (ROOT / "LICENSE").is_file():
        errors.append("LICENSE is missing")

    return errors


def main() -> int:
    """Print validation results and return a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--site-dir",
        type=Path,
        default=Path(os.environ[DOCS_SITE_ENV]) if DOCS_SITE_ENV in os.environ else None,
        help=f"built doc site directory to check doc links against (env {DOCS_SITE_ENV}); "
        "doc links are left unchecked when omitted",
    )
    parser.add_argument(
        "--docs-version",
        default=os.environ.get(DOCS_VERSION_ENV),
        help=f"targeted mike version, if site-dir holds one subdirectory per version "
        f"(env {DOCS_VERSION_ENV})",
    )
    args = parser.parse_args()

    errors = check(site_dir=args.site_dir, docs_version=args.docs_version)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(
        f"Checked {len(REQUIRED_REFERENCES)} skills and "
        f"{len(list(ROOT.rglob('*.md')))} Markdown files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
