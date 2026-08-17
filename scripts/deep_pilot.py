#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📖 상세 해설 파일럿 — 커버리지·품질 실측 (커밋하지 않는다)

목적
  1) 매체별 '원문 본문 추출' 실제 성공률을 GitHub Actions 러너에서 잰다.
     (개발 샌드박스는 robots.txt 강제 프록시를 거쳐 CNBC·The Verge가 403이었다.
      그 숫자는 바닥값이지 실제값이 아니다. 여기서 재는 게 실제값이다.)
  2) 같은 기사에 Flash / Flash-Lite 두 모델을 돌려 해설 품질을 나란히 비교한다.

안전장치
  · 저장소에 아무것도 쓰지 않는다. 결과는 out/ 에만 남고 아티팩트로 나간다.
  · 환각 게이트: 추출 본문이 MIN_BODY 미만이면 모델에 보내지 않는다.
    페이월로 리드 300자만 받은 상태에서 "자세히 쓰라"고 하면 수치를 지어낸다.
"""
import os, re, sys, json, time, html, random
from collections import Counter, defaultdict
from urllib.parse import urlparse
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ── 설정 ───────────────────────────────────────────────────────────
N_ARTICLES = int(os.environ.get("PILOT_COUNT", "30"))
BATCH      = int(os.environ.get("PILOT_BATCH", "4"))     # 한 요청에 담을 기사 수
MIN_BODY   = int(os.environ.get("PILOT_MIN_BODY", "1200"))  # 환각 게이트 (자)
API_KEY    = os.environ.get("GEMINI_API_KEY", "")

MODELS = [
    # (모델 ID, 표시명, 분당 요청 한도)
    ("gemini-3.5-flash",      "3.5 Flash",      5),
    ("gemini-3.5-flash-lite", "3.5 Flash-Lite", 15),
]

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

ROOT = Path(__file__).resolve().parent.parent
OUT  = ROOT / "out"
OUT.mkdir(exist_ok=True)


# ── 1. 대상 카드 수집 (최신 아카이브부터) ──────────────────────────
DATE_RE  = re.compile(r"(\d{4})-(\d{2})-(\d{2})\.html$")
DAILY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.html$")

def archive_files(daily_only=True):
    """발행일 역순. 파일명 문자열 정렬은 'weekly-'가 숫자보다 커서 주간이 먼저 온다 — 쓰면 안 된다."""
    out = []
    for f in ROOT.glob("archive/*.html"):
        if daily_only and not DAILY_RE.match(f.name):
            continue
        m = DATE_RE.search(f.name)
        out.append((m.group(0) if m else "0000-00-00", f))
    out.sort(key=lambda x: x[0], reverse=True)
    return [f for _, f in out]


def collect_cards(n, daily_only=True):
    files = archive_files(daily_only)
    picked, seen = [], set()
    for f in files:
        if len(picked) >= n:
            break
        soup = BeautifulSoup(f.read_text(encoding="utf-8"), "html.parser")
        for c in soup.select(".jfnb-card"):
            if len(picked) >= n:
                break
            url = c.get("data-card-url", "")
            if not url or url in seen:
                continue
            seen.add(url)
            kr = c.select_one(".article-title-kr, .title-kr")
            summ = c.select_one(".article-summary")
            picked.append({
                "file":    f.name,
                "id":      c.get("id", ""),
                "url":     url,
                "domain":  urlparse(url).netloc.replace("www.", ""),
                "title_en": c.get("data-card-title", "")[:200],
                "title_kr": _txt(kr),
                "summary_now": _txt(summ),
            })
    return picked


def _txt(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip() if el else ""


# ── 2. 본문 추출 ───────────────────────────────────────────────────
def extract(url):
    """반환: (본문 str, 상태 str). 상태는 리포트용 사유 문자열."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=25, allow_redirects=True)
    except Exception as e:
        return "", f"net:{type(e).__name__}"
    if r.status_code != 200:
        return "", f"http:{r.status_code}"

    body = ""
    try:
        import trafilatura
        body = trafilatura.extract(
            r.text, include_comments=False, include_tables=False,
            favor_precision=True, url=url
        ) or ""
    except Exception:
        pass

    if len(body) < 400:                      # 폴백 — 문단 태그 직접 수집
        soup = BeautifulSoup(r.text, "html.parser")
        for bad in soup.select("script,style,nav,footer,header,aside,form"):
            bad.decompose()
        ps = [_txt(p) for p in soup.find_all("p")]
        alt = "\n".join(p for p in ps if len(p) > 60)
        if len(alt) > len(body):
            body = alt

    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    if not body:
        return "", "empty"
    return body, "ok"


