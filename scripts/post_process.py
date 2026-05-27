#!/usr/bin/env python3
"""Post-process briefing article pages with reader-mode chrome and heroes.

API keys are not required. Hero images are selected from a handpicked,
deterministic Unsplash CDN image map.
"""

from __future__ import annotations

import hashlib
import json
import re
from html import escape
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


ARCHIVE_DIR = Path("briefing/archive")
BRIEFINGS_JSON = Path("briefing/briefings.json")

CATEGORY_PATTERNS = [
    # (카테고리 키, regex 패턴)
    ("ai",          r'AI|인공지능|LLM|ChatGPT|Gemini|Claude|Grok|딥러닝|머신러닝|GPT|오픈AI|OpenAI|Anthropic'),
    ("chip",        r'반도체|칩|HBM|TSMC|SK하이닉스|하이닉스|마이크론|Micron|NVIDIA|엔비디아|삼성전자|파운드리|웨이퍼'),
    ("finance",     r'주식|증시|S&P|나스닥|시총|IPO|상장|월가|투자|채권|금리|연준|Fed|주가|코스피|다우'),
    ("robot",       r'로봇|휴머노이드|Unitree|보스턴다이내믹스|Figure|Agility|자동화|드론'),
    ("space",       r'우주|SpaceX|스타링크|Starlink|위성|로켓|발사|NASA|스타십|Starship|ISS'),
    ("health",      r'헬스|의료|Fitbit|웨어러블|건강|바이오|임상|FDA|제약|스마트워치|애플워치'),
    ("ev",          r'전기차|EV|배터리|Tesla|테슬라|리비안|BYD|충전|전동화|자율주행'),
    ("economy",     r'무역|관세|수출|수입|경제|글로벌|GDP|인플레|관세|공급망|달러|환율'),
]

# post_process.py 내 상단 상수로 선언
BASE = "https://images.unsplash.com/photo-"
PARAMS_LG = "?w=1200&q=80&fit=crop&auto=format"
PARAMS_SM = "?w=640&q=80&fit=crop&auto=format"

def _img(photo_id, alt, credit_name, credit_slug):
    return {
        "url":         BASE + photo_id + PARAMS_LG,
        "url_small":   BASE + photo_id + PARAMS_SM,
        "alt":         alt,
        "credit_name": credit_name,
        "credit_url":  f"https://unsplash.com/photos/{photo_id}",
    }

