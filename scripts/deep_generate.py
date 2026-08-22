#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📖 상세 해설 자동 생성 — 발행 파이프라인용 (deep/{날짜}.json 커밋까지)

파일럿(deep_pilot.py)과 다른 점
  1) 프롬프트를 **확정 규격**으로 교체했다.
     · 파일럿 프롬프트는 '한국 관점' 문단을 강제하고 800~1,200자를 요구했다.
       둘 다 폐기된 옛 규격이다. 지금 규격은 700~2,100자·4~6문단·한국 관점 금지다.
  2) maxOutputTokens 8192 → 32768. 배치 4건에서 JSON이 잘리던 원인.
  3) responseSchema로 구조를 강제하고 finishReason을 확인한다.
     잘리면 같은 배치를 1건씩 쪼개 재시도한다.
  4) 배치 기본 2건. 한 응답에 여러 기사를 몰아 쓰다 문단이 엉뚱한 기사에
     배분되던 사고를 막는다.
  5) **생성분마다 verify_deep.py를 돌려 통과한 것만 저장한다.**
     미대조 수치·고유명사가 하나라도 있으면 그 기사는 아예 만들지 않는다.
  6) 기사별 목표 글자수를 원문 길이에서 계산해 프롬프트에 넣는다.
     (사람이 쓸 때도 초고가 목표의 1.4~1.8배로 나왔다. 미리 못 박는다.)

안전
  · 건드리는 파일은 deep/{날짜}.json 뿐이다. archive·data·briefings.json 무관.
  · 이미 deep/{날짜}.json이 있으면 그 날짜는 건너뛴다 (중복 호출·한도 낭비 방지).
  · 같은 원문 URL의 해설이 다른 날짜에 이미 있으면 재사용한다 (한도 절약).
  · DEEP_MAX_REQUESTS로 Gemini 호출 수에 상한을 둔다 (무료 등급 Flash 20 RPD).
  · DEEP_DRY_RUN=1 이면 Gemini를 부르지 않고 파이프라인만 점검한다.
"""
import os, re, sys, json, time, random
from collections import defaultdict
from urllib.parse import urlparse
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import verify_deep as V                      # 검증 로직 재사용

# ── 설정 ───────────────────────────────────────────────────────────
API_KEY      = os.environ.get("GEMINI_API_KEY", "")
MODEL        = os.environ.get("DEEP_MODEL", "gemini-3.5-flash")
BATCH        = int(os.environ.get("DEEP_BATCH", "2"))
MIN_BODY     = int(os.environ.get("DEEP_MIN_BODY", "1200"))
BODY_CAP     = int(os.environ.get("DEEP_BODY_CAP", "12000"))
MAX_DATES    = int(os.environ.get("DEEP_MAX_DATES", "1"))
MAX_REQUESTS = int(os.environ.get("DEEP_MAX_REQUESTS", "18"))   # Flash 무료 20 RPD
TARGET_RATIO = float(os.environ.get("DEEP_TARGET_RATIO", "0.28"))
LEN_MIN, LEN_MAX = 700, 2100
LEN_HARD_MAX = int(os.environ.get("DEEP_LEN_HARD_MAX", "2300"))  # 장문 예외 허용치
RPM_GAP      = float(os.environ.get("DEEP_RPM_GAP", "13"))       # Flash 5 RPM → 13초
DRY_RUN      = os.environ.get("DEEP_DRY_RUN", "") == "1"
ONLY_DATE    = os.environ.get("DEEP_DATE", "").strip()
BODIES_DIR   = os.environ.get("DEEP_BODIES_DIR", "").strip()   # 있으면 bodies-{날짜}.json 재사용

DEEP_DIR = ROOT / "deep"
DEEP_DIR.mkdir(exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
HEADERS = {"User-Agent": UA,
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "Accept-Language": "en-US,en;q=0.9"}

DAILY_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.html$")
_requests_used = 0


def _txt(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip() if el else ""


# ── 1. 대상 날짜 고르기 ────────────────────────────────────────────
def target_dates():
    dates = []
    for f in ROOT.glob("archive/*.html"):
        m = DAILY_RE.match(f.name)
        if m:
            dates.append((m.group(1), f))
    dates.sort(reverse=True)
    if ONLY_DATE:
        return [(d, f) for d, f in dates if d == ONLY_DATE][:1]
    out = [(d, f) for d, f in dates if not (DEEP_DIR / f"{d}.json").exists()]
    return out[:MAX_DATES]


def existing_deep_by_url():
    """다른 날짜에 이미 있는 해설 — 같은 원문이면 재사용해 한도를 아낀다."""
    got = {}
    for j in DEEP_DIR.glob("*.json"):
        try:
            for url, v in json.loads(j.read_text(encoding="utf-8")).get("items", {}).items():
                if isinstance(v, dict) and v.get("deep"):
                    got[url] = v
        except Exception:
            pass
    return got


# ── 2. 카드 수집 ───────────────────────────────────────────────────
def collect_cards(path):
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    cards, seen = [], set()
    for c in soup.select(".jfnb-card"):
        url = c.get("data-card-url", "")
        if not url or url in seen:
            continue
        seen.add(url)
        cards.append({
            "id": c.get("id", ""),
            "url": url,
            "domain": urlparse(url).netloc.replace("www.", ""),
            "title_en": c.get("data-card-title", "")[:200],
            "title_kr": _txt(c.select_one(".article-title-kr, .title-kr")),
            "summary_now": _txt(c.select_one(".article-summary")),
        })
    return cards


# ── 3. 본문 추출 (deep_extract.py와 동일 로직) ─────────────────────
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
        body = trafilatura.extract(r.text, include_comments=False, include_tables=False,
                                   favor_precision=True, url=url) or ""
    except Exception:
        pass
    if len(body) < 400:
        soup = BeautifulSoup(r.text, "html.parser")
        for bad in soup.select("script,style,nav,footer,header,aside,form"):
            bad.decompose()
        alt = "\n".join(p for p in (_txt(p) for p in soup.find_all("p")) if len(p) > 60)
        if len(alt) > len(body):
            body = alt
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return (body, "ok") if body else ("", "empty")


# ── 4. 프롬프트 (확정 규격) ────────────────────────────────────────
SYSTEM = """너는 한국 경제·기술 매체의 외신 데스크다. 영문 기사 원문을 받아 '상세 해설'을 쓴다.
아래 규격은 확정된 것이다. 하나라도 어기면 그 원고는 폐기된다.

