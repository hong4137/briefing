/*!
 * JFNB 공통 스크립트 — 기사 카드 북마크 · 딥링크 · 하이라이트 · 복사
 *
 * post_process.py가 아카이브 HTML head에 <script src="../app.js?v=N" defer>로 주입한다.
 * 카드 탐지는 빌드 타임에 끝나 있다 — 이 파일은 .jfnb-card 와 data-* 속성만 읽는다.
 * (아카이브에 마크업이 6세대 섞여 있지만 여기서는 알 필요가 없다.)
 */
(function () {
  'use strict';

  var KEY = 'jfnb-saved-articles';
  var MAX = 200;   // hong4137.github.io는 다른 Pages 프로젝트와 5MB 한도를 공유한다

  /* ---------- 저장소 ---------- */

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
      // 용량 초과 — 오래된 절반을 버리고 한 번만 재시도한다
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

  /* ---------- 유틸 ---------- */

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

  /* ---------- 액션 바 ---------- */

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

  /* ---------- 하이라이트 ---------- */

  function focusCard(card) {
    var navEl = document.querySelector('nav.reader-nav');
    var offset = navEl ? navEl.getBoundingClientRect().height + 12 : 0;
    var y = card.getBoundingClientRect().top + window.pageYOffset - offset;
    window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' });
    card.classList.add('jfnb-focus');
    setTimeout(function () { card.classList.remove('jfnb-focus'); }, 1600);
  }

  // 텍스트 노드만 순회한다. innerHTML 치환은 카드 안의 원문 링크를 깨뜨릴 수 있다.
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

  /* ---------- 부팅 ---------- */

  function init() {
    var cards = document.querySelectorAll('.jfnb-card');
    if (!cards.length) return;

    var saved = load();

    Array.prototype.forEach.call(cards, function (card) {
      if (card.querySelector(':scope > .jfnb-actions')) return;  // 멱등
      card.classList.add('jfnb-card-host');
      card.insertBefore(buildBar(card, saved), card.firstChild);
    });

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
    });

    paintCount(saved.length);

    // 딥링크 + 검색어 마킹
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

  function paintCount(n) {
    var el = document.querySelector('[data-jfnb-count]');
    if (el) el.textContent = n ? '(' + n + ')' : '';
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