CATEGORY_IMAGE_MAP = {

    # ── AI / 인공지능 ─────────────────────────────────────────────
    "ai": [
        _img("1677442135703-1787eea5ce01",
             "Blue neural network visualization on dark background",
             "Growtika", "growtika"),
        _img("1620712943543-bcc4688e7485",
             "Humanoid robot face with silver metallic surface",
             "Possessed Photography", "possessedphotography"),
        _img("1526378722484-bd91ca387e72",
             "Robot hand reaching through digital interface",
             "Franck V.", "franckinjapan"),
        _img("1655720828018-edd2daec9349",
             "Abstract AI data streams in deep blue",
             "Steve Johnson", "steve_j"),
    ],

    # ── 반도체 / 칩 ──────────────────────────────────────────────
    "chip": [
        _img("1518770660439-4636190af475",
             "Close-up of blue printed circuit board",
             "Alexandre Debiève", "alexkixa"),
        _img("1563770557593-f9e36f476dc8",
             "Silicon semiconductor wafer under purple light",
             "Laura Ockel", "lauraockel"),
        _img("1591696331111-ef9586a5b17a",
             "Macro shot of CPU processor chip",
             "Slejven Djurakovic", "slavudin"),
        _img("1601004890684-d8cbf643f5f2",
             "Intel microprocessor on motherboard close-up",
             "Olivier Collet", "olivier_collet"),
    ],

    # ── 주식 / 금융 ──────────────────────────────────────────────
    "finance": [
        _img("1611974789855-9c2a0a7236a3",
             "Stock market candlestick chart on dark screen",
             "Maxim Hopman", "nampoh"),
        _img("1590283603385-17ffb3a7f29f",
             "Charging Bull bronze statue on Wall Street",
             "Konstantin Evdokimov", "konstantinv"),
        _img("1579621970563-ebec7560ff3e",
             "Financial data graph with upward trend on dark background",
             "Tech Daily", "techdailyca"),
        _img("1638913971789-f64cf5acac09",
             "Multiple trading monitors showing financial data",
             "Austin Distel", "austindistel"),
    ],

    # ── 로봇 / 휴머노이드 ─────────────────────────────────────────
    "robot": [
        _img("1485827404703-89b55fcc595e",
             "White humanoid robot standing against grey background",
             "Alex Knight", "agk42"),
        _img("1535378917042-10a22c95931a",
             "Industrial robotic arm in dark factory",
             "Lenny Kuhne", "lennykuhne"),
        _img("1561144257-e32e8efc6c4f",
             "Robotic arm welding with sparks in dark setting",
             "Ant Rozetsky", "rozetsky"),
        _img("1508614589041-895b88991e3e",
             "Futuristic robot head with glowing eyes",
             "Possessed Photography", "possessedphotography"),
    ],

    # ── 우주 / SpaceX / 위성 ─────────────────────────────────────
    "space": [
        _img("1446776811953-b23d57bd21aa",
             "Earth from orbit with blue atmosphere",
             "NASA", "nasa"),
        _img("1516849841032-87cbac4d88f7",
             "Rocket launching with bright exhaust flame at night",
             "SpaceX", "spacex"),
        _img("1454789548928-701522940945",
             "Milky Way galaxy with stars over dark landscape",
             "Greg Rakozy", "grakozy"),
        _img("1614730321146-b6fa6a46bcb4",
             "Nebula and stars in deep space",
             "Jeremy Thomas", "jeremythomasphoto"),
    ],

    # ── 헬스케어 / 웨어러블 ──────────────────────────────────────
    "health": [
        _img("1576091160399-112ba8d25d1d",
             "Medical professional using digital health tablet",
             "National Cancer Institute", "nci"),
        _img("1559757148-5c350d0d3c56",
             "DNA strand and biotechnology research visualization",
             "Warren Umoh", "warrenumoh"),
        _img("1576671081837-49000212a223",
             "Smart wearable health monitoring device on wrist",
             "Luke Chesser", "lukechesser"),
        _img("1505751172876-fa1923c5c528",
             "Doctor reviewing digital patient data on screen",
             "Online Marketing", "impulsq"),
    ],

    # ── 전기차 / EV ───────────────────────────────────────────────
    "ev": [
        _img("1593941707882-a5bba14938c7",
             "Electric vehicle charging port glowing blue",
             "dcbel", "dcbel"),
        _img("1558618666-fcd25c85cd64",
             "Red Tesla Model S on mountain road",
             "Charlie Deets", "charliedeets"),
        _img("1617788138017-80ad40651399",
             "EV charging station with multiple connectors",
             "Juice Flair", "juiceflair"),
        _img("1603584173870-7f23fdae1b7a",
             "Modern electric vehicle interior dashboard at night",
             "Jp Valery", "jpvalery"),
    ],

    # ── 무역 / 글로벌 경제 ───────────────────────────────────────
    "economy": [
        _img("1553729459-efe14ef6055d",
             "Container cargo ship at ocean port",
             "Channey", "channey"),
        _img("1486406146926-c627a92ad1ab",
             "Glass skyscrapers of financial district",
             "Sean Pollock", "seanpollock"),
        _img("1454165804606-c3d57bc86b40",
             "Business professionals in meeting room",
             "Cytonn Photography", "cytonn_photography"),
        _img("1494412574643-ff11b0a5c1c3",
             "Aerial view of cargo containers at port terminal",
             "Tom Fisk", "tomfisk"),
    ],
}

