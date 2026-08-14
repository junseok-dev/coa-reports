#!/usr/bin/env python3
"""dist의 공개 범위와 HTML 내부 링크를 검사한다."""

from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
ALLOWED_TOP_LEVEL = {".nojekyll", "assets", "index.html", "reports", "robots.txt"}
MARKER = "<!--SECTIONS-->"


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.links: list[str] = []

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            if element_id in self.ids:
                self.duplicate_ids.add(element_id)
            self.ids.add(element_id)
        href = values.get("href")
        if href:
            self.links.append(href)


def destination_for(document: Path, href: str) -> tuple[Path, str]:
    parsed = urlsplit(href)
    fragment = unquote(parsed.fragment)
    if not parsed.path:
        return document, fragment

    destination = (document.parent / unquote(parsed.path)).resolve()
    if parsed.path.endswith("/") or destination.is_dir():
        destination /= "index.html"
    return destination, fragment


def check_document(path: Path, errors: list[str]) -> None:
    source = path.read_text(encoding="utf-8")
    if MARKER in source:
        errors.append(f"조립 마커가 남아 있습니다: {path.relative_to(DIST)}")

    parser = DocumentParser()
    parser.feed(source)
    if parser.duplicate_ids:
        errors.append(
            f"중복 ID: {path.relative_to(DIST)}: {sorted(parser.duplicate_ids)}"
        )

    for href in parser.links:
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc or href.startswith(("mailto:", "tel:")):
            continue
        destination, fragment = destination_for(path, href)
        if not destination.is_file():
            errors.append(f"깨진 링크: {path.relative_to(DIST)} → {href}")
            continue
        if fragment:
            target_parser = DocumentParser()
            target_parser.feed(destination.read_text(encoding="utf-8"))
            if fragment not in target_parser.ids:
                errors.append(
                    f"없는 앵커: {path.relative_to(DIST)} → {href}"
                )


def main() -> None:
    if not DIST.is_dir():
        raise SystemExit("dist/가 없습니다. python build.py를 먼저 실행하세요.")

    unexpected = sorted(path.name for path in DIST.iterdir() if path.name not in ALLOWED_TOP_LEVEL)
    errors = [f"허용되지 않은 최상위 공개 항목: {unexpected}"] if unexpected else []

    documents = sorted(DIST.rglob("*.html"))
    if not documents:
        errors.append("공개 HTML이 없습니다.")
    for document in documents:
        check_document(document, errors)

    if errors:
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        raise SystemExit(1)

    print(f"검증 완료: HTML {len(documents)}개, 공개 최상위 항목 {len(list(DIST.iterdir()))}개")


if __name__ == "__main__":
    main()

