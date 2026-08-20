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
 * 🔴 로그인 경로가 기기에 따라 둘로 나뉜다. 하나로 합치려 하지 말 것.
 *
 *    데스크톱 = signInWithPopup.
 *      signInWithRedirect로 바꾸지 말 것. authDomain이 앱 도메인과 달라
 *      교차 출처 iframe에 의존하는데 Chrome 115+ / Firefox 109+ / Safari 16.1+ 가
 *      서드파티 저장소를 차단한다. Firebase 공식 문서도 그 문제의 해법으로 popup을 든다.
 *
 *    모바일 = Google Identity Services + signInWithCredential.
 *      모바일 크롬은 OAuth 창을 별도 탭으로 열고, 그 사이 원래 탭을 폐기할 수 있다.
 *      돌아오면 페이지가 다시 로드돼 signInWithPopup의 프로미스가 사라진다.
 *      성공도 실패도 전달될 곳이 없어 '에러조차 안 뜨는' 무한 루프가 된다(2026-08-18 실측).
 *      GIS는 같은 페이지 안에서 ID 토큰을 콜백으로 돌려주므로 이 문제가 없다.
 *      GIS_CLIENT_ID가 비어 있으면 모바일도 팝업으로 폴백한다.
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

  /* 🟡 OAuth 웹 클라이언트 ID — 모바일 로그인에 필요하다. 비워두면 모바일도
   *    기존 팝업 방식을 그대로 쓴다(=지금과 동일, 회귀 없음).
   *    Firebase 콘솔 → Authentication → Sign-in method → Google
   *      → '웹 SDK 구성' 펼치기 → 웹 클라이언트 ID
   *    형식: 1044512119500-xxxxxxxx.apps.googleusercontent.com
   *    공개돼도 되는 값이다. 페이지 소스에 그대로 실린다. */
  var GIS_CLIENT_ID = '1044512119500-m0sodv559tcho75csl8atavo23kmpfd4.apps.googleusercontent.com';

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

  /* 요약 추출 —— 셀렉터 목록(`a, b, c`)은 우선순위가 아니라 문서 순으로 매칭된다.
   * 예전 코드 `querySelector('.article-summary, .summary, p.status, p')`는
   * 바로 이 이유로 p.article-title-kr(한글 제목)을 먼저 집어 요약을 통째로 잃었다.
   * 코퍼스 4,420장 실측으로 뽑은 순서다. 반드시 한 개씩 순서대로 시도할 것. */
  var SUM_SELS = [
    '.article-summary',                                  // 일간 현행 (3,965장)
    '.cluster-story', '.cluster-summary', '.story-summary',
    '.standalone-desc', '.pick-body', '.pick-rationale',  // 주간
    '.article-content', '.article-desc', '.article-subtitle',
    '.summary', '.desc', '.why',
    '.status', '.current-status', '.story-context', '.insight',
    '.pick-reason'                                       // PICK 카드는 이게 본문이다
  ];
  // 폴백에서 건너뛸 클래스 — 제목·메타·배지·타임라인 부속
  var SUM_DENY = /(^|[-_ ])(title|ttl|headline|meta|badge|badges|source|date|time|score|rank|chip|tag|tags|timeline|tl|num|lab|day|momentum|vs|header|head|footer|jfnb|actions|key-point)([-_ ]|$)/i;
  var BLOCK_SEL = 'p, div, ul, ol, li, h1, h2, h3, h4, table, section, article';

  function clean(el) {
    return el ? el.textContent.replace(/\s+/g, ' ').trim() : '';
  }

  function summaryOf(card) {
    var i, j, els, t;

    for (i = 0; i < SUM_SELS.length; i++) {
      els = card.querySelectorAll(SUM_SELS[i]);
      for (j = 0; j < els.length; j++) {
        t = clean(els[j]);
        if (t) return t;
      }
    }

    // 폴백 1 — 이름 없는 본문 단락 (2025-12 초기판 141장)
    var title = card.getAttribute('data-card-title') || '';
    var cand = card.querySelectorAll('p, div');
    for (i = 0; i < cand.length; i++) {
      var el = cand[i];
      var cls = el.className;
      if (typeof cls !== 'string') cls = '';        // SVG 등은 className이 객체다
      if (cls && SUM_DENY.test(cls)) continue;
      if (el.querySelector(BLOCK_SEL)) continue;    // 컨테이너는 건너뛴다
      t = clean(el);
      if (t.length >= 25 && t !== title) return t;
    }

    // 폴백 2 — 요약이 아예 없는 초기 주간 클러스터(24장). 타임라인이 본문 역할을 한다.
    var tl = card.querySelectorAll('.timeline-item, .tl-item, .timeline li');
    if (tl.length) {
      var parts = [];
      for (i = 0; i < tl.length; i++) {
        t = clean(tl[i]);
        if (t) parts.push(t);
      }
      if (parts.length) return parts.join(' · ');
    }

    return '';
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
  var authReady = false;    // onAuthStateChanged가 한 번이라도 돌았는가
  var pendingSave = null;   // 로그인 유도로 보류된 보관 요청 { id }
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

  /* 로그인 실패 원인을 삼키지 말 것.
   * 이전 버전은 popup-closed-by-user를 조용히 무시했는데, 모바일에서 팝업 결과가
   * 돌아오지 못할 때 SDK가 던지는 코드가 바로 그것이다. 사용자 눈에는
   * "눌렀는데 아무 일도 안 일어남"으로 보이고, 우리는 원인을 알 수 없게 된다. */
  var LOGIN_MSG = {
    'auth/popup-closed-by-user':
      '로그인 창이 결과를 전달하지 못했습니다. 모바일에서 자주 발생합니다',
    'auth/popup-blocked':
      '브라우저가 로그인 창을 차단했습니다. 팝업 허용 후 다시 시도해주세요',
    'auth/cancelled-popup-request': null,          // 사용자가 연속 클릭한 경우 — 무시
    'auth/unauthorized-domain':
      '이 도메인이 Firebase 승인 목록에 없습니다',
    'auth/operation-not-supported-in-this-environment':
      '이 브라우저(앱 내 브라우저 등)에서는 로그인할 수 없습니다',
    'auth/network-request-failed':
      '네트워크 오류로 로그인하지 못했습니다'
  };

  function loginFailed(e) {
    var code = (e && e.code) || 'unknown';
    console.warn('[jfnb] 로그인 실패', code, e);
    if (LOGIN_MSG[code] === null) return;                 // 조용히 넘길 것만 명시적으로
    var msg = LOGIN_MSG[code] || '로그인에 실패했습니다';
    toast(msg + ' (' + code + ')');                       // 코드를 노출해야 원인을 좁힐 수 있다
  }

  /* 사용자 제스처 만료 대비 — 버튼을 '누르기 전에' SDK를 미리 받아둔다.
   * click 핸들러에서 SDK를 받고 나서 signInWithPopup을 부르면, 그 사이 수백 ms 동안
   * 브라우저가 부여한 사용자 제스처 자격이 만료된다. 데스크톱은 관대하지만
   * 모바일은 엄격해서 팝업이 opener를 잃은 채 열릴 수 있다.
   * pointerdown은 click보다 먼저 발생하므로 그만큼 시간을 번다. */
  function warmAuth() {
    initFirebase().catch(function () {});
  }

  function armWarmup(el) {
    if (!el) return el;
    el.addEventListener('pointerdown', warmAuth, { once: true, passive: true });
    el.addEventListener('touchstart', warmAuth, { once: true, passive: true });
    el.addEventListener('mouseenter', warmAuth, { once: true, passive: true });
    return el;
  }

  function popupLogin() {
    initFirebase().then(function (f) {
      var provider = new f.A.GoogleAuthProvider();
      // 기기에 계정이 하나뿐이고 이미 동의한 상태면 구글이 선택 화면을 건너뛴다.
      // 공용 기기에서 남의 계정으로 조용히 들어가는 상황을 막는다(결정 #9와 같은 취지).
      provider.setCustomParameters({ prompt: 'select_account' });
      try { f.A.useDeviceLanguage(f.auth); } catch (e) {}   // 동의 화면 한국어

      // 🔴 signInWithPopup 고정. signInWithRedirect는 authDomain이 앱 도메인과 달라
      //    서드파티 저장소 차단에 걸린다 (파일 상단 주석 참조).
      return f.A.signInWithPopup(f.auth, provider);
    }).catch(loginFailed);
  }

  // 데스크톱은 검증된 팝업 경로를 유지한다. 모바일만 GIS로 우회한다.
  function doLogin() {
    if (useGis()) gisLogin();
    else popupLogin();
  }

  function doLogout() {
    /* GIS는 한 번 고른 계정을 기억해 다음 로그인에서 선택 단계를 건너뛴다.
     * 로그아웃했다는 건 다른 사람이 쓸 수도 있다는 뜻이므로 그 기억을 지운다.
     * (prompt:'select_account'는 팝업 경로에만 먹는다 — GIS 쪽은 이 호출이 담당) */
    try {
      if (window.google && window.google.accounts && window.google.accounts.id) {
        window.google.accounts.id.disableAutoSelect();
      }
    } catch (e) {}
    if (!fb) return;
    fb.A.signOut(fb.auth).catch(function () {});
  }

  function onAuthChanged(u) {
    user = u || null;
    authReady = true;
    if (user) {
      try { localStorage.setItem(AUTH_MARK, '1'); } catch (e) {}
      closeLoginAsk();
      flushPendingSave();      // pullCloud보다 먼저 — 병합에 함께 실려 올라간다
      upsertProfile();
      pullCloud();
    } else {
      // 보류된 담기가 있는데 세션 복원에 실패했다면 그때 로그인 창을 띄운다
      if (pendingSave) askLogin();
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
        armWarmup(b);
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
    box.innerHTML = '<span>로그인하면 아직 <strong>안 본 브리핑</strong>이 표시되고, '
                  + '<strong>보관함</strong>이 기기 간에 동기화됩니다.</span>';
    var go = document.createElement('button');
    go.type = 'button'; go.className = 'jfnb-hint-go'; go.textContent = '로그인';
    go.addEventListener('click', doLogin);
    armWarmup(go);
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

    // 📖 상세 해설 — 해설 파일이 있는 카드에서만 나중에 드러난다 (revealDeep)
    if (card.getAttribute('data-card-url')) {
      var dp = document.createElement('button');
      dp.type = 'button';
      dp.className = 'jfnb-btn jfnb-dp';
      dp.setAttribute('aria-label', '상세 해설 보기');
      dp.setAttribute('aria-expanded', 'false');
      dp.title = '상세 해설';
      dp.textContent = '📖';
      dp.hidden = true;
      bar.appendChild(dp);
    }
    return bar;
  }

  /* ══════════════ 상세 해설 (deep/{날짜}.json) ══════════════
   * 발행 직후 별도 워크플로가 만들어 둔 해설을 펼친다.
   * 파일이 없는 날짜에서는 버튼 자체를 그리지 않는다 — 눌러도 안 되는 버튼은
   * 기능이 고장 난 것처럼 보인다. 그래서 로드 시 한 번만 확인하고 드러낸다. */

  var DEEP_CSS = [
    '.jfnb-deep{margin:14px 0 2px;padding:16px 18px;border-radius:12px;',
    'background:rgba(102,126,234,.07);border:1px solid rgba(102,126,234,.22);',
    'font-size:.92rem;line-height:1.85;color:#c8cee2}',
    '.jfnb-deep p{margin:0 0 13px}',
    '.jfnb-deep p:last-child{margin-bottom:0}',
    '.jfnb-deep strong{color:#fff;font-weight:600}',
    '.jfnb-deep-h{display:flex;align-items:center;gap:8px;margin:0 0 12px;',
    'font-size:.74rem;letter-spacing:.04em;color:#8fa6ff;font-weight:600}',
    '.jfnb-deep-h::after{content:"";flex:1;height:1px;background:rgba(102,126,234,.22)}',
    '@media(max-width:480px){.jfnb-deep{padding:14px;font-size:.88rem}}'
  ].join('');

  var deepMap = null;          // { url: {deep, by, n} } — 없으면 null
  var deepTried = false;

  function deepUrl() {
    return '../deep/' + encodeURIComponent(stem()) + '.json';
  }

  function loadDeep() {
    if (deepTried) return Promise.resolve(deepMap);
    deepTried = true;
    return fetch(deepUrl(), { cache: 'default' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) {
        deepMap = (j && j.items) || null;
        return deepMap;
      })
      .catch(function () { return null; });
  }

  // 해설이 있는 카드의 📖만 드러낸다
  function revealDeep() {
    if (!deepMap) return;
    var btns = document.querySelectorAll('.jfnb-dp');
    Array.prototype.forEach.call(btns, function (b) {
      var card = b.closest('.jfnb-card');
      var u = card && card.getAttribute('data-card-url');
      if (u && deepMap[u]) b.hidden = false;
    });
  }

  // **굵게** 만 처리한다. innerHTML에 원문을 그대로 넣지 않기 위해 직접 조립한다.
  function renderDeep(text) {
    var wrap = document.createElement('div');
    wrap.className = 'jfnb-deep';

    var h = document.createElement('div');
    h.className = 'jfnb-deep-h';
    h.textContent = '📖 상세 해설';
    wrap.appendChild(h);

    text.split(/\n{2,}/).forEach(function (para) {
      if (!para.trim()) return;
      var p = document.createElement('p');
      para.split(/\*\*/).forEach(function (chunk, i) {
        if (!chunk) return;
        if (i % 2 === 1) {
          var s = document.createElement('strong');
          s.textContent = chunk;
          p.appendChild(s);
        } else {
          p.appendChild(document.createTextNode(chunk));
        }
      });
      wrap.appendChild(p);
    });
    return wrap;
  }

  function toggleDeep(card, btn) {
    var open = card.querySelector(':scope > .jfnb-deep');
    if (open) {
      open.remove();
      btn.setAttribute('aria-expanded', 'false');
      btn.classList.remove('on');
      return;
    }
    var url = card.getAttribute('data-card-url');
    var it = deepMap && url && deepMap[url];
    if (!it || !it.deep) {
      toast('이 기사는 상세 해설이 없습니다');
      return;
    }
    if (!document.getElementById('jfnb-deep-css')) {
      var st = document.createElement('style');
      st.id = 'jfnb-deep-css';
      st.textContent = DEEP_CSS;
      document.head.appendChild(st);
    }
    card.appendChild(renderDeep(it.deep));
    btn.setAttribute('aria-expanded', 'true');
    btn.classList.add('on');
  }

  function setBmState(btn, on) {
    btn.textContent = on ? '🔖' : '🏷️';
    btn.classList.toggle('on', on);
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    btn.title = on ? '보관함에서 빼기' : '보관함에 담기';
  }

  /* ══════════════ 로그인 요구 (보관 버튼) ══════════════
   * 보관함은 기기 간 동기화가 본질이라 로그인이 전제다.
   * 비로그인 상태에서 담으면 로컬에만 쌓였다가 로그인 시점에 사라진 것처럼 보인다
   * (로그아웃/최초 로그인 때 로컬 캐시를 비우기 때문 — 결정 #9).
   * 그래서 담기 전에 막고 로그인을 먼저 요구한다. */

  var askBox = null;

  /* 스타일은 theme-modern.css가 아니라 여기서 주입한다.
   * saved.html·search.html·about.html과 아카이브 2개 파일이 그 CSS를 안 물고 있어,
   * 시트에 넣으면 그 페이지들에서 다이얼로그가 무스타일로 뜬다. */
  var ASK_CSS = [
    '.jfnb-ask{position:fixed;inset:0;background:rgba(8,8,14,.68);',
    '-webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px);',
    'display:flex;align-items:center;justify-content:center;padding:20px;z-index:10000}',
    '.jfnb-ask-box{width:100%;max-width:380px;background:#15151f;',
    'border:1px solid rgba(255,255,255,.12);border-radius:16px;padding:24px 22px 18px;',
    'box-shadow:0 24px 60px rgba(0,0,0,.55);',
    'font-family:"Noto Sans KR",-apple-system,BlinkMacSystemFont,sans-serif;line-height:1.7}',
    '.jfnb-ask-t{margin:0 0 10px;font-size:1.02rem;font-weight:700;color:#fff;line-height:1.4}',
    '.jfnb-ask-d{margin:0 0 20px;font-size:.86rem;line-height:1.6;color:#a9b1c9}',
    '.jfnb-ask-row{display:flex;gap:8px;justify-content:flex-end}',
    '.jfnb-ask-go,.jfnb-ask-no{border:0;border-radius:9px;padding:9px 18px;',
    'font:inherit;font-size:.87rem;cursor:pointer}',
    '.jfnb-ask-go{background:linear-gradient(135deg,#667eea,#a855f7);color:#fff;font-weight:600}',
    '.jfnb-ask-go:hover{filter:brightness(1.12)}',
    '.jfnb-ask-no{background:rgba(255,255,255,.06);color:#9aa2ba;',
    'border:1px solid rgba(255,255,255,.1)}',
    '.jfnb-ask-no:hover{color:#fff;background:rgba(255,255,255,.1)}',
    '.jfnb-ask-go:focus-visible,.jfnb-ask-no:focus-visible{outline:2px solid #8fa6ff;outline-offset:2px}',
    '@media(max-width:480px){.jfnb-ask-box{padding:20px 18px 16px}',
    '.jfnb-ask-row{flex-direction:column-reverse}',
    '.jfnb-ask-go,.jfnb-ask-no{width:100%;padding:12px}}'
  ].join('');

  function ensureAskCss() {
    if (document.getElementById('jfnb-ask-css')) return;
    var s = document.createElement('style');
    s.id = 'jfnb-ask-css';
    s.textContent = ASK_CSS;
    document.head.appendChild(s);
  }

  /* ══════════════ 모바일 로그인 — Google Identity Services ══════════════
   *
   * 왜 팝업으로는 안 되는가 (2026-08-18 실측)
   *   모바일 크롬은 OAuth 창을 별도 탭으로 연다. 그동안 원래 탭이 백그라운드로
   *   밀리고 메모리 압박을 받으면 폐기된다. 돌아오면 페이지가 처음부터 다시 로드된다.
   *   → signInWithPopup이 반환한 프로미스가 페이지와 함께 사라진다.
   *     성공도 실패도 전달될 곳이 없어 '에러조차 안 뜨는' 상태가 된다.
   *     새로고침해도 로그인되지 않는 것으로 결과 전달 자체가 끊겼음을 확인했다.
   *   → 타이밍 조정으로는 못 넘는다. 창을 넘나들지 않는 방식이 필요하다.
   *
   * GIS는 같은 페이지 안에서 ID 토큰을 콜백으로 돌려준다. 창 간 결과 전달이
   * 없으므로 탭이 폐기될 여지도 없다. 받은 토큰을 signInWithCredential로 넘긴다.
   * (Firebase 공식 문서가 정적 호스팅 환경에 제시하는 경로)
   */

  var gisPromise = null;

  function isTouchDevice() {
    try {
      if (window.matchMedia && window.matchMedia('(pointer: coarse)').matches) return true;
    } catch (e) {}
    return /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent || '');
  }

  function useGis() {
    return !!GIS_CLIENT_ID && isTouchDevice();
  }

  function loadGis() {
    if (gisPromise) return gisPromise;
    gisPromise = new Promise(function (res, rej) {
      if (window.google && window.google.accounts && window.google.accounts.id) return res();
      var sc = document.createElement('script');
      sc.src = 'https://accounts.google.com/gsi/client';
      sc.async = true;
      sc.defer = true;
      sc.onload = function () {
        if (window.google && window.google.accounts && window.google.accounts.id) res();
        else rej(new Error('gis-missing'));
      };
      sc.onerror = function () { rej(new Error('gis-load-failed')); };
      document.head.appendChild(sc);
    }).catch(function (e) {
      gisPromise = null;                 // 다음 시도를 막지 않는다
      throw e;
    });
    return gisPromise;
  }

  // 구글이 돌려준 ID 토큰 → Firebase 세션
  function onGisCredential(resp) {
    var idToken = resp && resp.credential;
    if (!idToken) { toast('로그인 정보를 받지 못했습니다'); return; }
    initFirebase().then(function (f) {
      var cred = f.A.GoogleAuthProvider.credential(idToken);
      return f.A.signInWithCredential(f.auth, cred);
    }).then(function () {
      closeLoginAsk();                   // onAuthChanged가 먼저 닫지만 이중 안전
    }).catch(loginFailed);
  }

  function gisLogin() {
    loadGis().then(function () {
      window.google.accounts.id.initialize({
        client_id: GIS_CLIENT_ID,
        callback: onGisCredential,
        auto_select: false,
        cancel_on_tap_outside: true,
        use_fedcm_for_prompt: true,
        itp_support: true
      });
      openGisDialog();
    }).catch(function (e) {
      console.warn('[jfnb] GIS 로드 실패 — 팝업으로 대체', e);
      popupLogin();                      // GIS를 못 받으면 기존 경로라도 시도한다
    });
  }

  /* 구글이 그려주는 버튼을 우리 다이얼로그 안에 넣는다.
   * One Tap(prompt)은 사용자가 이전에 닫았거나 쿨다운 중이면 조용히 안 뜬다.
   * 눌러서 확실히 뜨는 renderButton 쪽이 진입점으로 안전하다. */
  function openGisDialog() {
    closeLoginAsk();
    ensureAskCss();

    var ov = document.createElement('div');
    ov.className = 'jfnb-ask';
    ov.setAttribute('role', 'dialog');
    ov.setAttribute('aria-modal', 'true');
    ov.setAttribute('aria-label', '구글 로그인');

    var box = document.createElement('div');
    box.className = 'jfnb-ask-box';

    var h = document.createElement('p');
    h.className = 'jfnb-ask-t';
    h.textContent = '구글 계정으로 로그인';

    var d = document.createElement('p');
    d.className = 'jfnb-ask-d';
    d.textContent = '아래 버튼을 눌러주세요. 가입 절차는 없습니다.';

    var host = document.createElement('div');
    host.style.cssText = 'display:flex;justify-content:center;margin:4px 0 16px;min-height:44px';

    var row = document.createElement('div');
    row.className = 'jfnb-ask-row';
    var no = document.createElement('button');
    no.type = 'button';
    no.className = 'jfnb-ask-no';
    no.textContent = '닫기';
    no.addEventListener('click', function () { pendingSave = null; closeLoginAsk(); });
    row.appendChild(no);

    box.appendChild(h); box.appendChild(d); box.appendChild(host); box.appendChild(row);
    ov.appendChild(box);
    ov.addEventListener('click', function (ev) {
      if (ev.target === ov) { pendingSave = null; closeLoginAsk(); }
    });
    document.body.appendChild(ov);
    askBox = ov;
    document.addEventListener('keydown', onAskKey);

    try {
      window.google.accounts.id.renderButton(host, {
        theme: 'filled_blue', size: 'large', shape: 'pill',
        text: 'signin_with', locale: 'ko', width: 240
      });
    } catch (e) {
      console.warn('[jfnb] GIS 버튼 렌더 실패', e);
      host.remove();
      closeLoginAsk();
      popupLogin();
    }
  }

  function closeLoginAsk() {
    if (!askBox) return;
    askBox.remove();
    askBox = null;
    document.removeEventListener('keydown', onAskKey);
  }

  function onAskKey(ev) {
    if (ev.key === 'Escape') { pendingSave = null; closeLoginAsk(); }
  }

  function askLogin() {
    closeLoginAsk();
    ensureAskCss();

    var ov = document.createElement('div');
    ov.className = 'jfnb-ask';
    ov.setAttribute('role', 'dialog');
    ov.setAttribute('aria-modal', 'true');
    ov.setAttribute('aria-label', '로그인 필요');

    var box = document.createElement('div');
    box.className = 'jfnb-ask-box';

    var h = document.createElement('p');
    h.className = 'jfnb-ask-t';
    h.textContent = '🔖 보관하려면 로그인이 필요합니다';

    var p = document.createElement('p');
    p.className = 'jfnb-ask-d';
    p.textContent = '보관함은 구글 계정에 저장돼 휴대폰·PC 어디서든 같은 목록을 봅니다. 가입 절차는 없습니다.';

    var row = document.createElement('div');
    row.className = 'jfnb-ask-row';

    var go = document.createElement('button');
    go.type = 'button';
    go.className = 'jfnb-ask-go';
    go.textContent = '구글로 로그인';
    go.addEventListener('click', function () { doLogin(); });
    armWarmup(go);

    var no = document.createElement('button');
    no.type = 'button';
    no.className = 'jfnb-ask-no';
    no.textContent = '나중에';
    no.addEventListener('click', function () { pendingSave = null; closeLoginAsk(); });

    row.appendChild(no);
    row.appendChild(go);
    box.appendChild(h); box.appendChild(p); box.appendChild(row);
    ov.appendChild(box);

    ov.addEventListener('click', function (ev) {
      if (ev.target === ov) { pendingSave = null; closeLoginAsk(); }
    });

    document.body.appendChild(ov);
    askBox = ov;
    document.addEventListener('keydown', onAskKey);
    setTimeout(function () { go.focus(); }, 20);
  }

  // 로그인 직후, 보류돼 있던 카드를 그대로 담아준다 (한 번 더 누르게 하지 않는다)
  function flushPendingSave() {
    if (!pendingSave) return;
    var card = document.getElementById(pendingSave.id);
    pendingSave = null;
    if (!card) return;
    var btn = card.querySelector('.jfnb-bm');
    if (!btn) return;
    if (indexOfKey(load(), keyOf(card)) !== -1) { setBmState(btn, true); return; }
    toggleBookmark(card, btn);
  }

  function toggleBookmark(card, btn) {
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
    var badge = document.querySelector('.date-badge');
    var date = (badge && badge.textContent.trim())
      ? badge.textContent.replace(/\s+/g, ' ').trim()
      : (stem().match(/\d{4}-\d{2}-\d{2}$/) || [stem()])[0];   // weekly- 접두사를 떼어낸다
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

      if (btn.classList.contains('jfnb-dp')) {
        toggleDeep(card, btn);           // 로그인 불필요 — 읽기 기능이다
        return;
      }

      /* 보관 — 로그인 게이트 */
      if (!user) {
        var mark = null;
        try { mark = localStorage.getItem(AUTH_MARK); } catch (e) {}
        if (mark === '1' && !authReady) {
          // 로그인한 적 있는 기기. SDK가 아직 세션을 복원하는 중이다
          pendingSave = { id: card.id };
          initFirebase().catch(function () { pendingSave = null; askLogin(); });
          toast('로그인 확인 중입니다…');
          return;
        }
        pendingSave = { id: card.id };
        askLogin();
        return;
      }

      toggleBookmark(card, btn);
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

      // 상세 해설 — 파일이 있는 날짜에서만 📖가 드러난다
      loadDeep().then(revealDeep);
    }

    /* 로그인 층 — 비로그인 사용자는 여기서 아무 요청도 하지 않는다 */
    renderAuthUI();
    renderHint();
    observeList();

    var mark = null;
    try { mark = localStorage.getItem(AUTH_MARK); } catch (e) {}
    if (mark === '1') initFirebase().catch(function () {});
  }

  // saved.html 등 개별 페이지에서 로그인 버튼을 붙일 수 있게 최소한만 노출한다
  window.JFNB = {
    login: doLogin,
    logout: doLogout,
    isAuthed: function () { return !!user; },
    askCss: ensureAskCss           // .jfnb-ask-go 버튼을 직접 쓰는 페이지용
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
