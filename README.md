# spacecatx-archive

spacecatx.me 워드프레스 글을 GitHub Actions로 매일 자동 동기화해서,
Claude가 fetch 없이 바로 읽을 수 있게 저장해두는 레포.

## 구조

posts/{slug}.md   AI가 읽기 편한 Markdown 버전
raw/{slug}.html   content.rendered 원본 HTML
index.json        전체 글 목록 요약 (id, slug, title, url, published, modified, excerpt)

## 세팅 방법 (최초 1회)

1. 이 파일들 커밋 후, GitHub Actions 탭 > Sync SpaceCatX Posts > Run workflow로 수동 실행
2. 정상 작동하면 posts/, raw/, index.json이 자동 생성되어 커밋됨
3. 이후 매일 새벽 1시(KST) 자동 실행, 변경 있을 때만 커밋

## MVP 범위에서 생략한 것

- 카테고리명 매핑
- 삭제/비공개 전환된 글 정리
- 인증이 필요한 비공개 글 수집
