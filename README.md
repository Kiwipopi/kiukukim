# kiukukim.com

스튜디오 김기욱 포트폴리오 사이트.

- `public/` — 사이트 파일 전체 (index.html, media/)
- `wrangler.jsonc` — Cloudflare 배포 설정. `main`에 올리면 자동 배포된다.

영상 원본은 이 저장소에 두지 않는다 (Cloudflare 파일당 25MB 제한). `public/media`에는 사이트용으로 줄인 영상만 둔다.

## 영어 · 일본어 페이지

`public/en/`, `public/ja/`는 손으로 고치지 않는다. 한국어 `public/index.html`을 고친 뒤 다음을 실행하면 다시 만들어진다.

    python3 tools/i18n/build.py

- `tools/i18n/strings.json` — [한국어, 영어, 일본어] 문구표. 새 한국어 문구를 넣었으면 여기에도 한 줄 추가한다.
- 작가 노트(Blast 설명문)는 `index.html`의 `STMT`에 세 언어가 함께 들어 있다.
- 실행 결과에 "남은 한글"이 나오면 그 문구가 표에 빠진 것이다.