■ 넣는 것
· 원문의 수치·날짜·발언 주체·반론
· 발언은 간접화법 중심. 표현 자체가 중요한 대목만 짧게 인용(15자 안팎, 기사당 최대 1개)
· 고유명사는 원어를 괄호로 병기 — 사라 프라이어(Sarah Friar), 애브북스(AbeBooks)
· 문단마다 굵은 리드 문장으로 시작한다. **문장.** 형태이며, 원문 문장을 옮기는 것이 아니라
  그 문단의 내용을 요약해 새로 붙이는 것이다.

■ 절대 넣지 않는 것
· '한국 관점' 문단 — 전면 금지. 한국 이야기를 억지로 엮지 마라.
· 해석·전망·시장 함의 ("밸류에이션 논리가 바뀐다", "선례를 겨눈 포석" 류) — 금지.
· 원문에 없는 사실·수치·인용 — 근거가 없으면 그 대목을 통째로 빼라.
· 원문에 없는 약칭을 만들지 마라. 본문에 'Taiwan Semiconductor Manufacturing Co.'만 있으면
  'TSMC'라고 쓸 수 없다. GDP·EPS·CISA 같은 약칭도 본문에 실제로 있을 때만 쓴다.
· 의역으로 숫자를 만들지 마라. 'to the penny'를 '1센트'로, 'a quarter'(동전)를 '25센트'로
  바꾸면 안 된다.
· 소제목·불릿·번호 목록을 쓰지 마라. 문단만 쓴다.

■ 분량
· 기사마다 목표 글자수가 주어진다. 그 안에서 끝내라. 목표를 넘기면 폐기된다.
· 문단은 4~6개. 문단 수를 먼저 정하고 각 문단을 목표 글자수 나눈 만큼만 써라.
· 줄여야 하면 문장을 다듬지 말고 문단이나 사례를 통째로 빼라.
· 단, 반론·회사 측 해명·전문가 반박은 마지막까지 남긴다.

