"""
직전 판 대조 도구 — briefing-main v3.6 Step 1·4.5·5 용

외신 브리핑은 '전날(직전 일간판)과 겹치는 것'만 피한다. 이 스크립트는
  1) 직전 일간판의 카드 목록(제목·URL·요약 앞 두 문장)과 「어제에 이어」 줄을 뽑고
  2) 후보 기사와 고유명사가 겹치는 직전 판 카드를 짝 후보로 추리고
  3) 지난 모든 일간판의 카드 URL과 완전 일치하는 후보를 찾는다(URL 안전망)

표준 라이브러리만 쓴다(무인 실행 환경에 설치 없이 돈다).

  python scripts/prev_edition.py --before 2026-11-21                     # 직전 판 요약 (기본)
  python scripts/prev_edition.py --before 2026-11-21 --facts <url>       # 그 카드 요약 전문
  python scripts/prev_edition.py --before 2026-11-21 --pairs cand.json   # 짝 후보
  python scripts/prev_edition.py --before 2026-11-21 --seen-urls cand.json  # URL 안전망

cand.json = [{"id": "c1", "title": "영문 제목", "url": "https://..."}, ...]  (문자열 URL 목록도 받는다)

직전 판을 못 찾으면 {"date": null, "reason": "..."} 을 내고 종료 코드 0 — 발행을 막지 않는다.
"""
import argparse
import html
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))
DAILY = re.compile(r"^\d{4}-\d{2}-\d{2}\.html$")

# 짝 후보를 고를 때 무시하는 흔한 대문자 낱말 — 이것만 겹쳐서는 같은 사건이 아니다
STOP = set("""
The A An In On Of For And To With At By From As Is Are Its It This That These Those New
Why How What When Where Who Can Will Would Could Should May Might After Before Says Say Said
Over Into Up Out More Than Be Has Have Had Was Were Not But Just Now Here There Their Your
Our His Her They We You I Inc Co Corp Ltd LLC CEO CFO AI US U.S UK EU Big Tech First Last
Report Reports Exclusive Update Live Breaking Week Year Day Today Billion Million Trillion
Jan Feb Mar Apr May Jun Jul Aug Sep Sept Oct Nov Dec Monday Tuesday Wednesday Thursday Friday
Saturday Sunday Wall Street
""".split())
# 너무 자주 나와 그것만으로는 짝을 짓지 않는 이름 (다른 고유명사가 함께 겹쳐야 짝)
COMMON = {"Google", "Apple", "Meta", "Microsoft", "Amazon", "OpenAI", "Nvidia", "China",
          "Chinese", "Trump", "Musk", "Tesla", "Samsung", "Anthropic", "Claude", "Gemini",
          "ChatGPT", "Washington", "Beijing", "America", "American", "Europe", "European"}


def norm_url(u):
    u = html.unescape(u or "").strip()
    u = re.sub(r"[?#].*$", "", u)
    u = re.sub(r"^https?://(www\.|m\.)?", "", u, flags=re.I)
    host, _, path = u.partition("/")
    return (host.lower() + "/" + path).rstrip("/")


def text_of(fragment):
    t = re.sub(r"<[^>]+>", " ", fragment or "")
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


# 내용어(소문자 낱말) 가운데 사건을 가르는 데 쓸모없는 것
WSTOP = set("""
about after again against along among another around because before being below between
could during every first other since still their there these those through under until
which while would should might report reports reported says saying said years today
company companies people plans plan major amid billion million shares stock stocks
backed house could makes making launches launch""".split())


def words(title):
    return {w for w in re.findall(r"[a-z]{5,}", (title or "").lower()) if w not in WSTOP}


def lead_of(summary, n=2):
    parts = re.split(r"(?<=[.!?다요])\s+", summary)
    return " ".join(parts[:n]).strip()


def ents(title):
    words = re.findall(r"[A-Z][A-Za-z0-9\-’'&.]+", title or "")
    out = set()
    for w in words:
        w = re.sub(r"(’s|'s)$", "", w).strip(".,:;'’")
        if len(w) >= 2 and w not in STOP:
            out.add(w)
    return out


def parse_edition(path):
    s = open(path, encoding="utf-8").read()
    # 섹션 경계: h2.section-title 위치
    secs = [(m.start(), text_of(m.group(1))) for m in
            re.finditer(r'<h2[^>]*class="[^"]*section-title[^"]*"[^>]*>(.*?)</h2>', s, re.S)]

    def section_at(pos):
        name = ""
        for p, t in secs:
            if p < pos:
                name = t
        return name

    cards = []
    for m in re.finditer(r'<article\b([^>]*class="[^"]*article-card[^"]*"[^>]*)>(.*?)</article>', s, re.S):
        attrs, body = m.group(1), m.group(2)
        g = lambda p: (lambda x: text_of(x.group(1)) if x else "")(re.search(p, body, re.S))
        url = re.search(r'data-card-url="([^"]+)"', attrs)
        if not url:
            url = re.search(r'href="(https?://[^"]+)"', body)
        aid = re.search(r'\bid="([^"]+)"', attrs)
        title = re.search(r'data-card-title="([^"]*)"', attrs)
        summary = g(r'class="article-summary"[^>]*>(.*?)</p>')
        cards.append({
            "id": aid.group(1) if aid else f"art-{len(cards)}",
            "section": section_at(m.start()),
            "title": html.unescape(title.group(1)) if title else g(r'class="article-title"[^>]*>(.*?)</h3>'),
            "title_kr": g(r'class="article-title-kr"[^>]*>(.*?)</p>'),
            "url": html.unescape(url.group(1)) if url else "",
            "lead": lead_of(summary),
            "_summary": summary,
        })

    followups = []
    for m in re.finditer(r'<li\b([^>]*class="[^"]*followup-item[^"]*"[^>]*)>(.*?)</li>', s, re.S):
        attrs, body = m.group(1), m.group(2)
        prev = re.search(r'data-prev="([^"]+)"', attrs)
        subj = re.search(r'class="fu-subject"[^>]*>(.*?)</', body, re.S)
        followups.append({
            "prev": prev.group(1) if prev else "",
            "subject": text_of(subj.group(1)) if subj else "",
            "text": text_of(re.sub(r"<a\b.*?</a>", "", body, flags=re.S)),
            "urls": [html.unescape(u) for u in re.findall(r'href="(https?://[^"]+)"', body)],
        })
    return cards, followups


