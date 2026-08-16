/*!
 * JFNB 공통 스크립트 v2 — 북마크 · 딥링크 · 하이라이트 · 복사 + 구글 로그인 동기화
 *
 * post_process.py가 아카이브 HTML head에 <script src="../app.js?v=N" defer>로 주입한다.
 * 카드 탐지는 빌드 타임에 끝나 있다 — 이 파일은 .jfnb-card 와 data-* 속성만 읽는다.
 *
 * ── 로그인 설계 (계획서 v2.3 / 사양서 v1.0) ──────────────────────────
 *  · 비로그인 = 지금까지와 완전히 동일. Firebase SDK를 한 바이트도 받지 않는다.
 *  · 로그인   = 북마크 기기 간 동기화 + '안 본 브리핑' 표시
 *  · 열람 기록(visits)은 서버가 유일한 진실. 병합 로직이 없다.
 *
 * 🔴 signInWithPopup 고정. signInWithRedirect는 이 사이트에서 동작하지 않는다.
 *    앱 도메인(hong4137.github.io)과 authDomain이 달라 교차 출처 iframe에 의존하는데,
 *    Chrome 115+ / Firefox 109+ / Safari 16.1+ 가 서드파티 저장소를 차단한다.
 *    튜토리얼·생성 코드가 거의 항상 틀리는 지점이므로 절대 바꾸지 말 것.
 */
