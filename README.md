# coa-reports

엔코아 AI 캠퍼스 상담 챗봇의 공개용 HTML 보고서를 관리하는 독립 저장소입니다.

실제 챗봇 애플리케이션 저장소와 이 저장소는 형제 폴더로 배치합니다.

```text
<작업 폴더>/
├─ chatbot/       실제 챗봇 애플리케이션
└─ coa-reports/   챗봇 보고서
```

## 편집 기준

- 보고서 원본은 `reports/chatbot/<보고서>/sections/`입니다.
- `00-shell.html`에는 문서 셸을, 번호가 붙은 나머지 파일에는 본문 섹션을 둡니다.
- 보고서의 `index.html`은 생성 결과이므로 직접 수정하지 않습니다.
- 챗봇 구현 근거가 필요하면 형제 폴더 `../chatbot`을 읽되, 보고서 작업 중 애플리케이션 코드는 임의로 변경하지 않습니다.
- 개인정보, 원문 대화, API 키, DB 접속정보, 암호화 키와 비공개 URL은 보고서와 Git에 넣지 않습니다.
- `_local/`은 이전 초안 등 로컬 참고자료 전용이며 Git에 포함하지 않습니다.

## 구조

```text
coa-reports/
├─ .github/workflows/pages.yml
├─ assets/index.css
├─ reports/chatbot/
│  └─ 2026-08-09_chatbot-service-report/
│     ├─ sections/
│     └─ index.html
├─ tools/check_site.py
├─ tools/import_report.py
├─ build.py
├─ index.html
└─ robots.txt
```

## 로컬 검증

```powershell
python build.py
python tools/check_site.py
python -m http.server 8000 --directory dist
```

브라우저에서 <http://127.0.0.1:8000/>을 엽니다.

## 새 보고서 추가

`reports/chatbot/<YYYY-MM-DD_보고서명>/sections/` 구조로 원본을 추가하고 루트 `index.html`에 보고서 카드를 추가합니다. 단일 HTML을 조각 구조로 변환할 때는 다음 도구를 사용할 수 있습니다.

```powershell
python tools/import_report.py `
  "C:\path\to\report.html" `
  "reports/chatbot/<YYYY-MM-DD_보고서명>"

python build.py
python tools/check_site.py
```

## GitHub Pages

`main`에 반영되면 `.github/workflows/pages.yml`이 `dist/`를 빌드·검증해 GitHub Pages에 배포합니다. 최초 한 번 저장소의 `Settings → Pages → Build and deployment → Source`를 `GitHub Actions`로 설정합니다.
