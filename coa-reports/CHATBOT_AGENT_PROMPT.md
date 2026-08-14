# 챗봇 보고서 작업 프롬프트

아래 내용을 챗봇 프로젝트가 있는 작업 환경의 코딩 에이전트에게 전달합니다.

```text
현재 작업 폴더에는 서로 독립된 형제 저장소가 있다.

- chatbot/: 실제 엔코아 AI 캠퍼스 상담 챗봇 애플리케이션
- coa-reports/: 챗봇 공개용 HTML 보고서

이번 작업의 기본 변경 대상은 coa-reports만이다. 먼저 양쪽 저장소의 AGENTS.md, README와 현재 Git 상태를 확인하고, chatbot 저장소는 보고서 내용의 사실 확인을 위한 읽기 전용 근거로 사용한다. 내가 명시적으로 애플리케이션 변경을 요청하지 않는 한 chatbot 코드, 설정, 배포 파일과 데이터는 수정하지 않는다.

보고서 작업 규칙:

1. coa-reports/reports/chatbot/<보고서>/sections/가 원본이다. 생성 결과인 보고서 index.html은 직접 수정하지 않는다.
2. 현재 챗봇 코드와 설정을 근거로 서비스 구조, API, 데이터 흐름, 운영 절차를 확인한다. 추측한 내용은 사실처럼 쓰지 말고 확인되지 않은 항목으로 분리한다.
3. 개인정보, 실제 사용자 대화, API 키, DB 접속 문자열, 암호화 키, OAuth secret, PEM, 내부 전용 URL과 비밀 저장소 위치는 HTML·Markdown·Git에 기록하지 않는다.
4. 새 보고서를 추가하거나 제목·날짜를 바꾸면 coa-reports/index.html의 카드와 건수도 함께 갱신한다.
5. 이전 초안과 로컬 참고자료는 coa-reports/_local/에서만 사용하고 커밋 대상에 포함하지 않는다.
6. 작업 후 coa-reports에서 `python build.py`와 `python tools/check_site.py`를 실행한다. 생성된 dist/는 커밋하지 않는다.
7. 커밋·push·PR은 하지 않는다. 완료 시 변경 파일, 확인한 챗봇 근거 경로, 검증 결과와 남은 미확정 사항을 보고한다.

먼저 coa-reports/README.md와 기존 보고서를 읽고 현재 구조를 요약한 뒤, 내가 요청한 챗봇 보고서 작업을 이어서 수행하라.
```
