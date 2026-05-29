import re
import json
import hashlib
from pathlib import Path
from bs4 import BeautifulSoup

ROOT_DIR       = Path(__file__).resolve().parent.parent
ARCHIVE_DIR    = ROOT_DIR / "archive"
BRIEFINGS_JSON = ROOT_DIR / "briefings.json"

BASE = "https://images.unsplash.com/photo-"

PARAMS_THUMB    = "?w=480&h=270&fit=crop&auto=format&q=75"
PARAMS_THUMB_XS = "?w=112&h=112&fit=crop&auto=format&q=70"

HERO_META_KEYS = (
    "hero_url",
    "hero_url_sm",
    "hero_alt",
    "hero_credit_name",
    "hero_credit_url",
    "hero_source",
)

CATEGORY_PATTERNS = [
    # 순서가 우선순위. 앞 카테고리가 먼저 매칭되면 이후 검사 안 함.
    ("ai",       r'AI|인공지능|LLM|ChatGPT|Gemini|Claude|Grok|딥러닝|머신러닝|GPT|오픈AI|OpenAI|Anthropic'),
    ("chip",     r'반도체|칩|HBM|TSMC|SK하이닉스|하이닉스|마이크론|Micron|NVIDIA|엔비디아|삼성전자|파운드리|웨이퍼'),
    ("finance",  r'주식|증시|S&P|나스닥|시총|IPO|상장|월가|투자|채권|금리|연준|Fed|주가|코스피|다우'),
    ("robot",    r'로봇|휴머노이드|Unitree|보스턴다이내믹스|Figure|Agility|자동화|드론'),
    ("space",    r'우주|SpaceX|스타링크|Starlink|위성|로켓|발사|NASA|스타십|Starship|ISS'),
    ("health",   r'헬스|의료|Fitbit|웨어러블|건강|바이오|임상|FDA|제약|스마트워치|애플워치'),
    ("ev",       r'전기차|배터리|자율주행|EV|테슬라|Tesla|리튬|양극재'),
    ("economy",  r'거시경제|무역|관세|수출|인플레이션|GDP|경기|환율|달러|무역전쟁|통상'),
    ("telecom",  r'통신망|5G|6G|통신사|광케이블|기지국|네트워크|라우터'),
    ("bigtech",  r'빅테크|마이크로소프트|구글|애플|메타|아마존|OS|iOS|안드로이드|Windows|GCP|AWS'),
    ("policy",   r'규제|반독점|소송|정부|청문회|법원|벌금|가이드라인|국회|안전성|안보'),
    ("defense",  r'방산|방위산업|미사일|무기|전투기|군사|국방|K-방산|드론전|화약|군인'),
]

def _img(photo_id, alt, credit_name):
    return {
        "id":          photo_id,
        "alt":         alt,
        "credit_name": credit_name,
        "credit_url":  f"https://unsplash.com/photos/{photo_id}",
    }

