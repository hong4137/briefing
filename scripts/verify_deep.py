#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_deep.py — 상세 해설(deep) 초안을 원문(bodies)과 대조한다.
usage: python verify_deep.py bodies-YYYY-MM-DD.json deep/YYYY-MM-DD.json
인계서 3-3 기준.
"""
import json, re, sys, unicodedata

MEDIA_WHITELIST = {
    # 매체명 (원문에 자기 이름을 안 쓰는 경우가 많음)
    'cnbc','techcrunch','wired','zdnet','the','verge','theverge','guardian','ars','technica',
    'arstechnica','reuters','bloomberg','axios','engadget','ap','afp','ft','financial','times',
    'wsj','wall','street','journal','nyt','new','york','information','businessinsider','insider',
    'cnn','bbc','nikkei','techmeme','theinformation','forbes','fortune','semafor','politico',
    'washington','post','404','media','platformer','404media','yonhap','venturebeat','protocol',
    'scmp','morning','south','china','tech','review','mit','theregister','register','gizmodo',
    'businesswire','prnewswire','staff','com','co','uk','www','http','https',
}
SCALE = {'thousand':1e3,'million':1e6,'m':1e6,'bn':1e9,'billion':1e9,'trillion':1e12,'b':1e9,
         'k':1e3,'crore':1e7,'lakh':1e5}
KSCALE = {'천':1e3,'만':1e4,'억':1e8,'조':1e12,'백만':1e6,'십억':1e9}
WORDNUM = {'zero':0,'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,
    'nine':9,'ten':10,'eleven':11,'twelve':12,'dozen':12,'thirteen':13,'fourteen':14,
    'fifteen':15,'sixteen':16,'seventeen':17,'eighteen':18,'nineteen':19,'twenty':20,
    'thirty':30,'forty':40,'fifty':50,'sixty':60,'seventy':70,'eighty':80,'ninety':90,
    'hundred':100,'thousand':1000,'million':1e6,'billion':1e9,'trillion':1e12,
    'first':1,'second':2,'third':3,'fourth':4,'fifth':5,'sixth':6,'seventh':7,'eighth':8,
    'ninth':9,'tenth':10,'half':0.5,'quarter':0.25,'twice':2,'double':2,'triple':3,
    'once':1,'single':1,'both':2,'couple':2,'pair':2,'trio':3,'dual':2,
    'decade':10,'century':100,'score':20,'quintet':5,'quadruple':4,'sole':1,'lone':1,
    'twelfth':12,'eleventh':11,'twentieth':20,'thirtieth':30,
    'twenties':20,'thirties':30,'forties':40,'fifties':50,'sixties':60,'seventies':70,
    'eighties':80,'nineties':90,'teens':10,'quarterly':4,'biweekly':2,'fortnight':14}
MONTHS = {'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,'july':7,'august':8,
    'september':9,'october':10,'november':11,'december':12,'jan':1,'feb':2,'mar':3,'apr':4,
    'jun':6,'jul':7,'aug':8,'sep':9,'sept':9,'oct':10,'nov':11,'dec':12}
WEEKNUM = {}  # 요일은 숫자 대조 대상 아님

NUM_RE = re.compile(r'(\d[\d,]*(?:\.\d+)?)')

def norm_body(b):
    b = unicodedata.normalize('NFKC', b)
    # 원문 표기 오류: "$17. 3 billion" 같은 공백 삽입 허용
    b = re.sub(r'(\d)\.\s+(\d)', r'\1.\2', b)
    # 1,234 -> 1234 는 별도 처리
    return b

def f(v):
    """값을 정규화(유효숫자 9자리로 부동소수 오차 흡수)"""
    return float('%.9g' % float(v))

def body_values(body):
    """본문에 등장하는 모든 수치를 값 집합으로 환산"""
    b = norm_body(body)
    vals = set()
    low = b.lower()
    for m in NUM_RE.finditer(b):
        raw = m.group(1)
        try:
            v = float(raw.replace(',', ''))
        except ValueError:
            continue
        vals.add(f(v))
        tail = low[m.end():m.end()+16]
        for w, s in SCALE.items():
            if re.match(r'\s*%s\b' % w, tail):
                vals.add(f(v * s)); break
        # 퍼센트/기타는 값 그대로
        # 소수점 뒤 0 제거형(4.0 -> 4)
        if v == int(v):
            vals.add(f(int(v)))
    # 영어 수사
    for w, v in WORDNUM.items():
        if re.search(r'\b%s\b' % re.escape(w), low):
            vals.add(f(v))
            for w2, s in SCALE.items():
                if re.search(r'\b%s[- ]%s\b' % (re.escape(w), w2), low):
                    vals.add(f(v * s))
    # "a/half a billion" 류
    for w2, s in SCALE.items():
        if re.search(r'\bhalf a %s\b' % w2, low):
            vals.add(f(0.5 * s))
    # 영어 복합 수사 (two-hundred, twenty-five, three hundred thousand ...)
    WU = {'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,
          'ten':10,'eleven':11,'twelve':12,'thirteen':13,'fourteen':14,'fifteen':15,
          'sixteen':16,'seventeen':17,'eighteen':18,'nineteen':19,'twenty':20,'thirty':30,
          'forty':40,'fifty':50,'sixty':60,'seventy':70,'eighty':80,'ninety':90}
    WM = {'hundred':100,'thousand':1000,'million':1e6,'billion':1e9,'trillion':1e12}
    words = re.findall(r"[a-z]+(?:[- ][a-z]+)*", low)
    for phrase in words:
        toks = re.split(r'[- ]', phrase)
        i = 0
        while i < len(toks):
            if toks[i] not in WU:
                i += 1; continue
            j = i; cur = 0; run = 0; ok = False
            while j < len(toks):
                t = toks[j]
                if t in WU:
                    run += WU[t]; ok = True; j += 1
                elif t in WM:
                    run = (run or 1) * WM[t]
                    cur += run; run = 0; ok = True; j += 1
                elif t == 'and' and j + 1 < len(toks) and (toks[j+1] in WU or toks[j+1] in WM):
                    j += 1
                else:
                    break
            if ok and (cur + run) > 0:
                vals.add(f(cur + run))
            i = max(j, i + 1)
    # 월 이름 -> 숫자
    for w, v in MONTHS.items():
        if re.search(r'\b%s\b' % w, low):
            vals.add(f(v))
    return vals

KUNIT = {'조': 1e12, '억': 1e8, '만': 1e4, '천': 1e3}
COMPOUND_RE = re.compile(r'(?:\d[\d,]*(?:\.\d+)?\s*[조억만천]\s*)+(?:\d[\d,]*(?:\.\d+)?)?')

def deep_numbers(deep):
    """해설에 등장하는 수치를 (원문표기, 환산값들, 문맥) 목록으로.
    한국식 복합 단위(1조 2,500억 / 1억 2,280만)를 하나의 값으로 합산한다."""
    d = unicodedata.normalize('NFKC', deep)
    out = []
    consumed = []
    for m in COMPOUND_RE.finditer(d):
        seg = m.group(0)
        parts = re.findall(r'(\d[\d,]*(?:\.\d+)?)\s*([조억만천]?)', seg)
        parts = [(a, b) for a, b in parts if a]
        if len(parts) < 2 and not (parts and parts[0][1]):
            continue
        total = 0.0
        for numtxt, unit in parts:
            v = float(numtxt.replace(',', ''))
            total += v * KUNIT.get(unit, 1)
        cands = {f(total)}
        # 단일 단위인 경우 원 숫자도 후보(예: 400억 -> 400 자체가 본문에 있을 수도)
        for numtxt, unit in parts:
            cands.add(f(float(numtxt.replace(',', ''))))
            if unit:
                cands.add(f(float(numtxt.replace(',', '')) * KUNIT[unit]))
        ctx = d[max(0, m.start() - 14):m.end() + 14].replace('\n', ' ')
        out.append((seg.strip(), cands, ctx))
        consumed.append((m.start(), m.end()))

    def inside(i):
        return any(a <= i < b for a, b in consumed)

    for m in NUM_RE.finditer(d):
        if inside(m.start()):
            continue
        raw = m.group(1)
        try:
            v = float(raw.replace(',', ''))
        except ValueError:
            continue
        cands = {f(v)}
        tail = d[m.end():m.end() + 4]
        for w, sc in sorted(KSCALE.items(), key=lambda x: -len(x[0])):
            if tail.startswith(w):
                cands.add(f(v * sc))
                break
        ctx = d[max(0, m.start() - 14):m.end() + 14].replace('\n', ' ')
        out.append((raw, cands, ctx))
    return out

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9&'’\.\-]*")

def latin_tokens(deep):
    toks = []
    for m in TOKEN_RE.finditer(deep):
        t = m.group(0).strip(".-'’")
        if not t or len(t) < 2:
            continue
        toks.append((t, deep[max(0, m.start()-12):m.end()+12].replace('\n', ' ')))
    return toks

QUOTE_RE = re.compile(r'[\"“]([^\"“”]{1,400})[\"”]')

def check_article(art, deep):
    body = art['body']
    bl = norm_body(body).lower()
    bvals = body_values(body)
    prob_num, prob_tok = [], []
    for raw, cands, ctx in deep_numbers(deep):
        if any(c in bvals for c in cands):
            continue
        # 본문에 문자열 그대로 있으면 통과(연도·모델명 등)
        if raw.lower() in bl or raw.replace(',', '') in bl.replace(',', ''):
            continue
        prob_num.append((raw, ctx))
    seen = set()
    for t, ctx in latin_tokens(deep):
        tl = t.lower()
        if tl in MEDIA_WHITELIST or tl in seen:
            continue
        seen.add(tl)
        if tl in bl:
            continue
        # 하이픈/점 제거 후 재시도
        alt = re.sub(r"[\.\-'’]", '', tl)
        if alt and alt in re.sub(r"[\.\-'’]", '', bl):
            continue
        prob_tok.append((t, ctx))
    quotes = [q for q in QUOTE_RE.findall(deep) if len(q) > 20]
    return prob_num, prob_tok, quotes

def main():
    bodies_path, deep_path = sys.argv[1], sys.argv[2]
    bodies = json.load(open(bodies_path, encoding='utf-8'))
    deepj = json.load(open(deep_path, encoding='utf-8'))
    by_url = {a['url']: a for a in bodies['articles']}
    items = deepj['items']
    total_body = 0
    total_deep = 0
    n_prob = 0
    print('=' * 74)
    print('  %s  vs  %s' % (bodies_path, deep_path))
    print('=' * 74)
    missing = [u for u in items if u not in by_url]
    if missing:
        print('!! bodies에 없는 URL 키 %d건' % len(missing))
        for u in missing: print('   ', u)
        n_prob += len(missing)
    ready = [a for a in bodies['articles'] if a['state'] == 'ready']
    notcov = [a['id'] for a in ready if a['url'] not in items]
    if notcov:
        print('!! ready인데 해설 없음: %s' % ', '.join(notcov))
    for url, ent in items.items():
        art = by_url.get(url)
        if not art:
            continue
        deep = ent['deep']
        bl, dl = len(art['body']), len(deep)
        total_body += bl; total_deep += dl
        pn, pt, q = check_article(art, deep)
        flag = ''
        if dl < 700 or dl > 2100: flag += ' [분량이탈]'
        if '한국' in deep: flag += ' [한국관점?]'
        if ent.get('n') != dl: flag += ' [n불일치 n=%s]' % ent.get('n')
        status = 'OK' if not (pn or pt or q or flag) else '**'
        print('\n%s %-7s %-20s body %5d -> deep %4d (%4.1f%%)%s'
              % (status, art['id'], art['domain'], bl, dl, dl / bl * 100, flag))
        for raw, ctx in pn:
            print('    [수치 미대조] %-10s … %s' % (raw, ctx)); n_prob += 1
        for t, ctx in pt:
            print('    [고유명사 미대조] %-22s … %s' % (t, ctx)); n_prob += 1
        for x in q:
            print('    [직접인용 20자 초과 %d자] %s' % (len(x), x[:60])); n_prob += 1
    print('\n' + '=' * 74)
    print('기사 %d건 / 원문 %d자 -> 해설 %d자 = %.1f%%  (적정 25~35%%)'
          % (len(items), total_body, total_deep, total_deep / total_body * 100))
    print("'한국 관점' 문단: %d건" % sum(1 for e in items.values() if '한국 관점' in e['deep']))
    print('미대조/경고 항목 총 %d건' % n_prob)
    print('=' * 74)
    return 1 if n_prob else 0

if __name__ == '__main__':
    sys.exit(main())