def daily_files(repo):
    d = os.path.join(repo, "archive")
    return sorted(f for f in os.listdir(d) if DAILY.match(f))


def find_prev(repo, before):
    """briefings.json 의 일간판 가운데 before 보다 앞선 첫 판. 없거나 읽기 실패면 archive 파일명으로."""
    dates = []
    try:
        b = json.load(open(os.path.join(repo, "briefings.json"), encoding="utf-8"))
        b = b.get("briefings", b) if isinstance(b, dict) else b
        dates = sorted({x.get("date") for x in b if x.get("date")}, reverse=True)
    except Exception:
        pass
    if not dates:
        dates = sorted((f[:10] for f in daily_files(repo)), reverse=True)
    for d in dates:
        if d >= before:
            continue
        p = os.path.join(repo, "archive", f"{d}.html")
        if not os.path.exists(p):
            continue
        cards, fus = parse_edition(p)
        if cards:
            return d, cards, fus
    return None, [], []


def load_candidates(path):
    c = json.load(open(path, encoding="utf-8"))
    out = []
    for i, x in enumerate(c):
        if isinstance(x, str):
            out.append({"id": f"c{i}", "title": "", "url": x})
        else:
            out.append({"id": x.get("id", f"c{i}"), "title": x.get("title", ""), "url": x.get("url", "")})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--before", default=datetime.now(KST).strftime("%Y-%m-%d"), help="오늘 발행 날짜(이 날짜보다 앞선 판을 찾는다)")
    ap.add_argument("--facts", metavar="URL")
    ap.add_argument("--pairs", metavar="CANDIDATES_JSON")
    ap.add_argument("--seen-urls", metavar="CANDIDATES_JSON")
    a = ap.parse_args()
    out = lambda o: print(json.dumps(o, ensure_ascii=False, indent=1))

    if a.seen_urls:
        cands = load_candidates(a.seen_urls)
        want = {norm_url(c["url"]): c for c in cands if c["url"]}
        hits = {}
        for f in daily_files(a.repo):
            d = f[:10]
            if d >= a.before:
                continue
            s = open(os.path.join(a.repo, "archive", f), encoding="utf-8").read()
            for u in set(re.findall(r'data-card-url="([^"]+)"', s)):
                k = norm_url(u)
                if k in want:
                    hits.setdefault(want[k]["id"], {"url": want[k]["url"], "dates": []})["dates"].append(d)
        out({"checked": len(want), "already_published": hits})
        return

    date, cards, fus = find_prev(a.repo, a.before)
    if not date:
        out({"date": None, "reason": f"{a.before} 이전 일간판을 찾지 못함 — 대조 생략하고 발행"})
        return

    if a.facts:
        k = norm_url(a.facts)
        c = next((c for c in cards if norm_url(c["url"]) == k), None)
        out({"date": date, "card": {**{x: y for x, y in c.items() if x != "_summary"}, "facts": c["_summary"]}} if c
            else {"date": date, "card": None, "reason": "직전 판에 그 URL 없음"})
        return

    if a.pairs:
        cands = load_candidates(a.pairs)
        res = []
        for c in cands:
            ce = ents(c["title"])
            hits = []
            cw = words(c["title"])
            for p in cards:
                # 짝 후보는 놓치지 않는 쪽으로 넓게 — 판정은 AI 가 한다.
                # 고유명사 하나라도(흔한 이름 포함) 또는 사건을 가르는 내용어 하나라도 겹치면 후보.
                shared = {w.lower() for w in ce & ents(p["title"])} | (cw & words(p["title"]))
                if shared:
                    hits.append({"prev": f'{date}#{p["id"]}', "title": p["title"], "shared": sorted(shared)})
            # 직전 판 「어제에 이어」 줄의 주체도 본다
            for f in fus:
                if f["subject"] and any(f["subject"].lower() in w.lower() for w in ce | {c["title"]}):
                    hits.append({"prev": f["prev"] or date, "title": f["text"][:80], "shared": [f["subject"]], "followup": True})
            if hits:
                res.append({"id": c["id"], "title": c["title"], "candidates": hits})
        out({"date": date, "checked": len(cands), "pairs": res})
        return

    out({"date": date, "cards": [{k: v for k, v in c.items() if k != "_summary"} for c in cards],
         "followups": fus})


if __name__ == "__main__":
    sys.exit(main())