# ── 3. 프롬프트 ────────────────────────────────────────────────────
SYSTEM = """너는 한국 경제·기술 매체의 외신 데스크다. 영문 기사 원문을 받아
한국 독자를 위한 '상세 해설'을 쓴다.

절대 규칙
1. 원문에 없는 사실·수치·인용을 절대 만들지 마라. 원문에 근거가 없으면 쓰지 마라.
   불확실하면 그 대목을 통째로 빼라. 분량을 채우려고 추측하지 마라.
2. 전문 번역이 아니다. 번역체 문장을 나열하지 말고 재구성해서 설명하라.
3. 직접인용은 최대 1개, 15단어 이내로만. 원문 문장을 길게 옮기지 마라.
4. 함께 주는 '기존 요약'은 이미 독자가 읽은 내용이다. 반복하지 말고
   그 다음 층위를 써라 — 구체 수치, 이해관계자의 실제 발언, 반론,
   시간 순서, 후속 일정, 경쟁사·시장과의 비교.

형식 (800~1,200자, 한국어, 3~4개 문단)
· 각 문단은 굵은 글씨의 짧은 리드 문장으로 시작한다. **문장** 형태.
· 마지막 문단은 반드시 **한국 관점** 으로 시작하고, 한국 산업·기업·규제에
  어떤 의미인지 쓴다. 원문에 한국 언급이 없으면 억지로 엮지 말고
  '왜 한국 독자가 알아야 하는가'를 한 단락으로 정리하라.
· 소제목·불릿·번호 목록을 쓰지 마라. 문단만 쓴다."""

USER_TMPL = """다음 {n}건의 기사 각각에 대해 상세 해설을 써라.

{articles}

출력은 JSON 배열 하나. 각 원소는 {{"i": <번호>, "deep": "<해설 본문>"}}.
설명이나 코드펜스 없이 JSON만 출력하라."""

ART_TMPL = """───────── 기사 {i} ─────────
[매체] {domain}
[제목] {title_en}
[한글 제목] {title_kr}
[기존 요약 — 반복 금지] {summary_now}
[원문 본문]
{body}
"""


def build_prompt(batch):
    arts = "\n".join(
        ART_TMPL.format(
            i=a["i"], domain=a["domain"], title_en=a["title_en"],
            title_kr=a["title_kr"] or "(없음)",
            summary_now=a["summary_now"] or "(없음)",
            body=a["body"][:12000],
        ) for a in batch
    )
    return USER_TMPL.format(n=len(batch), articles=arts)


# ── 4. Gemini 호출 ─────────────────────────────────────────────────
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"

def call_gemini(model, prompt, tries=4):
    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 8192,
            "responseMimeType": "application/json",
        },
    }
    last = ""
    for k in range(tries):
        try:
            r = requests.post(
                ENDPOINT.format(m=model),
                headers={"x-goog-api-key": API_KEY, "Content-Type": "application/json"},
                json=payload, timeout=180,
            )
        except Exception as e:
            last = f"net:{type(e).__name__}"
            time.sleep(5 * (k + 1)); continue

        if r.status_code == 200:
            try:
                cands = r.json().get("candidates") or []
                if not cands:
                    return None, "no-candidate"
                txt = "".join(p.get("text", "")
                              for p in cands[0].get("content", {}).get("parts", []))
                return json.loads(txt), "ok"
            except Exception as e:
                last = f"parse:{type(e).__name__}"
                break
        if r.status_code == 429:
            wait = 20 * (k + 1) + random.uniform(0, 5)
            print(f"    429 — {wait:.0f}s 대기 후 재시도 ({k+1}/{tries})", flush=True)
            last = "429"
            time.sleep(wait); continue
        last = f"http:{r.status_code} {r.text[:200]}"
        break
    return None, last