■ 기존 요약
함께 주는 '기존 요약'은 독자가 이미 읽은 것이다. 반복하지 말고 그다음 층위를 써라.
다만 기존 요약에만 있고 원문 본문에 없는 사실은 근거가 없는 것이므로 쓰지 마라."""

USER_TMPL = """다음 {n}건 각각에 대해 상세 해설을 써라.

{articles}

출력은 JSON 배열. 각 원소는 {{"i": <기사 번호>, "deep": "<해설 본문>"}}.
기사 번호를 절대 섞지 마라. 각 해설은 해당 번호의 기사 내용만으로 써야 한다."""

ART_TMPL = """───────── 기사 {i} ─────────
[매체] {domain}
[제목] {title_en}
[한글 제목] {title_kr}
[목표 분량] {target}자 (초과 금지)
[기존 요약 — 반복 금지] {summary_now}
[원문 본문]
{body}
"""

SCHEMA = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "properties": {"i": {"type": "INTEGER"}, "deep": {"type": "STRING"}},
        "required": ["i", "deep"],
    },
}


def target_len(body_len):
    return max(LEN_MIN, min(LEN_MAX, int(body_len * TARGET_RATIO)))


def build_prompt(batch):
    arts = "\n".join(
        ART_TMPL.format(i=a["i"], domain=a["domain"], title_en=a["title_en"],
                        title_kr=a["title_kr"] or "(없음)",
                        target=a["target"],
                        summary_now=a["summary_now"] or "(없음)",
                        body=a["body"][:BODY_CAP])
        for a in batch)
    return USER_TMPL.format(n=len(batch), articles=arts)


# ── 5. Gemini 호출 ─────────────────────────────────────────────────
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"

def call_gemini(prompt, tries=3):
    """반환: (파싱된 리스트 or None, 사유). 사유 'truncated'면 배치를 쪼개 재시도."""
    global _requests_used
    if _requests_used >= MAX_REQUESTS:
        return None, "budget-exhausted"
    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 32768,
            "responseMimeType": "application/json",
            "responseSchema": SCHEMA,
        },
    }
    last = ""
    for k in range(tries):
        _requests_used += 1
        try:
            r = requests.post(ENDPOINT.format(m=MODEL),
                              headers={"x-goog-api-key": API_KEY,
                                       "Content-Type": "application/json"},
                              json=payload, timeout=240)
        except Exception as e:
            last = f"net:{type(e).__name__}"
            time.sleep(5 * (k + 1)); continue

        if r.status_code == 429:
            wait = 20 * (k + 1) + random.uniform(0, 5)
            print(f"    429 — {wait:.0f}초 대기 후 재시도 ({k+1}/{tries})", flush=True)
            last = "429"; time.sleep(wait); continue
        if r.status_code != 200:
            return None, f"http:{r.status_code} {r.text[:200]}"

        try:
            j = r.json()
            cands = j.get("candidates") or []
            if not cands:
                return None, "no-candidate"
            fr = cands[0].get("finishReason", "")
            txt = "".join(p.get("text", "")
                          for p in cands[0].get("content", {}).get("parts", []))
            if fr and fr != "STOP":
                # MAX_TOKENS 등 — 잘렸다. 쪼개서 다시.
                return None, f"truncated:{fr}"
            data = json.loads(txt)
            if not isinstance(data, list):
                return None, "not-a-list"
            return data, "ok"
        except json.JSONDecodeError:
            return None, "truncated:json"
        except Exception as e:
            return None, f"parse:{type(e).__name__}"
    return None, last


def generate(batch):
    """배치 하나를 생성한다. 잘리면 1건씩 쪼개 재시도."""
    data, why = call_gemini(build_prompt(batch))
    if data is not None:
        got = {int(o.get("i", -1)): (o.get("deep") or "") for o in data if isinstance(o, dict)}
        missing = [a for a in batch if not got.get(a["i"])]
        if not missing:
            return got, "ok"
        print(f"    응답 누락 {len(missing)}건 — 개별 재시도", flush=True)
    elif why.startswith("truncated"):
        print(f"    {why} — 1건씩 쪼개 재시도", flush=True)
        got = {}
    else:
        return {}, why

    if len(batch) == 1:
        return got, why
    for a in batch:
        if got.get(a["i"]):
            continue
        time.sleep(RPM_GAP)
        d, w = call_gemini(build_prompt([a]))
        if d:
            for o in d:
                if isinstance(o, dict) and o.get("deep"):
                    got[a["i"]] = o["deep"]
        else:
            print(f"      기사 {a['i']} 실패 — {w}", flush=True)
    return got, "ok"


# ── 6. 검증 게이트 ─────────────────────────────────────────────────
def gate(article, deep):
    """통과하면 (True, []), 아니면 (False, [사유...])"""
    reasons = []
    n = len(deep)
    if n < LEN_MIN:
        reasons.append(f"분량 미달 {n}자")
    if n > LEN_HARD_MAX:
        reasons.append(f"분량 초과 {n}자")
    if "한국 관점" in deep:
        reasons.append("'한국 관점' 문단")
    if not deep.lstrip().startswith("**"):
        reasons.append("굵은 리드 문장 없음")
    pn, pt, q = V.check_article(article, deep)
    for raw, ctx in pn:
        reasons.append(f"수치 미대조 {raw}")
    for t, ctx in pt:
        reasons.append(f"고유명사 미대조 {t}")
    for x in q:
        reasons.append(f"직접인용 {len(x)}자")
    return (not reasons), reasons


REPAIR_TMPL = """아래 해설 초고가 검증에서 걸렸다. 지적된 것만 고쳐서 다시 써라.

