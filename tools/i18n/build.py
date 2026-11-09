#!/usr/bin/env python3
"""한국어 public/index.html 에서 영어(public/en/)·일본어(public/ja/) 페이지를 만든다.

  python3 tools/i18n/build.py

- strings.json : [한국어, 영어, 일본어] 문구표. 긴 문구부터 바꾼다.
- 작가 노트(STMT)는 페이지 안에 세 언어가 모두 들어 있고, LANG 값만 바꾼다.
- 로고 글자(스튜디오 김기욱)는 모든 언어에서 그대로 둔다.
- 바꾸지 못한 한글이 남으면 줄 번호와 함께 알려 준다(주석은 무시).
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "public" / "index.html"
TABLE = json.loads((Path(__file__).parent / "strings.json").read_text(encoding="utf-8"))
HANGUL = re.compile(r"[가-힣]")
LOCALE = {"en": "en_US", "ja": "ja_JP"}
JP_FONT = "&family=IBM+Plex+Sans+JP:wght@400;500;600;700"


def build(lang: str, s: str) -> str:
    col = {"en": 1, "ja": 2}[lang]
    # 그대로 둘 부분을 잠시 가린다
    keep = []
    def mask(m):
        keep.append(m.group(0)); return f"\x00{len(keep) - 1}\x00"
    s = re.sub(r"const STMT = \{.*?\n\};\n", mask, s, flags=re.S)
    s = re.sub(r"<b>스튜디오 김기욱</b>", mask, s)
    s = re.sub(r'<div class="rt-col" lang="ko">.*?</div>', mask, s, flags=re.S)  # 국문 저작권 안내는 원문 그대로(페이지 언어에 따라 CSS가 숨김)

    for row in sorted(TABLE, key=lambda r: -len(r[0])):
        s = s.replace(row[0], row[col])
    s = re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], s)

    s = s.replace('const LANG = "ko";', f'const LANG = "{lang}";')
    s = s.replace('<html lang="ko">', f'<html lang="{lang}">')
    # 언어 전환 표시
    s = s.replace(' aria-current="page">KO</a>', '>KO</a>')
    s = s.replace(f'hreflang="{lang}" lang="{lang}">', f'hreflang="{lang}" lang="{lang}" aria-current="page">')
    # 주소: 하위 폴더에서도 같은 파일을 보도록 절대 경로로
    s = re.sub(r'(["`(])media/', r"\1/media/", s)
    for f in ("favicon-32.png", "favicon-192.png", "apple-touch-icon.png"):
        s = s.replace(f'href="{f}"', f'href="/{f}"')
    s = s.replace('<link rel="canonical" href="https://kiukukim.com/">', f'<link rel="canonical" href="https://kiukukim.com/{lang}/">')
    s = s.replace('<meta property="og:url" content="https://kiukukim.com/">', f'<meta property="og:url" content="https://kiukukim.com/{lang}/">')
    s = s.replace('<meta property="og:locale" content="ko_KR">', f'<meta property="og:locale" content="{LOCALE[lang]}">')
    if lang == "ja":
        s = s.replace("&family=IBM+Plex+Sans+KR:", JP_FONT + "&family=IBM+Plex+Sans+KR:")
    return s


def leftovers(s: str):
    s = re.sub(r"const STMT = \{.*?\n\};\n", lambda m: "\n" * m.group(0).count("\n"), s, flags=re.S)
    s = re.sub(r'<div class="rt-col" lang="ko">.*?</div>', "", s, flags=re.S)
    s = re.sub(r"/\*.*?\*/|<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), s, flags=re.S)
    out = []
    for i, line in enumerate(s.split("\n"), 1):
        code = re.sub(r"(^|\s)//.*$", "", line)
        code = code.replace("<b>스튜디오 김기욱</b>", "")
        if HANGUL.search(code):
            out.append((i, line.strip()[:160]))
    return out


if __name__ == "__main__":
    src = SRC.read_text(encoding="utf-8")
    bad = False
    for lang in ("en", "ja"):
        out = build(lang, src)
        dst = ROOT / "public" / lang / "index.html"
        dst.parent.mkdir(exist_ok=True)
        dst.write_text(out, encoding="utf-8")
        left = leftovers(out)
        print(f"{lang}: {dst.relative_to(ROOT)}  남은 한글 {len(left)}줄")
        for i, l in left:
            print(f"   {i}: {l}"); bad = True
    sys.exit(1 if bad and "--strict" in sys.argv else 0)