# ── 5. 실행 ────────────────────────────────────────────────────────
def main():
    if not API_KEY:
        print("GEMINI_API_KEY 가 없습니다.", file=sys.stderr)
        sys.exit(1)

    print(f"■ 대상 수집 — 최신 아카이브에서 {N_ARTICLES}건", flush=True)
    cards = collect_cards(N_ARTICLES)
    print(f"  {len(cards)}건 (파일 {len(set(c['file'] for c in cards))}개)\n", flush=True)

    print("■ 본문 추출", flush=True)
    stat = defaultdict(lambda: {"try": 0, "ok": 0, "short": 0, "fail": 0, "lens": [], "why": Counter()})
    for i, c in enumerate(cards):
        body, why = extract(c["url"])
        c["body"], c["extract"] = body, why
        s = stat[c["domain"]]
        s["try"] += 1
        if why != "ok":
            s["fail"] += 1; s["why"][why] += 1
            c["state"] = "extract_fail"
        elif len(body) < MIN_BODY:
            s["short"] += 1; s["lens"].append(len(body))
            c["state"] = "too_short"
        else:
            s["ok"] += 1; s["lens"].append(len(body))
            c["state"] = "ready"
        print(f"  [{i+1:2d}/{len(cards)}] {c['domain']:<20} {len(body):>6}자  {c['state']}", flush=True)
        time.sleep(0.7)

    ready = [c for c in cards if c["state"] == "ready"]
    print(f"\n  생성 대상 {len(ready)}건 / 전체 {len(cards)}건\n", flush=True)

    for i, c in enumerate(ready):
        c["i"] = i + 1

    batches = [ready[i:i + BATCH] for i in range(0, len(ready), BATCH)]

    for model, label, rpm in MODELS:
        gap = 60.0 / rpm + 1
        print(f"■ {label} — {len(batches)}요청 (요청 간 {gap:.0f}초)", flush=True)
        for bi, b in enumerate(batches):
            t0 = time.time()
            data, why = call_gemini(model, build_prompt(b))
            took = time.time() - t0
            if data is None:
                print(f"  [{bi+1}/{len(batches)}] 실패 — {why}", flush=True)
                for a in b:
                    a.setdefault("deep", {})[model] = f"(실패: {why})"
            else:
                got = {int(o.get("i", -1)): o.get("deep", "") for o in data if isinstance(o, dict)}
                for a in b:
                    a.setdefault("deep", {})[model] = got.get(a["i"], "(응답 누락)")
                lens = [len(got.get(a['i'], '')) for a in b]
                print(f"  [{bi+1}/{len(batches)}] ok {took:.0f}s — 길이 {lens}", flush=True)
            if bi < len(batches) - 1:
                time.sleep(max(0, gap - took))
        print(flush=True)

    write_reports(cards, ready, stat)
    print(f"■ 완료 — out/ 에 결과 3종 생성", flush=True)


# ── 6. 리포트 ──────────────────────────────────────────────────────
def write_reports(cards, ready, stat):
    (OUT / "raw.json").write_text(
        json.dumps(cards, ensure_ascii=False, indent=1), encoding="utf-8")

    # 커버리지 리포트
    L = []
    tot = len(cards)
    ok = sum(1 for c in cards if c["state"] == "ready")
    short = sum(1 for c in cards if c["state"] == "too_short")
    fail = sum(1 for c in cards if c["state"] == "extract_fail")
    L.append("# 📖 상세 해설 파일럿 — 커버리지 실측\n")
    L.append(f"대상 **{tot}건** · 환각 게이트 **{MIN_BODY}자** · 배치 **{BATCH}건/요청**\n")
    L.append("| 결과 | 건수 | 비율 |")
    L.append("|---|---:|---:|")
    L.append(f"| ✅ 생성 (본문 {MIN_BODY}자 이상) | {ok} | {ok/tot*100:.0f}% |")
    L.append(f"| ⚠️ 본문 부족 (페이월 추정) | {short} | {short/tot*100:.0f}% |")
    L.append(f"| ❌ 추출 실패 | {fail} | {fail/tot*100:.0f}% |")
    L.append("\n## 매체별\n")
    L.append("| 매체 | 시도 | 생성 | 부족 | 실패 | 본문 중앙값 | 실패 사유 |")
    L.append("|---|---:|---:|---:|---:|---:|---|")
    for dom, s in sorted(stat.items(), key=lambda x: -x[1]["try"]):
        med = sorted(s["lens"])[len(s["lens"]) // 2] if s["lens"] else 0
        why = ", ".join(f"{k}×{v}" for k, v in s["why"].most_common(3)) or "—"
        L.append(f"| {dom} | {s['try']} | {s['ok']} | {s['short']} | {s['fail']} | {med:,} | {why} |")
    (OUT / "coverage.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    # 품질 비교 — 같은 기사, 두 모델 나란히
    Q = ["# 📖 해설 품질 비교 — 3.5 Flash vs 3.5 Flash-Lite\n",
         "각 기사마다 ① 현행 요약 ② Flash ③ Flash-Lite 순으로 싣는다.",
         "읽으면서 볼 것 — **원문에 없는 수치를 지어내지 않았는가**, ",
         "**기존 요약을 반복하지 않고 그 다음 층위를 썼는가**, ",
         "**한국 관점 문단이 억지스럽지 않은가**.\n\n---\n"]
    for c in ready:
        Q.append(f"## {c['i']}. {c['title_kr'] or c['title_en']}\n")
        Q.append(f"`{c['domain']}` · `{c['file']}#{c['id']}` · 본문 {len(c['body']):,}자 · "
                 f"[원문]({c['url']})\n")
        Q.append(f"**현행 요약** ({len(c['summary_now'])}자)\n\n> {c['summary_now'] or '(없음)'}\n")
        for model, label, _ in MODELS:
            d = c.get("deep", {}).get(model, "(없음)")
            Q.append(f"**{label}** ({len(d)}자)\n\n{d}\n")
        Q.append("\n---\n")
    (OUT / "quality.md").write_text("\n".join(Q), encoding="utf-8")


if __name__ == "__main__":
    main()
