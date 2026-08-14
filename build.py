#!/usr/bin/env python3
"""보고서를 조립하고 GitHub Pages 배포 디렉터리를 만든다.

보고서 구조:

    reports/<project>/<report>/sections/00-shell.html
    reports/<project>/<report>/sections/01-*.html
    reports/<project>/<report>/index.html

00-shell.html의 ``<!--SECTIONS-->`` 자리에 번호가 붙은 조각을 파일명
순서대로 넣는다. 이후 저장소의 공개 파일만 dist/로 복사한다.
"""

from __future__ import annotations

import os
import shutil
import stat
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"
DIST = ROOT / "dist"
MARKER = "<!--SECTIONS-->"


def report_directories() -> list[Path]:
    return sorted(
        shell.parent.parent
        for shell in REPORTS.glob("**/sections/00-shell.html")
    )


def build_report(report_dir: Path) -> Path:
    sections_dir = report_dir / "sections"
    shell_path = sections_dir / "00-shell.html"
    shell = shell_path.read_text(encoding="utf-8")

    if MARKER not in shell:
        raise SystemExit(f"{shell_path.relative_to(ROOT)}에 {MARKER}가 없습니다.")

    fragments = sorted(
        path
        for path in sections_dir.glob("[0-9][0-9]-*.html")
        if path.name != "00-shell.html"
    )
    if not fragments:
        raise SystemExit(f"{sections_dir.relative_to(ROOT)}에 본문 조각이 없습니다.")

    body = "\n\n".join(
        path.read_text(encoding="utf-8").strip() for path in fragments
    )
    output = report_dir / "index.html"
    output.write_text(shell.replace(MARKER, body, 1), encoding="utf-8")
    print(
        f"조립: {output.relative_to(ROOT)} "
        f"({len(fragments)}개 섹션, {output.stat().st_size:,} bytes)"
    )
    return output


def resolve_targets(arguments: list[str]) -> list[Path]:
    available = report_directories()
    if not available:
        raise SystemExit("reports/ 아래에서 sections/00-shell.html을 찾지 못했습니다.")
    if not arguments:
        return available

    requested = (ROOT / arguments[0]).resolve()
    if requested not in available:
        choices = "\n".join(f"- {path.relative_to(ROOT)}" for path in available)
        raise SystemExit(f"보고서 경로를 찾지 못했습니다: {arguments[0]}\n{choices}")
    return [requested]


def remove_readonly(function, path: str, _error) -> None:
    """Windows에서 읽기 전용 속성이 붙은 빌드 폴더도 다시 만들 수 있게 한다."""
    os.chmod(path, stat.S_IWRITE)
    function(path)


def copy_public_site(outputs: list[Path]) -> None:
    if DIST.exists():
        shutil.rmtree(DIST, onerror=remove_readonly)
    DIST.mkdir()

    for filename in ("index.html", "robots.txt"):
        source = ROOT / filename
        if not source.exists():
            raise SystemExit(f"필수 공개 파일이 없습니다: {filename}")
        shutil.copy2(source, DIST / filename)

    assets = ROOT / "assets"
    if assets.exists():
        shutil.copytree(assets, DIST / "assets")

    for output in outputs:
        relative = output.relative_to(ROOT)
        destination = DIST / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output, destination)

    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    print(f"배포본: {DIST.relative_to(ROOT)}/")


def main() -> None:
    targets = resolve_targets(sys.argv[1:])

    # 특정 보고서를 요청해도 dist에는 누락이 없도록 다른 보고서의 기존 생성본을 포함한다.
    built = {build_report(path) for path in targets}
    outputs: list[Path] = []
    for report_dir in report_directories():
        output = report_dir / "index.html"
        if output not in built and not output.exists():
            output = build_report(report_dir)
        outputs.append(output)

    copy_public_site(outputs)


if __name__ == "__main__":
    main()
