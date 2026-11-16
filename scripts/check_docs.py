"""Check required community documents and repository-relative Markdown links."""
import posixpath
import re
from pathlib import Path
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "README.md", "README.tr.md", "CONTRIBUTING.md", "SUPPORT.md", "LICENSE", "THIRD-PARTY.md",
    ".github/PULL_REQUEST_TEMPLATE.md", ".github/ISSUE_TEMPLATE/config.yml",
    *(f"docs/{name}.md" for name in (
        "PROJECT_STATUS", "ARCHITECTURE", "BUILDING", "GPU_COMPATIBILITY", "TESTING", "KNOWN_ISSUES",
        "FIRST_CONTRIBUTION", "UPSTREAM-PROVENANCE", "SOCIAL_PREVIEW", "DOWNLOADS",
    )),
    *(f".github/ISSUE_TEMPLATE/{name}.yml" for name in (
        "bug", "gpu-compatibility", "performance", "visual-glitch", "feature"
    )),
}
INLINE = re.compile(r"\]\(\s*(?:<([^>]+)>|([^\s()]+))")
REFERENCE = re.compile(r"^\s{0,3}\[[^]]+\]:\s*(?:<([^>]+)>|(\S+))")
FENCE = re.compile(r"^\s{0,3}([~]{3,}|[\x60]{3,})")


def main():
    tracked = set(subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
                  .decode("utf-8").rstrip("\0").split("\0"))
    directories = {parent.as_posix() for path in tracked for parent in Path(path).parents}
    errors = [f"Missing required file {p}" for p in sorted(REQUIRED - tracked)]
    documents = sorted(p for p in tracked if p.endswith(".md") and (ROOT / p).is_file())
    for path in documents:
        fence = None
        for number, line in enumerate((ROOT / path).read_text(encoding="utf-8-sig").splitlines(), 1):
            marker = FENCE.match(line)
            if marker and not fence:
                fence = marker[1]
                continue
            if fence:
                if marker and marker[1].startswith(fence) and not line[marker.end():].strip():
                    fence = None
                continue
            for match in (*INLINE.finditer(line), *REFERENCE.finditer(line)):
                href = match[1] or match[2]
                url = urlsplit(href)
                if url.scheme or url.netloc or not url.path:
                    continue
                target = unquote(url.path)
                target = posixpath.normpath(posixpath.join(posixpath.dirname(path), target))
                if target not in tracked and target not in directories:
                    errors.append(f"{path}:{number}: missing local target {target}")
        if fence:
            errors.append(f"{path}: unterminated fenced code block")
    checklist = (ROOT / ".github/PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")
    if "## Change summary" not in checklist or "## Evidence" not in checklist or "- [ ]" not in checklist:
        errors.append("PR template needs summary, evidence and a checklist")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Checked {len(documents)} Markdown files and {len(REQUIRED)} required community files.")


if __name__ == "__main__":
    main()
