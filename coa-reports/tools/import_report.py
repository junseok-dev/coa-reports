#!/usr/bin/env python3
"""완성된 단일 HTML 보고서를 sections 기반 보고서로 변환한다."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


MARKER = "<!--SECTIONS-->"
MAIN_PATTERN = re.compile(
    r'(?P<open><main\b[^>]*class=["\'][^"\']*\bcontent\b[^"\']*["\'][^>]*>)'
    r"(?P<body>.*?)"
    r"(?P<close></main>)",
    re.IGNORECASE | re.DOTALL,
)
SECTION_PATTERN = re.compile(r"<section\b.*?</section>", re.IGNORECASE | re.DOTALL)
ID_PATTERN = re.compile(r'<section\b[^>]*\bid=["\']([^"\']+)["\']', re.IGNORECASE)
NUMBER_PATTERN = re.compile(r"<h2\b[^>]*>\s*(\d+)\.", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="단일 HTML의 main.content 섹션을 보고서 조각으로 분리합니다."
    )
    parser.add_argument("source", type=Path, help="원본 HTML 파일")
    parser.add_argument("destination", type=Path, help="생성할 보고서 폴더")
    return parser.parse_args()


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z가-힣_-]+", "-", value).strip("-")
    return cleaned or "section"


def main() -> None:
    args = parse_args()
    source = args.source.resolve()
    destination = args.destination.resolve()
    sections_dir = destination / "sections"

    if not source.is_file():
        raise SystemExit(f"원본 HTML을 찾지 못했습니다: {source}")
    if destination.exists() and any(destination.iterdir()):
        raise SystemExit(f"대상 폴더가 비어 있지 않습니다: {destination}")

    html = source.read_text(encoding="utf-8")
    main_match = MAIN_PATTERN.search(html)
    if not main_match:
        raise SystemExit('원본에서 <main class="content">를 찾지 못했습니다.')

    main_body = main_match.group("body")
    section_matches = list(SECTION_PATTERN.finditer(main_body))
    if not section_matches:
        raise SystemExit("main.content 안에서 section을 찾지 못했습니다.")

    parsed: list[tuple[int, str, str]] = []
    for fallback, section_match in enumerate(section_matches, 1):
        section = section_match.group(0)
        id_match = ID_PATTERN.search(section)
        number_match = NUMBER_PATTERN.search(section)
        section_id = id_match.group(1) if id_match else f"section-{fallback}"
        number = int(number_match.group(1)) if number_match else fallback
        parsed.append((number, safe_name(section_id), section.strip()))

    numbers = [number for number, _, _ in parsed]
    if len(numbers) != len(set(numbers)):
        raise SystemExit("중복된 h2 번호가 있어 섹션 순서를 결정할 수 없습니다.")

    sections_dir.mkdir(parents=True, exist_ok=True)
    before_sections = main_body[: section_matches[0].start()]
    after_sections = main_body[section_matches[-1].end() :]
    shell = (
        html[: main_match.start("body")]
        + before_sections
        + "\n"
        + MARKER
        + "\n"
        + after_sections
        + html[main_match.end("body") :]
    )
    (sections_dir / "00-shell.html").write_text(shell, encoding="utf-8")

    for number, section_id, section in sorted(parsed):
        path = sections_dir / f"{number:02d}-{section_id}.html"
        path.write_text(section + "\n", encoding="utf-8")
        print(f"생성: {path}")

    print(f"생성: {sections_dir / '00-shell.html'}")


if __name__ == "__main__":
    main()