# ── 기본 풀 (카테고리 미매칭 시) ────────────────────────────────
DEFAULT_IMAGE_POOL = [
    _img("1504711434969-e33886168f5c",
         "Aerial view of city lights at night in blue tones",
         "Maximalfocus", "maximalfocus"),
    _img("1451187580459-43490279c0fa",
         "Planet Earth seen from space with city lights",
         "NASA", "nasa"),
    _img("1498050108023-c5249f4df085",
         "Laptop with code on screen in dark environment",
         "Christopher Gower", "cgower"),
    _img("1522071820081-009f0129c71c",
         "Team working on laptops in modern office",
         "Annie Spratt", "anniespratt"),
]

GNB_HTML = """<nav class="reader-nav">
  <div class="reader-nav-inner">
    <a href="../index.html" class="reader-nav-logo">JFNB</a>
    <div class="reader-nav-links">
      <a href="../index.html">홈</a>
      <a href="../archive.html">아카이브</a>
      <a href="../about.html">소개</a>
    </div>
  </div>
</nav>"""

FOOTER_HTML = """<footer class="reader-footer">
  <a href="../archive.html">← 아카이브로 돌아가기</a>
</footer>"""


def select_from_pool(pool: list, date_str: str) -> dict:
    """날짜 해시 기반 결정론적 선택 (§6-4 알고리즘)."""
    index = int(hashlib.md5(date_str.encode("utf-8")).hexdigest(), 16) % len(pool)
    return pool[index]


def parse_dimension(value: Any) -> int | None:
    if value is None:
        return None
    match = re.search(r"\d+", str(value))
    return int(match.group(0)) if match else None


def find_article_image(soup: BeautifulSoup) -> dict | None:
    """Priority 1: 기사 본문 내 이미지 탐색 및 히어로 승격."""
    BLOCKED = re.compile(r'icon|logo|badge|emoji|bullet|arrow|avatar', re.I)
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src or BLOCKED.search(src):
            continue
        w = parse_dimension(img.get("width"))
        h = parse_dimension(img.get("height"))
        if w is not None and w <= 200:
            continue
        if h is not None and h <= 100:
            continue
        img["data-promoted"] = "hero"
        return {
            "url":         src,
            "url_small":   src,
            "alt":         img.get("alt", ""),
            "credit_name": "",
            "credit_url":  "",
            "source":      "article_image",
        }
    return None


def detect_category(title: str, summary: str) -> str | None:
    """Priority 2: 제목+요약 텍스트에서 카테고리 탐지."""
    text = title + " " + summary
    for category_key, pattern in CATEGORY_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return category_key
    return None


def html_attr(value: Any) -> str:
    return escape(str(value or ""), quote=True)


def build_hero_html(img: dict, date_str: str) -> str:
    """히어로 이미지 div HTML 생성."""
    credit_html = ""
    if img.get("credit_name") and img.get("credit_url"):
        credit_html = (
            f'<a class="reader-hero-credit" href="{html_attr(img["credit_url"])}" '
            f'target="_blank" rel="noopener">'
            f'Photo by {html_attr(img["credit_name"])} / Unsplash</a>'
        )
    return f"""<div class="reader-hero has-image" data-article-date="{html_attr(date_str)}">
  <picture>
    <source media="(max-width: 640px)" srcset="{html_attr(img['url_small'])}">
    <img class="reader-hero-img" src="{html_attr(img['url'])}" alt="{html_attr(img['alt'])}"
         loading="lazy" decoding="async">
  </picture>
  <div class="reader-hero-overlay"></div>
  {credit_html}
</div>"""


