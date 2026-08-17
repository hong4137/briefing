#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📖 원문 본문 추출 — Gemini를 호출하지 않는다 (API 한도와 완전히 무관)

이 스크립트는 '재료'만 모은다. 해설 작성은 별도 단계다.
  · 최근 N일 일간 브리핑에서 원문 URL을 모으고
  · 각 원문의 본문을 추출해
  · out/ 에 날짜별 JSON으로 떨군다 (아티팩트로 회수)

왜 Actions에서 돌리는가
  개발 샌드박스는 robots.txt 강제 프록시를 거쳐 Bloomberg·CNBC·The Verge가 403이다.
  파일럿 실측에서 Actions 러너는 CNBC 9/9, The Verge 2/2로 전부 통과했다.
  추출만큼은 반드시 여기서 해야 커버리지 80%가 나온다.

저장소에 아무것도 쓰지 않는다.
"""
import os, re, json, time, random, sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from pathlib import Path
from threading import Lock

import requests
from bs4 import BeautifulSoup

DAYS      = int(os.environ.get("EXTRACT_DAYS", "30"))
MIN_BODY  = int(os.environ.get("EXTRACT_MIN_BODY", "1200"))   # 환각 게이트
BODY_CAP  = int(os.environ.get("EXTRACT_BODY_CAP", "12000"))  # JSON 비대 방지
WORKERS   = int(os.environ.get("EXTRACT_WORKERS", "4"))

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

DAILY_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.html$")
_print_lock = Lock()


def _txt(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip() if el else ""


# ── 1. 대상 수집 ───────────────────────────────────────────────────
def collect(days):
    """최근 N일 일간 브리핑. 같은 원문 URL이 여러 날 등장하면 최신 1건만 남긴다."""
    files = []
    for f in ROOT.glob("archive/*.html"):
        m = DAILY_RE.match(f.name)
        if m:
            files.append((m.group(1), f))
    files.sort(reverse=True)
    files = files[:days]

    # 이미 만들어 둔 해설은 건너뛴다 (증분 실행)
    done = set()
    for j in (ROOT / "deep").glob("*.json"):
        try:
            done |= set(json.loads(j.read_text(encoding="utf-8")).get("items", {}))
        except Exception:
            pass
    if done:
        print(f"  기존 해설 {len(done)}건 — 건너뜀")

    out, seen = [], set()
    for date, f in files:
        soup = BeautifulSoup(f.read_text(encoding="utf-8"), "html.parser")
        for c in soup.select(".jfnb-card"):
            url = c.get("data-card-url", "")
            if not url or url in seen or url in done:
                continue
            seen.add(url)
            out.append({
                "date": date,
                "file": f.name,
                "id": c.get("id", ""),
                "url": url,
                "domain": urlparse(url).netloc.replace("www.", ""),
                "title_en": c.get("data-card-title", "")[:200],
                "title_kr": _txt(c.select_one(".article-title-kr, .title-kr")),
                "summary_now": _txt(c.select_one(".article-summary")),
            })
    return files, out


# ── 2. 본문 추출 ───────────────────────────────────────────────────
def extract(url):
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
            favor_precision=True, url=url) or ""
    except Exception:
        pass

    if len(body) < 400:                       # 폴백 — 문단 태그 직접 수집
        soup = BeautifulSoup(r.text, "html.parser")
        for bad in soup.select("script,style,nav,footer,header,aside,form"):
            bad.decompose()
        alt = "\n".join(p for p in (_txt(p) for p in soup.find_all("p")) if len(p) > 60)
        if len(alt) > len(body):
            body = alt

    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return (body, "ok") if body else ("", "empty")


def work(a, i, n):
    time.sleep(random.uniform(0.2, 0.9))      # 같은 매체에 몰리지 않게
    body, why = extract(a["url"])
    a["body"] = body[:BODY_CAP]
    a["state"] = ("extract_fail" if why != "ok"
                  else "too_short" if len(body) < MIN_BODY
                  else "ready")
    a["why"] = why
    with _print_lock:
        print(f"  [{i+1:4d}/{n}] {a['date']} {a['domain']:<18} "
              f"{len(body):>6}자  {a['state']}", flush=True)
    return a


# ── 3. 실행 ────────────────────────────────────────────────────────
def main():
    print(f"■ 대상 수집 — 최근 {DAYS}일 일간 브리핑", flush=True)
    files, arts = collect(DAYS)
    if not arts:
        print("  새로 추출할 원문이 없습니다.")
        (OUT / "manifest.md").write_text("새로 추출할 원문이 없습니다.\n", encoding="utf-8")
        return
    print(f"  파일 {len(files)}개 ({files[-1][0]} ~ {files[0][0]}) · 고유 원문 {len(arts)}건\n",
          flush=True)

    print(f"■ 본문 추출 (동시 {WORKERS})", flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        arts = list(ex.map(lambda p: work(p[1], p[0], len(arts)), enumerate(arts)))
    print(f"\n  {time.time()-t0:.0f}초 소요\n", flush=True)

    # 날짜별로 쪼개 저장 — 해설 작성 단계에서 조금씩 받아가기 좋게
    by_date = defaultdict(list)
    for a in arts:
        by_date[a["date"]].append(a)
    for date, items in by_date.items():
        (OUT / f"bodies-{date}.json").write_text(
            json.dumps({"date": date, "articles": items}, ensure_ascii=False, indent=1),
            encoding="utf-8")

    # 한 덩어리 버전도 함께
    (OUT / "bodies-all.json").write_text(
        json.dumps({
            "days": DAYS, "min_body": MIN_BODY,
            "range": [files[-1][0], files[0][0]],
            "articles": arts,
        }, ensure_ascii=False, indent=1), encoding="utf-8")

    write_manifest(arts, files)
    print("■ 완료 — out/ 확인", flush=True)


def write_manifest(arts, files):
    tot = len(arts)
    ready = [a for a in arts if a["state"] == "ready"]
    short = [a for a in arts if a["state"] == "too_short"]
    fail  = [a for a in arts if a["state"] == "extract_fail"]

    dom = defaultdict(lambda: {"n": 0, "ok": 0, "short": 0, "fail": 0,
                               "lens": [], "why": Counter()})
    for a in arts:
        s = dom[a["domain"]]
        s["n"] += 1
        s[{"ready": "ok", "too_short": "short", "extract_fail": "fail"}[a["state"]]] += 1
        if a["body"]:
            s["lens"].append(len(a["body"]))
        if a["state"] == "extract_fail":
            s["why"][a["why"]] += 1

    L = ["# 📖 본문 추출 결과\n",
         f"최근 **{DAYS}일** ({files[-1][0]} ~ {files[0][0]}) · 파일 {len(files)}개 · "
         f"환각 게이트 **{MIN_BODY}자**\n",
         "| 결과 | 건수 | 비율 |", "|---|---:|---:|",
         f"| ✅ 해설 생성 대상 | {len(ready)} | {len(ready)/tot*100:.0f}% |",
         f"| ⚠️ 본문 부족 (페이월) | {len(short)} | {len(short)/tot*100:.0f}% |",
         f"| ❌ 추출 실패 | {len(fail)} | {len(fail)/tot*100:.0f}% |",
         f"| **합계** | **{tot}** | |", "\n## 매체별\n",
         "| 매체 | 전체 | 생성 | 부족 | 실패 | 본문 중앙값 | 실패 사유 |",
         "|---|---:|---:|---:|---:|---:|---|"]
    for d, s in sorted(dom.items(), key=lambda x: -x[1]["n"]):
        med = sorted(s["lens"])[len(s["lens"]) // 2] if s["lens"] else 0
        why = ", ".join(f"{k}×{v}" for k, v in s["why"].most_common(3)) or "—"
        L.append(f"| {d} | {s['n']} | {s['ok']} | {s['short']} | {s['fail']} | {med:,} | {why} |")

    L.append("\n## 날짜별 생성 대상\n")
    L.append("| 날짜 | 대상 | 파일 |")
    L.append("|---|---:|---|")
    per = defaultdict(int)
    for a in ready:
        per[a["date"]] += 1
    for date in sorted(per, reverse=True):
        L.append(f"| {date} | {per[date]} | `bodies-{date}.json` |")

    (OUT / "manifest.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