[검증 지적]
{problems}

[고치는 방법]
· '수치 미대조' / '고유명사 미대조' — 그 표현은 원문 본문에 없다. 해당 대목을 통째로 빼거나
  원문에 실제로 있는 표기로 바꿔라. 새로운 사실을 채워 넣지 마라.
· '분량 초과' — 문장을 다듬지 말고 문단이나 사례를 통째로 빼라. 목표는 {target}자다.
  단, 반론·회사 측 해명·전문가 반박은 남겨라.
· '직접인용' — 간접화법으로 바꿔라.
· '한국 관점' — 그 문단을 통째로 삭제하라.
· '굵은 리드 문장 없음' — 각 문단을 **굵은 리드 문장.** 으로 시작하게 하라.

[원문 본문]
{body}

[고칠 초고]
{deep}

출력은 JSON 배열 하나, 원소 하나: [{{"i": {i}, "deep": "<고친 해설>"}}]"""


def repair(a, deep, reasons):
    """검증에 걸린 초고를 한 번만 고쳐 본다. 실패하면 호출한 쪽에서 버린다."""
    prompt = REPAIR_TMPL.format(
        problems="\n".join("· " + r for r in reasons[:12]),
        target=a["target"], body=a["body"][:BODY_CAP], deep=deep, i=a["i"])
    data, why = call_gemini(prompt, tries=2)
    if not data:
        return None, why
    for o in data:
        if isinstance(o, dict) and o.get("deep"):
            return o["deep"].strip(), "ok"
    return None, "empty"


# ── 7. 실행 ────────────────────────────────────────────────────────
def run_date(date, path, reuse):
    print(f"\n■ {date} — {path.name}", flush=True)
    cards = collect_cards(path)
    if not cards:
        print("  .jfnb-card 가 없다. post_process 가 아직 안 돈 파일일 수 있다. 건너뜀.",
              flush=True)
        return None
    print(f"  카드 {len(cards)}건", flush=True)

    items, todo = {}, []
    for c in cards:
        if c["url"] in reuse:
            items[c["url"]] = dict(reuse[c["url"]])
            continue
        todo.append(c)
    if items:
        print(f"  기존 해설 재사용 {len(items)}건", flush=True)

    cached = {}
    if BODIES_DIR:
        bp = Path(BODIES_DIR) / f"bodies-{date}.json"
        if bp.exists():
            cached = {a["url"]: a for a in
                      json.loads(bp.read_text(encoding="utf-8")).get("articles", [])}
            print(f"  로컬 본문 {len(cached)}건 재사용 ({bp.name})", flush=True)

    print("  본문 추출", flush=True)
    ready = []
    for i, c in enumerate(todo):
        if c["url"] in cached:
            body, why = cached[c["url"]].get("body", ""), cached[c["url"]].get("why", "ok")
        else:
            body, why = extract(c["url"])
        c["body"] = body[:BODY_CAP]
        c["state"] = ("extract_fail" if why != "ok"
                      else "too_short" if len(body) < MIN_BODY else "ready")
        print(f"    [{i+1:2d}/{len(todo)}] {c['domain']:<20} {len(body):>6}자  {c['state']}",
              flush=True)
        if c["state"] == "ready":
            ready.append(c)
        if c["url"] not in cached:
            time.sleep(0.7)

    if not ready:
        print("  생성 대상 없음", flush=True)
        return items, [], []

    for i, c in enumerate(ready):
        c["i"] = i + 1
        c["target"] = target_len(len(c["body"]))

    batches = [ready[i:i + BATCH] for i in range(0, len(ready), BATCH)]
    print(f"  생성 — {len(ready)}건 / {len(batches)}요청 (배치 {BATCH})", flush=True)

    passed, dropped = [], []
    for bi, b in enumerate(batches):
        if DRY_RUN:
            got = {a["i"]: f"**드라이런.** {a['title_kr'] or a['title_en']}" for a in b}
        else:
            t0 = time.time()
            got, why = generate(b)
            if bi < len(batches) - 1:
                time.sleep(max(0, RPM_GAP - (time.time() - t0)))
        for a in b:
            deep = (got.get(a["i"]) or "").strip()
            if not deep:
                dropped.append((a, ["생성 실패"])); continue
            if DRY_RUN:
                passed.append((a, deep)); continue
            ok, reasons = gate(a, deep)
            if not ok:
                print(f"      기사 {a['i']} 검증 실패 — 수리 시도: {'; '.join(reasons[:3])}",
                      flush=True)
                time.sleep(RPM_GAP)
                fixed, why = repair(a, deep, reasons)
                if fixed:
                    ok2, r2 = gate(a, fixed)
                    if ok2:
                        deep, ok, reasons = fixed, True, []
                    else:
                        reasons = [f"수리 후에도: {r}" for r in r2]
                else:
                    reasons = reasons + [f"수리 실패({why})"]
            if ok:
                passed.append((a, deep))
            else:
                dropped.append((a, reasons))
        print(f"    [{bi+1}/{len(batches)}] 통과 {len(passed)} / 탈락 {len(dropped)}",
              flush=True)

    for a, deep in passed:
        items[a["url"]] = {"deep": deep, "by": MODEL, "n": len(deep)}
    return items, passed, dropped


def main():
    if not API_KEY and not DRY_RUN:
        print("GEMINI_API_KEY 가 없습니다.", file=sys.stderr); sys.exit(1)

    targets = target_dates()
    if not targets:
        print("새로 해설을 만들 날짜가 없습니다.")
        return
    reuse = existing_deep_by_url()
    print(f"기존 해설 {len(reuse)}건 보유 · 대상 {[d for d, _ in targets]}", flush=True)

    report = ["# 📖 상세 해설 자동 생성 결과\n"]
    wrote = 0
    for date, path in targets:
        res = run_date(date, path, reuse)
        if not res:
            continue
        items, passed, dropped = res
        if not items:
            print(f"  {date} — 저장할 항목이 없어 파일을 만들지 않는다.", flush=True)
            continue
        out = {"date": date, "v": 1, "items": items}
        (DEEP_DIR / f"{date}.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        wrote += 1
        tb = sum(len(a["body"]) for a, _ in passed) or 1
        td = sum(len(d) for _, d in passed)
        print(f"  ✅ deep/{date}.json — {len(items)}건 저장 "
              f"(신규 {len(passed)} · 탈락 {len(dropped)})", flush=True)
        report.append(f"## {date}\n")
        report.append(f"- 저장 **{len(items)}건** (신규 {len(passed)} · 탈락 {len(dropped)})")
        if passed:
            report.append(f"- 신규분 원문 {tb:,}자 → 해설 {td:,}자 = {td/tb*100:.1f}%")
        if dropped:
            report.append("\n### 탈락 (검증 미통과 — 저장하지 않음)\n")
            report.append("| 기사 | 사유 |")
            report.append("|---|---|")
            for a, rs in dropped:
                report.append(f"| {a.get('title_kr') or a.get('title_en','')[:60]} | "
                              f"{'; '.join(rs[:4])} |")
        report.append("")

    report.append(f"\nGemini 호출 {_requests_used}회 (상한 {MAX_REQUESTS})")
    (ROOT / "out").mkdir(exist_ok=True)
    (ROOT / "out" / "deep-generate.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"\n■ 완료 — 파일 {wrote}개 · Gemini 호출 {_requests_used}회", flush=True)


if __name__ == "__main__":
    main()