def resolve_hero(soup: BeautifulSoup, meta: dict) -> tuple[str, dict | None]:
    """
    히어로 이미지 결정. (html_snippet, image_meta) 반환.
    image_meta는 briefings.json 저장용. html_snippet은 주입용.
    """
    date_str = meta.get("date", "2026-01-01")
    title    = meta.get("title", "")
    summary  = meta.get("summary", "")

    # ── Priority 1: 기사 본문 이미지 ─────────────────────────────
    article_img = find_article_image(soup)
    if article_img:
        article_img["source"] = "article_image"
        return build_hero_html(article_img, date_str), article_img

    # ── Priority 2: 카테고리 핸드픽 맵 ──────────────────────────
    category = detect_category(title, summary)
    if category and category in CATEGORY_IMAGE_MAP:
        img_meta = select_from_pool(CATEGORY_IMAGE_MAP[category], date_str)
        img_meta = {**img_meta, "source": "handpick_category"}
        return build_hero_html(img_meta, date_str), img_meta

    # ── Priority 3: 기본 풀 ──────────────────────────────────────
    img_meta = select_from_pool(DEFAULT_IMAGE_POOL, date_str)
    img_meta = {**img_meta, "source": "handpick_default"}
    return build_hero_html(img_meta, date_str), img_meta

    # ── Priority 4: CSS 그라데이션 폴백 (도달 불가 — 기본 풀이 항상 존재)
    # return f'<div class="reader-hero no-image" data-article-date="{date_str}"></div>', None


def remove_previous_reader_chrome(soup: BeautifulSoup) -> None:
    for selector in ("nav.reader-nav", ".reader-hero", "footer.reader-footer"):
        for tag in soup.select(selector):
            tag.decompose()


def ensure_theme_link(soup: BeautifulSoup) -> None:
    head = soup.find("head")
    if head is None:
        return
    for link in head.find_all("link", href=True):
        if link.get("href", "").split("?", 1)[0] == "../theme-modern.css":
            return
    link = soup.new_tag("link", rel="stylesheet", href="../theme-modern.css")
    styles = head.find_all("style")
    if styles:
        styles[-1].insert_after(link)
    else:
        head.append(link)


def ensure_reader_mode(body: Any) -> None:
    existing = body.get("class", [])
    if isinstance(existing, str):
        existing = existing.split()
    if "reader-mode" not in existing:
        existing.append("reader-mode")
    body["class"] = existing


def process_article(html_path: Path, meta: dict) -> dict:
    """
    단일 기사 HTML 파일 변환.
    반환: briefings.json에 병합할 hero 메타데이터 dict.
    """
    soup = BeautifulSoup(html_path.read_text("utf-8"), "html.parser")

    # 1. <head>에 theme-modern.css 링크 주입
    head = soup.find("head")
    body = soup.find("body")
    if head is None or body is None:
        return {"hero_source": "css_gradient"}

    remove_previous_reader_chrome(soup)
    ensure_theme_link(soup)

    # 2. <body>에 reader-mode 클래스 추가
    ensure_reader_mode(body)

    # 3. 히어로 이미지 결정
    hero_html, img_meta = resolve_hero(soup, meta)

    # 4. GNB + 히어로를 <body> 최상단에 삽입
    body.insert(0, BeautifulSoup(hero_html, "html.parser"))
    body.insert(0, BeautifulSoup(GNB_HTML, "html.parser"))

    # 5. 리더 푸터를 </body> 직전에 삽입
    body.append(BeautifulSoup(FOOTER_HTML, "html.parser"))

    # 6. 저장
    html_path.write_text(str(soup), "utf-8")

    # 7. briefings.json 갱신용 메타 반환
    if img_meta:
        return {
            "hero_url":         img_meta.get("url", ""),
            "hero_url_small":   img_meta.get("url_small", ""),
            "hero_alt":         img_meta.get("alt", ""),
            "hero_credit_name": img_meta.get("credit_name", ""),
            "hero_credit_url":  img_meta.get("credit_url", ""),
            "hero_source":      img_meta.get("source", "css_gradient"),
        }
    return {"hero_source": "css_gradient"}


def main():
    data = json.loads(BRIEFINGS_JSON.read_text("utf-8"))

    for briefing in data.get("briefings", []):
        date = briefing.get("date", "")
        html_path = ARCHIVE_DIR / f"{date}.html"
        if not html_path.exists():
            continue

        hero_meta = process_article(html_path, briefing)
        briefing.update(hero_meta)
        print(f"[OK] {date} → source={hero_meta.get('hero_source')}")

    BRIEFINGS_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), "utf-8"
    )
    print(f"[DONE] briefings.json updated.")


if __name__ == "__main__":
    main()
