"""
아카이브 HTML 카드 탐지·정규화 — post_process.py 편입용 (검증 완료본)

검증 (2026-08-15, 아카이브 245개 파일 전수):
  일간 212개 : 카드 4,079건 / 검출 0건 파일 없음
               └ 2026-02 이후 168개는 기존 `.article-card` 개수와 168/168 완전 일치
  주간  30개 : 카드   290건 / 검출 0건 파일 없음
  특별판 3개 : 카드    38건 / 검출 0건 파일 없음

설계 원칙
  · 클래스 이름을 믿지 않는다. 아카이브에 마크업이 6세대 이상 섞여 있고
    주간은 매주 새로 작성되어 클래스가 매번 바뀐다.
  · 대신 "제목을 가진 블록"이라는 구조를 본다. 제목은 h2~h4 또는
    class에 title/ttl/headline이 들어간 요소 (2026-02-22 주간은 heading 태그가 0개다).
  · timeline-item·market-item·stat-card 등 '카드처럼 생긴 비기사'는 DENY로 차단한다.
    단순 [class*="card"] 셀렉터는 시장지표 박스를 기사로 잡는다 — 쓰지 말 것.
"""
import re

# 카드처럼 보이지만 기사가 아닌 것들 (실측으로 수집)
DENY = {
    "timeline-item", "tl-item", "timeline", "tl",
    "market-item", "m-card", "market", "mkt",
    "stat-item", "stat-card", "stats", "stat", "num", "val",
    "meta", "badge", "sec-head", "name", "lab", "ttl", "d", "status",
    "footer-counter", "reader-nav", "reader-footer",
}

# 세대별 카드 컨테이너. 위에서부터 우선 매칭된다.
SELECTORS = [
    # 일간 현행 (2026-01-31~)
    "article.article-card",
    # 일간 초기판 (2025-12 ~ 2026-01)
    "article.hero-card", "article.card", "article.pick-card",
    # 주간 마크업 계약 (weekly-briefing SKILL v1.8) — 태그를 가리지 않는다.
    #   계약은 article/div를 지정하지만, 태그 하나 어긋났다고 그 주 브리핑이
    #   통째로 빠지면 안 된다. 클래스 이름만 지켜지면 잡는다.
    ".cluster-card", ".standalone-item", ".pick-item",
    # 주간 — 계약 이전 세대들
    "article.cluster", "article.story-cluster", "article.story",
    "div.story-card", "div.story-cluster", "div.cluster", "div.story",
    "div.hl", "div.sa", "div.pick",
    # 최후의 이름 규칙 — 위 어느 이름에도 안 걸린 <article>.
    #   일간 초기판이 <article class="article">·"article top"·"article pick"을 썼다(코퍼스 323건).
    #   반드시 체인의 맨 끝에 둔다. 앞에 두면 구체적인 이름들을 덮어버린다.
    "article",
]

TITLE_CLS = re.compile(r"(^|[-_ ])(title|ttl|headline)", re.I)


def _title_el(el):
    """카드의 제목 요소. heading 태그가 없는 세대를 위해 class 기반 폴백을 둔다."""
    h = el.find(["h2", "h3", "h4"])
    if h:
        return h

    def _match(c):
        if not c:
            return False
        if isinstance(c, str):          # BeautifulSoup이 문자열로 넘기는 경우가 있다
            c = c.split()
        return any(TITLE_CLS.search(x) for x in c)

    return el.find(attrs={"class": _match})


def detect_cards(soup, kind="daily"):
    """kind: 'daily' | 'weekly' | 'special'. 문서 순으로 정렬된 카드 요소 리스트를 반환."""
    body = soup.find("body") or soup
    for sel in ("nav", "footer", "head", "script", "style"):
        for x in body.select(sel):
            x.decompose()

    found, seen = [], set()
    for sel in SELECTORS:
        for el in body.select(sel):
            if id(el) in seen:
                continue
            if DENY & set(el.get("class", [])):
                continue
            if _title_el(el) is None:
                continue
            if any(el in f.descendants for f in found):   # 이미 잡힌 카드의 자손
                continue
            seen.add(id(el))
            found.append(el)

    # 자손을 품은 조상이 뒤늦게 잡힌 경우 정리
    found = [e for e in found if not any(e is not f and e in f.descendants for f in found)]

    # 구조 폴백 — 셀렉터가 하나도 못 잡았을 때만. 원문 링크의 최근접 '제목 보유 조상'.
    # 주간은 원문 링크가 없으므로(30개 중 28개가 외부 링크 0개) 적용하지 않는다.
    if not found and kind != "weekly":
        for a in body.find_all("a", href=True):
            href = a["href"]
            if not href.startswith("http") or "hong4137.github.io" in href:
                continue
            box = a.parent
            while box is not None and box.name not in ("body", "html"):
                if _title_el(box) is not None:
                    break
                box = box.parent
            if box is None or box.name in ("body", "html") or id(box) in seen:
                continue
            seen.add(id(box))
            found.append(box)
        found = [e for e in found if not any(e is not f and e in f.descendants for f in found)]

    # 셀렉터 체인은 클래스 순으로 섞이므로 문서 순 재정렬이 반드시 필요하다
    order = {id(e): i for i, e in enumerate(body.find_all(True))}
    found.sort(key=lambda e: order.get(id(e), 1 << 30))
    return found


def normalize_cards(soup, kind="daily"):
    """카드에 id·정규화 클래스·메타데이터를 부여한다. 멱등. 반환: 카드 수."""
    cards = detect_cards(soup, kind)
    for i, el in enumerate(cards):
        el["id"] = f"art-{i}"
        cls = el.get("class", [])
        if isinstance(cls, str):
            cls = cls.split()
        if "jfnb-card" not in cls:
            cls = cls + ["jfnb-card"]
        el["class"] = cls
        el["data-card-index"] = str(i)
        el["data-card-type"] = "cluster" if kind == "weekly" else "article"

        link = next((a["href"] for a in el.find_all("a", href=True)
                     if a["href"].startswith("http")
                     and "hong4137.github.io" not in a["href"]), "")
        if link:
            el["data-card-url"] = link          # 주간에는 붙지 않는다 (원문 링크 부재)

        t = _title_el(el)
        if t is not None:
            el["data-card-title"] = re.sub(r"\s+", " ", t.get_text(" ", strip=True))[:200]
    return len(cards)