CATEGORY_IMAGE_MAP = {

    # ── 1. AI / 인공지능 ────────────────────────────────────────
    "ai": [
        _img("1677442135703-1787eea5ce01",
             "Blue neural network data visualization on dark background",
             "Growtika"),
        _img("1620712943543-bcc4688e7485",
             "Cybernetic virtual brain with glowing circuits",
             "Possessed Photography"),
        _img("1604079477490-fef21a76fb43",
             "Glowing network nodes interconnected web abstract",
             "Alina Grubnyak"),
        _img("1526374965328-7f61d4dc18c5",
             "Matrix green binary code wall on black screen",
             "Markus Spiske"),
        _img("1633356122102-4c8c5f9a2aa4",
             "Futuristic AI robot eye close-up neon",
             "Aideal Hwa"),
        _img("1712240931705-7c3bee0823f5",
             "Abstract artificial intelligence digital face",
             "Choong Deng Xiang"),
        _img("1558618666-fcd25c85cd64",
             "Dark neural network connection visualization",
             "Alina Grubnyak"),
        _img("1546776230-3b2a7aa2b0f0",
             "Blue digital brain neuron signal concept",
             "Fakurian Design"),
    ],

    # ── 2. 반도체 / 칩 ──────────────────────────────────────────
    "chip": [
        _img("1518770660439-4636190af475",
             "Gold pattern silicon microchip circuit board macro",
             "Alexandre Debiève"),
        _img("1607604276583-eef5d076aa5f",
             "Blue neon illuminated printed circuit motherboard",
             "Olivier Collet"),
        _img("1555664424-778a1e5e1b48",
             "Extreme macro close-up of circuit board traces",
             "Alex Andrews"),
        _img("1591453089816-0fbb971b454c",
             "Abstract semiconductor lattice grid graphic",
             "Laura Ockel"),
        _img("1641854961-9484f4e2c3c0",
             "Semiconductor wafer silicon close-up",
             "Laura Ockel"),
        _img("1563203369-26f2e7a5c1ca",
             "CPU chip processor extreme macro",
             "Christian Wiediger"),
        _img("1597852074816-d8c7a21a5b0a",
             "Silicon chip manufacturing blue light",
             "Lenny Kuhne"),
        _img("1574617024862-26570d3a3f57",
             "Green circuit board macro detail",
             "Alexandre Debiève"),
    ],

    # ── 3. 주식 / 금융 ──────────────────────────────────────────
    "finance": [
        _img("1611974789855-9c2a0a7236a3",
             "Neon candlestick stock market chart on dark monitor",
             "Maxim Hopman"),
        _img("1590283603385-17ffb3a7f29f",
             "Blue tone stock trading dashboard interface",
             "Konstantin Evdokimov"),
        _img("1642543492481-44e81e3914a7",
             "Financial data abstract 3D volume visualization",
             "Adam Nowakowski"),
        _img("1526304640581-d334cdbbf45e",
             "Digital currency and capital liquidity visual",
             "André François McKenzie"),
        _img("1560472354-b33ff0c44a43",
             "Stock market price ticker display",
             "Nicholas Cappello"),
        _img("1579532537598-459ecdaf39cc",
             "Financial trading charts dark theme",
             "Chris Liverani"),
        _img("1559526324-4b87b5e36e44",
             "Dark finance abstract digital currency",
             "André François McKenzie"),
        _img("1460925895917-afdab827c52f",
             "Economy data chart analysis dark",
             "M. B. M."),
    ],

    # ── 4. 로봇 / 휴머노이드 ────────────────────────────────────
    "robot": [
        _img("1485827404703-89b55fcc595e",
             "AI robot hand reaching digital interface",
             "Alex Knight"),
        _img("1589254065878-42c9da997008",
             "Minimalist humanoid robot upper body dark background",
             "Possessed Photography"),
        _img("1535378917042-10a22c95931a",
             "Robot under neon lighting looking forward",
             "Lenny Kuhne"),
        _img("1563770660941-20978e870e26",
             "Precise mechanical robot joint actuator close-up",
             "Ant Rozetsky"),
        _img("1507003211169-0a1dd7228f2d",
             "Robot manipulator arm factory automation",
             "Possessed Photography"),
        _img("1558470598-9e0ecc53f64e",
             "White humanoid robot dark studio",
             "Alex Knight"),
        _img("1531746790-e6595cb16e14",
             "AI robot metal body digital overlay",
             "Possessed Photography"),
        _img("1620712943543-bcc4688e7485",
             "Robotic arm precision mechanism close",
             "Possessed Photography"),
    ],

    # ── 5. 우주 / SpaceX ────────────────────────────────────────
    "space": [
        _img("1451187580459-43490279c0fa",
             "Blue Earth viewed from dark outer space orbit",
             "NASA"),
        _img("1506703719100-a0f3a48c0f86",
             "Majestic aurora borealis with deep space nebula",
             "Greg Rakozy"),
        _img("1446776811953-b23d57bd21aa",
             "Space station solar panels orbiting Earth",
             "NASA"),
        _img("1541185933-ef5d8ed016c2",
             "Rocket launch trajectory arc into night sky",
             "SpaceX"),
        _img("1484589065579-248aad0d8b13",
             "Rocket launch fire trail night",
             "NASA"),
        _img("1464802686167-b60a6688e7b1",
             "Milky way galaxy stars night sky",
             "Greg Rakozy"),
        _img("1608178398136-cd4b7d56ae7b",
             "Astronaut spacewalk earth background",
             "NASA"),
        _img("1531306728370-e2a126b8328e",
             "Deep space nebula colorful star field",
             "Jeremy Thomas"),
    ],

    # ── 6. 헬스케어 / 웨어러블 ──────────────────────────────────
    "health": [
        _img("1576091160399-112ba8d25d1d",
             "Glowing DNA helix structure graphic in dark lab",
             "National Cancer Institute"),
        _img("1530026405186-ed1ea0ac7a63",
             "Digital heartbeat ECG waveform sensor display",
             "National Cancer Institute"),
        _img("1505751172876-fa1923c5c528",
             "Smart wearable health monitoring loop screen",
             "Online Marketing"),
        _img("1579684389782-64d84b5e905d",
             "Bio cells under microscope biotech visualization",
             "National Cancer Institute"),
        _img("1583912267382-49c073ed35aa",
             "Medical tech brain scan dark room",
             "National Cancer Institute"),
        _img("1559757175-0eb30cd8c063",
             "Smart watch health sensor wrist",
             "Luke Chesser"),
        _img("1550751827-4bd374c3f58b",
             "Biotech lab blue light microscope",
             "Louis Reed"),
        _img("1628595351029-c2bf17511435",
             "DNA helix neon visualization blue",
             "National Cancer Institute"),
    ],

    # ── 7. 전기차 / EV ──────────────────────────────────────────
    "ev": [
        _img("1563720223185-11003d516935",
             "Autonomous vehicle headlight light trails tech art",
             "Jp Valery"),
        _img("1558441719-ff34b0524a24",
             "Futuristic electric vehicle charging port close-up",
             "Chuttersnap"),
        _img("1617788138017-80ad40651399",
             "Sleek EV body curves in dark studio lighting",
             "Juice Flair"),
        _img("1544716278-ca5e3f4abd8c",
             "LiDAR sensor autonomous driving line graphic",
             "Possessed Photography"),
        _img("1593941707882-a5bba14938c7",
             "Electric car charging cable night glow",
             "Chuttersnap"),
        _img("1620651788-3353e3d21f16",
             "Futuristic dashboard autonomous HUD",
             "Jp Valery"),
        _img("1581091226825-a6a2a5aee158",
             "Electric battery pack detail",
             "Roberto Sorin"),
        _img("1484100356142-db6ab6244067",
             "Highway autonomous car lidar beam",
             "Possessed Photography"),
    ],

    # ── 8. 거시경제 / 글로벌 무역 ───────────────────────────────
    "economy": [
        _img("1454165804606-c3d57bc86b40",
             "Dark theme global trade chart analysis screen",
             "Cytonn Photography"),
        _img("1526304640581-d334cdbbf45e",
             "Digital dollar financial liquidity visual",
             "André François McKenzie"),
        _img("1601597111158-2fceff292cdc",
             "Dark harbor container crane silhouette at dusk",
             "Channey"),
        _img("1586528116311-ad8dd3c8310d",
             "World map shipping route light graphic",
             "Thomas Lefebvre"),
        _img("1507679528-5d5ef73cf6b5",
             "Global container ship port supply chain",
             "Channey"),
        _img("1565373679579-0e22a33da54b",
             "World financial district skyscraper aerial",
             "Julien Moreau"),
        _img("1444653389962-9adb47052b4e",
             "Currency bills coins pile finance",
             "Andre Taissin"),
        _img("1460925895917-afdab827c52f",
             "Economy chart trend analysis dark",
             "M. B. M."),
    ],

    # ── 9. 통신 / 5G / 네트워크 ─────────────────────────────────
    "telecom": [
        _img("1544197150-b99a580bb7a8",
             "Dark blue fiber optic cables filling server rack",
             "Alina Grubnyak"),
        _img("1516321318423-f06f85e504b3",
             "Digital node hub connection network abstract art",
             "Alina Grubnyak"),
        _img("1600132806370-bf17e65e942f",
             "Tall cell tower antenna rising into night sky",
             "Thomas Kelley"),
        _img("1488590528505-98d2b5aba04b",
             "Neon data transmission flow visual dark background",
             "Umberto"),
        _img("1614064641-96cbef9f8c9f",
             "Server rack blue LED datacenter",
             "Taylor Vick"),
        _img("1586953208448-b04b81e45f94",
             "Fiber optic cable light macro",
             "Compare Fibre"),
        _img("1558494949-ef010cbdcc31",
             "5G tower antenna sky connection",
             "Thomas Kelley"),
        _img("1544197150-b99a580bb7a8",
             "Dark fiber optic server rack cables",
             "Alina Grubnyak"),
    ],

    # ── 10. 빅테크 / 플랫폼 ─────────────────────────────────────
    "bigtech": [
        _img("1618005182384-a83a8bd57fbe",
             "Abstract dark silk web browser art visual",
             "Growtika"),
        _img("1531297484001-80022131f5a1",
             "Premium laptop display Apple-style aesthetic",
             "Ales Nesetril"),
        _img("1562577309-4932fdd64cd1",
             "Data marketing multi-screen dashboard display",
             "Luke Chesser"),
        _img("1498050108023-c5249f4df085",
             "MacBook and smart devices overlay in dark room",
             "Christopher Gower"),
        _img("1516321497487-e288fb19713f",
             "Silicon valley tech campus modern",
             "Amos Bar-Zeev"),
        _img("1573804633927-bfcbcd909acd",
             "Dark laptop terminal developer coding",
             "Clément Hélardot"),
        _img("1519389950473-47ba0277781c",
             "Tech team collaborating laptops office",
             "Annie Spratt"),
        _img("1487058792275-0ad4aaf24ca7",
             "Colorful app icons smartphone screen",
             "Rami Al-zayat"),
    ],

    # ── 11. 정책 / 규제 / AI 안전 ───────────────────────────────
    "policy": [
        _img("1589829545856-d10d557cf95f",
             "Scales of justice in darkness law court symbol",
             "René DeAnda"),
        _img("1450133064473-71024230f91b",
             "Solemn marble columns and capitol building silhouette",
             "Louis Velazquez"),
        _img("1505664194779-8beaceb93744",
             "Old classic law books with leather cover close-up",
             "Tingey Injury Law Firm"),
        _img("1521791136364-7286472b6b5c",
             "Document signing with premium pen dark overlay",
             "Cytonn Photography"),
        _img("1555848962-6e79fc0c1a62",
             "Government capitol building cloudy sky",
             "Louis Velazquez"),
        _img("1507679522-7db8fc8c3e11",
             "Digital fingerprint biometric security",
             "George Prentzas"),
        _img("1604999565976-8913ad2ddb5c",
             "Legal document pen signing close-up",
             "Cytonn Photography"),
        _img("1529400971008-f566de0db5d5",
             "Privacy surveillance camera dark",
             "Matthew Henry"),
    ],

    # ── 12. 방산 / 군사 기술 ────────────────────────────────────
    "defense": [
        _img("1508873535684-277a3cbcc4e8",
             "Military helicopter silhouette in dark hangar",
             "David Henrichs"),
        _img("1473163928189-364b2c4e1135",
             "Radar grid scan line screen display",
             "Chris Henry"),
        _img("1506084868230-bb9d95c24759",
             "Aircraft vapor trails contrails in night sky",
             "Amir Kabirov"),
        _img("1569003339405-ea396a5a8a90",
             "Dark security zone restricted area fence",
             "Ehud Neuhaus"),
        _img("1473621038790-0f204fa15eef",
             "Military drone night infrared",
             "David Henrichs"),
        _img("1541802645-b8a4f37e12d1",
             "Radar sweep scan green dark",
             "Chris Henry"),
        _img("1586611292591-17f37862d040",
             "Fighter jet afterburner dark sky",
             "Amir Kabirov"),
        _img("1609743522653-52354461eb27",
             "Defense missile launch night trail",
             "Ehud Neuhaus"),
    ],
}