(function () {
  'use strict';

  /* ══════════════ 설정 ══════════════ */

  var KEY = 'jfnb-saved-articles';
  var MAX = 200;                       // hong4137.github.io는 다른 Pages 프로젝트와 5MB 한도를 공유한다
  var AUTH_MARK = 'jfnb-auth';         // '1'이면 이전에 로그인한 적 있음 → SDK 선로딩
  var HINT_KEY = 'jfnb-hint-dismissed';
  var SEEN_SENT = 'jfnb-seen-sent';    // sessionStorage. lastSeen 세션당 1회 제한

  var CUTOFF_DAYS = 14;                // '안 본 브리핑' 표시 범위
  var DWELL_MS = 5000;                 // 열람 판정 체류 시간

  var FB = {
    apiKey: "AIzaSyAWeFu6IZBEcD1VeThqXkNP6XiWQPDnUfA",
    authDomain: "briefing-login.firebaseapp.com",
    projectId: "briefing-login",
    storageBucket: "briefing-login.firebasestorage.app",
    messagingSenderId: "1044512119500",
    appId: "1:1044512119500:web:c5d783c3e68770e5d34069"
  };
  var FB_VER = '12.17.1';
  function cdn(mod) {
    return 'https://www.gstatic.com/firebasejs/' + FB_VER + '/firebase-' + mod + '.js';
  }

  /* ══════════════ 저장소 (로컬) ══════════════ */

  function load() {
    try {
      var v = JSON.parse(localStorage.getItem(KEY) || '[]');
      return Array.isArray(v) ? v : [];
    } catch (e) { return []; }
  }

  function save(list) {
    try {
      localStorage.setItem(KEY, JSON.stringify(list.slice(0, MAX)));
      return true;
    } catch (e) {
      try {
        localStorage.setItem(KEY, JSON.stringify(list.slice(0, Math.floor(MAX / 2))));
        return true;
      } catch (e2) { return false; }
    }
  }

  function stem() {
    return (location.pathname.split('/').pop() || '').replace('.html', '');
  }

  // 일간·특별판은 원문 URL이 키다(재발행으로 순서가 바뀌어도 안전).
  // 주간은 원문 링크가 없으므로 파일 stem + 앵커를 키로 쓴다.
  function keyOf(card) {
    return card.getAttribute('data-card-url') || (stem() + '#' + card.id);
  }

  function indexOfKey(list, k) {
    for (var i = 0; i < list.length; i++) if (list[i].k === k) return i;
    return -1;
  }

  /* ══════════════ 유틸 ══════════════ */

  function titleOf(card) {
    var t = card.getAttribute('data-card-title');
    if (t) return t;
    var h = card.querySelector('h2, h3, h4, [class*="title"]');
    return h ? h.textContent.replace(/\s+/g, ' ').trim() : '(제목 없음)';
  }

  // 한글 제목이 따로 있으면 그것을 우선한다 (일간은 h3가 영문 제목이다)
  function displayTitle(card) {
    var kr = card.querySelector('.article-title-kr, .title-kr');
    if (kr && kr.textContent.trim()) return kr.textContent.replace(/\s+/g, ' ').trim();
    return titleOf(card);
  }

  function summaryOf(card) {
    var el = card.querySelector('.article-summary, .summary, p.status, p');
    return el ? el.textContent.replace(/\s+/g, ' ').trim() : '';
  }

  function toast(msg) {
    var d = document.createElement('div');
    d.className = 'jfnb-toast';
    d.textContent = msg;
    document.body.appendChild(d);
    setTimeout(function () { d.classList.add('on'); }, 10);
    setTimeout(function () {
      d.classList.remove('on');
      setTimeout(function () { d.remove(); }, 300);
    }, 1800);
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text)
        .then(function () { toast('복사했습니다'); })
        .catch(function () { fallbackCopy(text); });
    } else {
      fallbackCopy(text);
    }
  }

  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.cssText = 'position:fixed;top:-9999px;opacity:0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); toast('복사했습니다'); }
    catch (e) { toast('복사에 실패했습니다'); }
    ta.remove();
  }

  /* ══════════════ Firebase — 지연 로딩 ══════════════ */

  var fb = null;            // { app, auth, db, A(auth모듈), F(firestore모듈) }
  var fbPromise = null;
  var user = null;          // 현재 로그인 사용자
  var visits = null;        // { since, seen:{} } — 서버가 유일 진실
  var retryQueue = [];      // 열람 기록 전송 실패분. 재시도 1회면 충분하다

  function initFirebase() {
    if (fbPromise) return fbPromise;
    fbPromise = Promise.all([
      import(cdn('app')), import(cdn('auth')), import(cdn('firestore'))
    ]).then(function (m) {
      var appMod = m[0], A = m[1], F = m[2];
      var app = appMod.initializeApp(FB);
      fb = { app: app, auth: A.getAuth(app), db: F.getFirestore(app), A: A, F: F };
      A.onAuthStateChanged(fb.auth, onAuthChanged);
      return fb;
    }).catch(function (e) {
      fbPromise = null;                       // 다음 시도를 막지 않는다
      console.warn('[jfnb] Firebase 로드 실패', e);
      throw e;
    });
    return fbPromise;
  }

  function doLogin() {
    initFirebase().then(function (f) {
      // 🔴 signInWithPopup — signInWithRedirect로 바꾸지 말 것 (파일 상단 주석 참조)
      return f.A.signInWithPopup(f.auth, new f.A.GoogleAuthProvider());
    }).catch(function (e) {
      if (e && (e.code === 'auth/popup-closed-by-user' || e.code === 'auth/cancelled-popup-request')) return;
      toast('로그인에 실패했습니다');
    });
  }

  function doLogout() {
    if (!fb) return;
    fb.A.signOut(fb.auth).catch(function () {});
  }

  function onAuthChanged(u) {
    user = u || null;
    if (user) {
      try { localStorage.setItem(AUTH_MARK, '1'); } catch (e) {}
      upsertProfile();
      pullCloud();
    } else {
      // 로그아웃 시 로컬 캐시를 비운다 — 서버에 있으므로 잃는 게 없고,
      // 공용 PC에서 남의 보관함이 남는 쪽이 더 나쁘다 (결정 #9)
      try {
        localStorage.removeItem(AUTH_MARK);
        localStorage.removeItem(KEY);
      } catch (e) {}
      visits = null;
      refreshBookmarkButtons();
      applyUnread();
      paintCount(0);
    }
    renderAuthUI();
    renderHint();
  }

  /* ── profiles: 회원 파악용. 콘솔에서 한 화면에 보이도록 플랫 컬렉션 ── */
  function upsertProfile() {
    if (!fb || !user) return;
    var F = fb.F;
    var ref = F.doc(fb.db, 'profiles', user.uid);
    var now = Date.now();
    var already = false;
    try { already = sessionStorage.getItem(SEEN_SENT) === '1'; } catch (e) {}
    if (already) return;                       // lastSeen은 세션당 1회만

    F.setDoc(ref, {
      nickname: (user.displayName || '').slice(0, 50),
      firstSeen: now,
      lastSeen: now
    }, { merge: true }).then(function () {
      try { sessionStorage.setItem(SEEN_SENT, '1'); } catch (e) {}
      // firstSeen은 최초값을 지켜야 하므로 이미 있으면 되돌린다
      return F.getDoc(ref);
    }).then(function (snap) {
      if (!snap || !snap.exists()) return;
      var d = snap.data() || {};
      if (d.firstSeen && d.firstSeen < now) return;   // 이미 이전 값이 있으면 그대로
    }).catch(function () {});
  }

  /* ── 클라우드에서 끌어오기 ── */
  function pullCloud() {
    if (!fb || !user) return;
    var F = fb.F;
    var bRef = F.doc(fb.db, 'users', user.uid, 'data', 'bookmarks');
    var vRef = F.doc(fb.db, 'users', user.uid, 'data', 'visits');

    // 1) 북마크 — 병합. 덮어쓰지 않는다
    F.getDoc(bRef).then(function (snap) {
      var server = (snap.exists() && Array.isArray(snap.data().items)) ? snap.data().items : [];
      var local = load();
      var merged = mergeItems(local, server);
      save(merged);
      refreshBookmarkButtons();
      paintCount(merged.length);
      if (merged.length !== server.length || local.length) {
        return F.setDoc(bRef, { items: merged, updatedAt: F.serverTimestamp() });
      }
    }).catch(function (e) { console.warn('[jfnb] 북마크 동기화 실패', e); });

    // 2) 열람 기록 — 없으면 지금을 기준선(since)으로 생성
    F.getDoc(vRef).then(function (snap) {
      if (snap.exists()) {
        var d = snap.data() || {};
        visits = { since: d.since || Date.now(), seen: d.seen || {} };
      } else {
        visits = { since: Date.now(), seen: {} };
        return F.setDoc(vRef, {
          since: visits.since, seen: {}, updatedAt: F.serverTimestamp()
        });
      }
    }).then(function () {
      applyUnread();
      scheduleVisit();
      flushRetry();
    }).catch(function (e) { console.warn('[jfnb] 열람 기록 로드 실패', e); });
  }

  // 합집합. 같은 k면 ts가 더 이른 것을 남긴다 (담은 시점 보존)
  function mergeItems(local, server) {
    var map = {};
    server.forEach(function (x) { if (x && x.k) map[x.k] = x; });
    local.forEach(function (x) {
      if (!x || !x.k) return;
      var e = map[x.k];
      if (!e || (x.ts || 0) < (e.ts || 0)) map[x.k] = x;
    });
    var out = Object.keys(map).map(function (k) { return map[k]; });
    out.sort(function (a, b) { return (b.ts || 0) - (a.ts || 0); });
    return out.slice(0, MAX);
  }

  /* ── 북마크 서버 반영 (디바운스) ── */
  var pushTimer = null;
  function pushBookmarks() {
    if (!fb || !user) return;
    clearTimeout(pushTimer);
    pushTimer = setTimeout(function () {
      var F = fb.F;
      F.setDoc(F.doc(fb.db, 'users', user.uid, 'data', 'bookmarks'),
        { items: load(), updatedAt: F.serverTimestamp() })
        .catch(function (e) { console.warn('[jfnb] 북마크 저장 실패', e); });
    }, 2500);
  }

  /* ── 열람 기록: 5초 체류 후 1회 ── */
  function scheduleVisit() {
    if (!document.querySelector('.jfnb-card')) return;   // 상세 페이지에서만
    setTimeout(function () {
      if (!user || !visits) return;
      var s = stem();
      if (!s || visits.seen[s]) return;                  // 이미 본 날이면 서버 쓰기 0
      visits.seen[s] = Date.now();
      writeVisit(s, visits.seen[s]);
    }, DWELL_MS);
  }

  function writeVisit(s, ts) {
    if (!fb || !user) { retryQueue.push([s, ts]); return; }
    var F = fb.F;
    // ⚠️ 문서 전체를 덮어쓰지 않는다. 필드 하나만 갱신해야 다른 탭의 기록이 안 날아간다.
    //    stem에 특수문자가 있어도 안전하도록 FieldPath를 쓴다.
    F.updateDoc(
      F.doc(fb.db, 'users', user.uid, 'data', 'visits'),
      new F.FieldPath('seen', s), ts,
      'updatedAt', F.serverTimestamp()
    ).catch(function () {
      retryQueue.push([s, ts]);                          // 재시도 1회면 충분하다
    });
  }

  function flushRetry() {
    if (!retryQueue.length || !fb || !user) return;
    var q = retryQueue.slice();
    retryQueue.length = 0;
    q.forEach(function (p) { writeVisit(p[0], p[1]); });
  }

  /* ══════════════ '안 본 브리핑' ══════════════ */

  // stem 끝의 YYYY-MM-DD로 발행일을 뽑는다.
  // 특별판(ces-2026-special 등)은 날짜가 없어 0 → 판정 대상에서 제외된다.
  function publishTs(s) {
    var m = /(\d{4})-(\d{2})-(\d{2})$/.exec(s || '');
    if (!m) return 0;
    return new Date(+m[1], +m[2] - 1, +m[3], 9, 0, 0).getTime();
  }

  function applyUnread() {
    var nodes = document.querySelectorAll('[data-briefing]');
    var n = 0;
    if (visits) {
      var floor = Math.max(visits.since || 0, Date.now() - CUTOFF_DAYS * 864e5);
      Array.prototype.forEach.call(nodes, function (el) {
        var s = el.getAttribute('data-briefing');
        var ts = publishTs(s);
        var unread = !!(ts && ts >= floor && !visits.seen[s]);
        el.classList.toggle('jfnb-unread', unread);
        if (unread) n++;
      });
    } else {
      Array.prototype.forEach.call(nodes, function (el) { el.classList.remove('jfnb-unread'); });
    }
    var c = document.querySelector('[data-jfnb-unread]');
    if (c) c.textContent = n ? '안 본 브리핑 ' + n : '';
  }

  // 목록은 비동기 렌더다. DOMContentLoaded 시점엔 아직 비어 있다.
  function observeList() {
    var t = document.getElementById('archive-container')
         || document.getElementById('special-container')
         || document.querySelector('main');
    if (!t || !window.MutationObserver) return;
    // childList만 관찰한다 — class 토글은 attribute 변경이라 재귀하지 않는다
    new MutationObserver(function () { applyUnread(); })
      .observe(t, { childList: true, subtree: true });
  }

  /* ══════════════ 로그인 UI ══════════════ */

  function renderAuthUI() {
    var slots = document.querySelectorAll('[data-jfnb-auth]');
    Array.prototype.forEach.call(slots, function (el) {
      el.innerHTML = '';
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'jfnb-auth-btn';
      if (user) {
        var name = (user.displayName || '내 계정').split(' ')[0];
        b.textContent = name;
        b.title = '로그아웃';
        b.setAttribute('aria-label', name + ' — 클릭하면 로그아웃');
        b.addEventListener('click', doLogout);
      } else {
        b.textContent = '로그인';
        b.title = 'Google 계정으로 로그인';
        b.addEventListener('click', doLogin);
      }
      el.appendChild(b);
    });
  }

  // 아카이브 목록 상단 유도 배너. 벽을 세우지 않는다.
  function renderHint() {
    var host = document.getElementById('archive-container');
    if (!host) return;
    var old = document.querySelector('.jfnb-hint');
    if (old) old.remove();
    if (user) return;
    var dismissed = false;
    try { dismissed = localStorage.getItem(HINT_KEY) === '1'; } catch (e) {}
    if (dismissed) return;

    var box = document.createElement('div');
    box.className = 'jfnb-hint';
    box.innerHTML = '<span>로그인하면 아직 <strong>안 본 브리핑</strong>을 표시해드립니다.</span>';
    var go = document.createElement('button');
    go.type = 'button'; go.className = 'jfnb-hint-go'; go.textContent = '로그인';
    go.addEventListener('click', doLogin);
    var x = document.createElement('button');
    x.type = 'button'; x.className = 'jfnb-hint-x'; x.textContent = '✕';
    x.setAttribute('aria-label', '닫기');
    x.addEventListener('click', function () {
      try { localStorage.setItem(HINT_KEY, '1'); } catch (e) {}
      box.remove();
    });
    box.appendChild(go); box.appendChild(x);
    host.parentNode.insertBefore(box, host);
  }

  /* ══════════════ 카드 액션 바 ══════════════ */

  function buildBar(card, saved) {
    var bar = document.createElement('div');
    bar.className = 'jfnb-actions';

    var bm = document.createElement('button');
    bm.type = 'button';
    bm.className = 'jfnb-btn jfnb-bm';
    bm.setAttribute('aria-label', '이 기사 보관');
    bm.dataset.key = keyOf(card);
    setBmState(bm, indexOfKey(saved, bm.dataset.key) !== -1);

    var cp = document.createElement('button');
    cp.type = 'button';
    cp.className = 'jfnb-btn jfnb-cp';
    cp.setAttribute('aria-label', '요약 복사');
    cp.textContent = '📋';

    bar.appendChild(bm);
    bar.appendChild(cp);
    return bar;
  }

  function setBmState(btn, on) {
    btn.textContent = on ? '🔖' : '🏷️';
    btn.classList.toggle('on', on);
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    btn.title = on ? '보관함에서 빼기' : '보관함에 담기';
  }

  // 클라우드 병합 후 버튼 상태를 다시 칠한다
  function refreshBookmarkButtons() {
    var list = load();
    var btns = document.querySelectorAll('.jfnb-bm');
    Array.prototype.forEach.call(btns, function (b) {
      setBmState(b, indexOfKey(list, b.dataset.key) !== -1);
    });
  }

  function copyPayload(card) {
    var isCluster = card.getAttribute('data-card-type') === 'cluster';
    var label = isCluster ? '주간 브리핑' : '외신 브리핑';
    var date = (document.querySelector('.date-badge') || {}).textContent || stem();
    var url = card.getAttribute('data-card-url');
    var perma = location.origin + location.pathname + '#' + card.id;
    var body = summaryOf(card);
    if (body.length > 400) body = body.slice(0, 400) + '…';
    return '[' + label + ' ' + String(date).trim() + '] ' + displayTitle(card) + '\n'
         + (body ? body + '\n' : '')
         + (url ? '원문: ' + url : perma);
  }

  /* ══════════════ 딥링크 · 하이라이트 ══════════════ */

  function focusCard(card) {
    var navEl = document.querySelector('nav.reader-nav');
    var offset = navEl ? navEl.getBoundingClientRect().height + 12 : 0;
    var y = card.getBoundingClientRect().top + window.pageYOffset - offset;
    window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' });
    card.classList.add('jfnb-focus');
    setTimeout(function () { card.classList.remove('jfnb-focus'); }, 1600);
  }

  // 텍스트 노드만 순회한다. innerHTML 치환은 카드 안의 원문 링크를 깨뜨린다.
  function markQuery(root, q) {
    if (!q || q.length < 2) return;
    var needle = q.toLowerCase();
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        var p = node.parentNode;
        while (p && p !== root) {
          var n = p.nodeName;
          if (n === 'A' || n === 'SCRIPT' || n === 'STYLE' || n === 'MARK' || n === 'BUTTON') {
            return NodeFilter.FILTER_REJECT;
          }
          p = p.parentNode;
        }
        return node.nodeValue.toLowerCase().indexOf(needle) !== -1
          ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    });
    var targets = [], n;
    while ((n = walker.nextNode())) targets.push(n);

    targets.forEach(function (node) {
      var text = node.nodeValue, frag = document.createDocumentFragment(), i = 0;
      var low = text.toLowerCase(), pos;
      while ((pos = low.indexOf(needle, i)) !== -1) {
        if (pos > i) frag.appendChild(document.createTextNode(text.slice(i, pos)));
        var m = document.createElement('mark');
        m.className = 'jfnb-mark';
        m.textContent = text.slice(pos, pos + q.length);
        frag.appendChild(m);
        i = pos + q.length;
      }
      if (i < text.length) frag.appendChild(document.createTextNode(text.slice(i)));
      node.parentNode.replaceChild(frag, node);
    });
  }

  function paintCount(n) {
    var els = document.querySelectorAll('[data-jfnb-count]');
    Array.prototype.forEach.call(els, function (el) {
      el.textContent = n ? '(' + n + ')' : '';
    });
  }

  /* ══════════════ 부팅 ══════════════ */

  function init() {
    var cards = document.querySelectorAll('.jfnb-card');

    /* 카드가 있는 페이지 — 액션 바 주입 */
    if (cards.length) {
      var saved = load();
      Array.prototype.forEach.call(cards, function (card) {
        if (card.querySelector(':scope > .jfnb-actions')) return;  // 멱등
        card.classList.add('jfnb-card-host');
        card.insertBefore(buildBar(card, saved), card.firstChild);
      });
    }

    // 이벤트 위임 — 카드마다 리스너를 달지 않는다
    document.addEventListener('click', function (ev) {
      var btn = ev.target.closest && ev.target.closest('.jfnb-btn');
      if (!btn) return;
      var card = btn.closest('.jfnb-card');
      if (!card) return;
      ev.preventDefault();

      if (btn.classList.contains('jfnb-cp')) {
        copyText(copyPayload(card));
        return;
      }

      var list = load();
      var k = keyOf(card);
      var at = indexOfKey(list, k);
      if (at !== -1) {
        list.splice(at, 1);
        setBmState(btn, false);
        toast('보관함에서 뺐습니다');
      } else {
        list.unshift({
          k:  k,
          d:  stem(),
          a:  card.id,
          t:  displayTitle(card).slice(0, 200),
          ty: card.getAttribute('data-card-type') || 'article',
          ts: Date.now()
        });
        setBmState(btn, true);
        toast(save(list) === false ? '저장 공간이 가득 찼습니다' : '보관함에 담았습니다');
      }
      save(list);
      paintCount(list.length);
      pushBookmarks();                 // 로그인 상태면 디바운스 후 서버 반영
    });

    paintCount(load().length);

    /* 딥링크 + 검색어 마킹 */
    if (cards.length) {
      var q = new URLSearchParams(location.search).get('q');
      if (q) Array.prototype.forEach.call(cards, function (c) { markQuery(c, q); });

      var hash = location.hash.replace('#', '');
      if (hash && /^art-\d+$/.test(hash)) {
        var target = document.getElementById(hash);
        if (target) setTimeout(function () { focusCard(target); }, 120);
      }
      window.addEventListener('hashchange', function () {
        var h = location.hash.replace('#', '');
        var t = h && document.getElementById(h);
        if (t && t.classList.contains('jfnb-card')) focusCard(t);
      });
    }

    /* 로그인 층 — 비로그인 사용자는 여기서 아무 요청도 하지 않는다 */
    renderAuthUI();
    renderHint();
    observeList();

    var mark = null;
    try { mark = localStorage.getItem(AUTH_MARK); } catch (e) {}
    if (mark === '1') initFirebase().catch(function () {});
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