# ── 기본 풀 (카테고리 미매칭 시) ─────────────────────────────────
DEFAULT_IMAGE_POOL = [
    _img("1504711434969-e33886168f5c",
         "Aerial view of city lights glowing at night",
         "Maximalfocus"),
    _img("1451187580459-43490279c0fa",
         "Planet Earth viewed from space with city lights",
         "NASA"),
    _img("1498050108023-c5249f4df085",
         "Laptop displaying code in dark environment",
         "Christopher Gower"),
    _img("1522071820081-009f0129c71c",
         "Tech team collaborating on laptops in office",
         "Annie Spratt"),
]


def select_from_pool(pool: list, title: str, date_str: str = "") -> dict:
    """제목+날짜 해시 → 결정론적 이미지 선택 (§6-5)."""
    seed   = f"{title}_{date_str}".encode("utf-8")
    digest = hashlib.md5(seed).hexdigest()
    return pool[int(digest, 16) % len(pool)]


def detect_category(title: str, summary: str) -> str | None:
    """CATEGORY_PATTERNS 순서대로 첫 매칭 카테고리 반환."""
    text = title + " " + summary
    for category_key, pattern in CATEGORY_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return category_key
    return None


def parse_dimension(value) -> int | None:
    if value is None:
        return None
    match = re.search(r"\d+", str(value))
    return int(match.group(0)) if match else None


def find_article_image(soup: BeautifulSoup) -> dict | None:
    """Priority 1: 기사 본문 내 이미지 탐색."""
    BLOCKED = re.compile(r'icon|logo|badge|emoji|bullet|arrow|avatar', re.I)
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src or BLOCKED.search(src):
            continue
        w, h = parse_dimension(img.get("width")), parse_dimension(img.get("height"))
        if w is not None and w <= 200:
            continue
        if h is not None and h <= 100:
            continue
        img["data-promoted"] = "hero"
        return {"id": None, "alt": img.get("alt", ""),
                "credit_name": "", "credit_url": "", "src_override": src}
    return None


def make_urls(img_meta: dict) -> dict:
    """이미지 메타에서 모든 URL 크기 변형 생성."""
    if img_meta.get("src_override"):
        src = img_meta["src_override"]
        return {"thumb_url": src, "thumb_url_xs": src}
    pid = img_meta["id"]
    return {
        "thumb_url":    BASE + pid + PARAMS_THUMB,
        "thumb_url_xs": BASE + pid + PARAMS_THUMB_XS,
    }


def resolve_image(soup: BeautifulSoup, title: str,
                  date_str: str, summary: str) -> tuple[dict, str]:
    """이미지 결정 메인 로직. 반환: (img_meta dict, source string)"""
    art = find_article_image(soup)
    if art:
        return art, "article_image"

    cat = detect_category(title, summary)
    if cat and cat in CATEGORY_IMAGE_MAP:
        img = select_from_pool(CATEGORY_IMAGE_MAP[cat], title, date_str)
        return img, "handpick_category"

    img = select_from_pool(DEFAULT_IMAGE_POOL, title, date_str)
    return img, "handpick_default"


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
    head.append(link)


def ensure_reader_mode(body) -> None:
    existing = body.get("class", [])
    if isinstance(existing, str):
        existing = existing.split()
    if "reader-mode" not in existing:
        existing.append("reader-mode")
    body["class"] = existing


def process_article(html_path: Path, briefing_meta: dict) -> dict:
    """단일 기사 HTML 변환. 반환: briefings.json 갱신용 thumb 메타 dict."""
    soup  = BeautifulSoup(html_path.read_text("utf-8"), "html.parser")
    title = briefing_meta.get("title", "")
    date  = briefing_meta.get("date", "")
    summ  = briefing_meta.get("summary", "")

    img_meta, _source = resolve_image(soup, title, date, summ)
    urls = make_urls(img_meta)

    head = soup.find("head")
    body = soup.find("body")
    if head is None or body is None:
        return {"thumb_category": "default"}

    remove_previous_reader_chrome(soup)
    ensure_theme_link(soup)
    ensure_reader_mode(body)

    body.insert(0, BeautifulSoup(GNB_HTML, "html.parser"))
    body.append(BeautifulSoup(FOOTER_HTML, "html.parser"))

    html_path.write_text(str(soup), "utf-8")

    cat = detect_category(title, summ) or "default"

    return {
        "thumb_url":        urls["thumb_url"],
        "thumb_url_xs":     urls["thumb_url_xs"],
        "thumb_alt":        img_meta["alt"],
        "thumb_category":   cat,
    }


def get_log_source(meta: dict) -> str:
    if not meta.get("thumb_url", "").startswith(BASE):
        return "article_image"
    if meta.get("thumb_category") == "default":
        return "handpick_default"
    return "handpick_category"


def main():
    data = json.loads(BRIEFINGS_JSON.read_text("utf-8"))

    for briefing in data.get("briefings", []):
        for key in HERO_META_KEYS:
            briefing.pop(key, None)

        date      = briefing.get("date", "")
        html_path = ARCHIVE_DIR / f"{date}.html"
        if not html_path.exists():
            print(f"[SKIP] {date}.html not found")
            continue

        meta = process_article(html_path, briefing)
        briefing.update(meta)
        print(f"[OK] {date} cat={meta['thumb_category']} src={get_log_source(meta)}")

    BRIEFINGS_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), "utf-8"
    )
    print("[DONE] briefings.json updated.")

if __name__ == "__main__":
    main()
