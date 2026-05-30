import re
import json
import hashlib
from collections import deque
from pathlib import Path
from bs4 import BeautifulSoup

ROOT_DIR       = Path(__file__).resolve().parent.parent
ARCHIVE_DIR    = ROOT_DIR / "archive"
BRIEFINGS_JSON = ROOT_DIR / "briefings.json"

BASE = "https://images.unsplash.com/photo-"

PARAMS_HERO     = "?w=1200&h=630&fit=crop&auto=format&q=80"
PARAMS_HERO_SM  = "?w=640&h=360&fit=crop&auto=format&q=80"
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

# 빌드 세션 전역 중복 차단 큐 (직전 5개 이미지 ID 기억)
_dedup_window: deque = deque(maxlen=5)

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

def _img(photo_id, alt, credit_name, tags=None):
    """tags: 이미지 연관 영문 키워드 리스트."""
    return {
        "id":          photo_id,
        "alt":         alt,
        "credit_name": credit_name,
        "credit_url":  f"https://unsplash.com/photos/{photo_id}",
        "tags":        [t.lower() for t in (tags or [])],
    }

CATEGORY_IMAGE_MAP = {

    # ── 1. AI / 인공지능 ────────────────────────────────────────
    "ai": [
        _img("1677442135703-1787eea5ce01",
             "Blue neural network data visualization on dark background",
             "Growtika",
             tags=["ai", "neural", "data", "model", "llm"]),
        _img("1620712943543-bcc4688e7485",
             "Cybernetic virtual brain with glowing circuits",
             "Possessed Photography"),
        _img("1518770660439-4636190af475",
             "Gold pattern silicon microchip circuit board macro",
             "Alexandre Debiève"),
        _img("1526374965328-7f61d4dc18c5",
             "Matrix green binary code wall on black screen",
             "Markus Spiske"),
        _img("1507146426996-ef05306b995a",
             "Neon glowing line tech art abstract dark",
             "Alina Grubnyak"),
        _img("1555066931-4365d14bab8c",
             "Green matrix code rain on dark screen",
             "Markus Spiske"),
        _img("1485827404703-89b55fcc595e",
             "Robot hand touching glowing digital interface",
             "Alex Knight"),
        _img("1526378722484-bd91ca387e72",
             "Glowing robotic hand reaching through screen",
             "Franck V."),
        _img("1607604276583-eef5d076aa5f",
             "Blue neon illuminated circuit motherboard",
             "Olivier Collet"),
        _img("1488590528505-98d2b5aba04b",
             "Neon data stream transmission visual",
             "Umberto"),
        _img("1618005182384-a83a8bd57fbe",
             "Abstract dark silk web browser art visual",
             "Growtika"),
        _img("1562577309-4932fdd64cd1",
             "Data marketing multi-screen dashboard display",
             "Luke Chesser"),
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
        _img("1591696331111-ef9586a5b17a",
             "CPU processor chip macro photograph",
             "Slejven Djurakovic"),
        _img("1601004890684-d8cbf643f5f2",
             "Intel processor on motherboard close-up",
             "Olivier Collet"),
        _img("1587202372634-32705e3bf49c",
             "Silicon wafer manufacturing clean room",
             "Laura Ockel"),
        _img("1640158615573-cd28feb1bf4e",
             "Semiconductor chip magnified surface texture",
             "Vishnu Mohanan"),
        _img("1544197150-b99a580bb7a8",
             "Server rack fiber optic cables blue glow",
             "Alina Grubnyak"),
        _img("1488590528505-98d2b5aba04b",
             "Neon data stream transmission visual",
             "Umberto"),
        _img("1677442135703-1787eea5ce01",
             "Blue neural network data visualization on dark background",
             "Growtika"),
        _img("1507146426996-ef05306b995a",
             "Neon glowing line tech art abstract dark",
             "Alina Grubnyak"),
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
        _img("1579621970563-ebec7560ff3e",
             "Financial graph upward trend dark background",
             "Tech Daily"),
        _img("1559526324-593bc073d938",
             "Bitcoin gold coin dark background macro",
             "Dmitry Demidko"),
        _img("1486406146926-c627a92ad1ab",
             "Glass skyscrapers financial district twilight",
             "Sean Pollock"),
        _img("1454165804606-c3d57bc86b40",
             "Global trade chart analysis dark screen",
             "Cytonn Photography"),
        _img("1504711434969-e33886168f5c",
             "Aerial city lights skyline night view",
             "Maximalfocus"),
        _img("1601597111158-2fceff292cdc",
             "Dark harbor container crane silhouette",
             "Channey"),
        _img("1494412574643-ff11b0a5c1c3",
             "Aerial container port terminal shipping",
             "Tom Fisk"),
        _img("1586528116311-ad8dd3c8310d",
             "World map shipping route light graphic",
             "Thomas Lefebvre"),
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
        _img("1508614589041-895b88991e3e",
             "Futuristic robot head glowing blue eyes",
             "Possessed Photography"),
        _img("1561144257-e32e8efc6c4f",
             "Robotic welding arm bright sparks dark",
             "Ant Rozetsky"),
        _img("1525338078858-d762b5e32f2c",
             "Industrial robot arm precision factory dark",
             "Lenny Kuhne"),
        _img("1547153760-18fc86324498",
             "Autonomous robot exploring terrain outdoor",
             "Lenny Kuhne"),
        _img("1526378722484-bd91ca387e72",
             "Glowing robotic hand reaching through screen",
             "Franck V."),
        _img("1544716278-ca5e3f4abd8c",
             "LiDAR sensor autonomous driving line graphic",
             "Possessed Photography"),
        _img("1620712943543-bcc4688e7485",
             "Cybernetic virtual brain with glowing circuits",
             "Possessed Photography"),
        _img("1677442135703-1787eea5ce01",
             "Blue neural network data visualization on dark background",
             "Growtika"),
    ],

    # ── 5. 우주 / SpaceX ────────────────────────────────────────
    "space": [
        _img("1451187580459-43490279c0fa",
             "Blue Earth viewed from dark outer space orbit",
             "NASA",
             tags=["space", "earth", "orbit", "nasa", "satellite"]),
        _img("1506703719100-a0f3a48c0f86",
             "Majestic aurora borealis with deep space nebula",
             "Greg Rakozy"),
        _img("1446776811953-b23d57bd21aa",
             "Space station solar panels orbiting Earth",
             "NASA"),
        _img("1541185933-ef5d8ed016c2",
             "Rocket launch trajectory arc into night sky",
             "SpaceX"),
        _img("1614730321146-b6fa6a46bcb4",
             "Deep space nebula colorful gas clouds",
             "Jeremy Thomas"),
        _img("1516849841032-87cbac4d88f7",
             "Rocket launching bright exhaust flame night",
             "SpaceX"),
        _img("1419242902214-272b3f66ee7a",
             "Satellite view Earth city lights night",
             "NASA"),
        _img("1586348943529-beaae6c28db9",
             "Space rocket interior launch control room",
             "SpaceX"),
        _img("1506084868230-bb9d95c24759",
             "Aircraft vapor trails contrails in night sky",
             "Amir Kabirov"),
        _img("1517976487492-5750f3195933",
             "Fighter jet cockpit interior control panel",
             "Lasseter Wen"),
        _img("1451187580459-43490279c0fa",
             "Planet Earth viewed from space with city lights",
             "NASA"),
        _img("1506703719100-a0f3a48c0f86",
             "Majestic aurora borealis with deep space nebula",
             "Greg Rakozy"),
    ],

    # ── 6. 헬스케어 / 웨어러블 ──────────────────────────────────
    "health": [
        _img("1576091160399-112ba8d25d1d",
             "Glowing DNA helix structure graphic in dark lab",
             "National Cancer Institute"),
        _img("1559757148-5c350d0d3c56",
             "DNA helix biotech visualization blue light",
             "Warren Umoh"),
        _img("1505751172876-fa1923c5c528",
             "Smart wearable health monitoring loop screen",
             "Online Marketing"),
        _img("1571019613454-1cb2f99b2d8b",
             "Pharmaceutical drug vials medical dark",
             "Nguyen Dang Hoang Nhu"),
        _img("1516549655169-df83a0774514",
             "Genome sequencing data visualization screen",
             "Shahadat Rahman"),
        _img("1620712943543-bcc4688e7485",
             "Cybernetic virtual brain with glowing circuits",
             "Possessed Photography"),
        _img("1677442135703-1787eea5ce01",
             "Blue neural network data visualization on dark background",
             "Growtika"),
        _img("1562577309-4932fdd64cd1",
             "Data marketing multi-screen dashboard display",
             "Luke Chesser"),
        _img("1498050108023-c5249f4df085",
             "Laptop displaying code in dark environment",
             "Christopher Gower"),
        _img("1526374965328-7f61d4dc18c5",
             "Matrix green binary code wall on black screen",
             "Markus Spiske"),
        _img("1507146426996-ef05306b995a",
             "Neon glowing line tech art abstract dark",
             "Alina Grubnyak"),
        _img("1555066931-4365d14bab8c",
             "Green matrix code rain on dark screen",
             "Markus Spiske"),
    ],

    # ── 7. 전기차 / EV ──────────────────────────────────────────
    "ev": [
        _img("1563720223185-11003d516935",
             "Autonomous vehicle headlight light trails tech art",
             "Jp Valery"),
        _img("1593941707882-a5bba14938c7",
             "Electric vehicle charging port glowing blue",
             "dcbel"),
        _img("1617788138017-80ad40651399",
             "Sleek EV body curves in dark studio lighting",
             "Juice Flair"),
        _img("1544716278-ca5e3f4abd8c",
             "LiDAR sensor autonomous driving line graphic",
             "Possessed Photography"),
        _img("1558618666-fcd25c85cd64",
             "Tesla electric car scenic mountain road",
             "Charlie Deets"),
        _img("1603584173870-7f23fdae1b7a",
             "Modern EV interior dashboard illuminated",
             "Jp Valery"),
        _img("1502877338535-766e1452684a",
             "Electric car charger plug closeup night",
             "Chuttersnap"),
        _img("1563720223185-11003d516935",
             "Autonomous vehicle headlight trails tech art",
             "Jp Valery"),
        _img("1593941707882-a5bba14938c7",
             "EV charging connector glowing close-up",
             "dcbel"),
        _img("1617788138017-80ad40651399",
             "Electric car studio curves and reflections",
             "Juice Flair"),
        _img("1544716278-ca5e3f4abd8c",
             "Autonomous driving sensor line graphic",
             "Possessed Photography"),
        _img("1494412574643-ff11b0a5c1c3",
             "Aerial transport terminal infrastructure",
             "Tom Fisk"),
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
        _img("1553729459-efe14ef6055d",
             "Large container cargo ship ocean port",
             "Channey"),
        _img("1486406146926-c627a92ad1ab",
             "Glass skyscrapers financial district twilight",
             "Sean Pollock"),
        _img("1611974789855-9c2a0a7236a3",
             "Global stock indices digital display dark",
             "Maxim Hopman"),
        _img("1494412574643-ff11b0a5c1c3",
             "Aerial container port terminal shipping",
             "Tom Fisk"),
        _img("1504711434969-e33886168f5c",
             "Aerial city lights skyline night view",
             "Maximalfocus"),
        _img("1579621970563-ebec7560ff3e",
             "Financial graph upward trend dark background",
             "Tech Daily"),
        _img("1590283603385-17ffb3a7f29f",
             "Blue tone stock trading dashboard interface",
             "Konstantin Evdokimov"),
        _img("1642543492481-44e81e3914a7",
             "Financial data abstract 3D volume visualization",
             "Adam Nowakowski"),
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
        _img("1497366216548-37526070297c",
             "Blue fiber optic light strands glowing dark",
             "Umberto"),
        _img("1606765962248-7ff407b51667",
             "Data center server racks blue illuminated",
             "Taylor Vick"),
        _img("1558494949-ef010cbdcc31",
             "5G signal wave abstract visualization",
             "Umberto"),
        _img("1617791160536-598cf32026fb",
             "Satellite dish antenna array night",
             "NASA"),
        _img("1504711434969-e33886168f5c",
             "Global internet cable undersea network",
             "Maximalfocus"),
        _img("1516321318423-f06f85e504b3",
             "Digital node hub connection network abstract art",
             "Alina Grubnyak"),
        _img("1544197150-b99a580bb7a8",
             "Dark blue fiber optic server rack cables",
             "Alina Grubnyak"),
        _img("1600132806370-bf17e65e942f",
             "Tall cell tower antenna night sky",
             "Thomas Kelley"),
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
        _img("1573804633927-bfcbcd909acd",
             "Modern tech company open office natural light",
             "Marvin Meyer"),
        _img("1580927752452-89d86da3fa0a",
             "Developer coding laptop dark room",
             "Christopher Gower"),
        _img("1460925895917-afdab827c52f",
             "Startup open office bright modern furniture",
             "Alex Kotliarskyi"),
        _img("1517245386807-bb43f82c33c4",
             "Devices laptop tablet phone clean desk",
             "Thomas Lefebvre"),
        _img("1496181133206-80ce9b88a853",
             "MacBook Pro keyboard backlit close-up",
             "Ales Nesetril"),
        _img("1504868584819-f8e8b4b6d7e3",
             "Social media apps smartphone screen dark",
             "Adem AY"),
        _img("1606765962248-7ff407b51667",
             "Data center server racks blue illuminated",
             "Taylor Vick"),
        _img("1544197150-b99a580bb7a8",
             "Server rack fiber optic cables blue glow",
             "Alina Grubnyak"),
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
        _img("1507679799987-c73779587ccf",
             "Wooden gavel courtroom justice symbol",
             "Tingey Injury Law Firm"),
        _img("1450101499163-c8848c66ca85",
             "Legal books wooden gavel close-up court",
             "Sora Shimazaki"),
        _img("1541872705-1f73c6400ec9",
             "Parliament government building dusk exterior",
             "Louis Velazquez"),
        _img("1589829545856-d10d557cf95f",
             "Government building classical columns",
             "René DeAnda"),
        _img("1486406146926-c627a92ad1ab",
             "Glass skyscrapers financial district twilight",
             "Sean Pollock"),
        _img("1454165804606-c3d57bc86b40",
             "Regulatory compliance dashboard dark screen",
             "Cytonn Photography"),
        _img("1504711434969-e33886168f5c",
             "Aerial city lights civic infrastructure",
             "Maximalfocus"),
        _img("1505664194779-8beaceb93744",
             "Classic law books leather cover detail",
             "Tingey Injury Law Firm"),
        _img("1450133064473-71024230f91b",
             "Solemn government columns silhouette",
             "Louis Velazquez"),
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
        _img("1517976487492-5750f3195933",
             "Fighter jet cockpit interior control panel",
             "Lasseter Wen"),
        _img("1451187580459-43490279c0fa",
             "Earth viewed from orbit military satellite context",
             "NASA"),
        _img("1446776811953-b23d57bd21aa",
             "Space station solar panels orbiting Earth",
             "NASA"),
        _img("1541185933-ef5d8ed016c2",
             "Rocket launch trajectory arc into night sky",
             "SpaceX"),
        _img("1516849841032-87cbac4d88f7",
             "Rocket launching bright exhaust flame night",
             "SpaceX"),
        _img("1419242902214-272b3f66ee7a",
             "Satellite view Earth city lights night",
             "NASA"),
        _img("1586348943529-beaae6c28db9",
             "Space rocket interior launch control room",
             "SpaceX"),
        _img("1600132806370-bf17e65e942f",
             "Tall antenna mast defense communications",
             "Thomas Kelley"),
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


CATEGORY_SMART_TAGS = {
    "ai": ["ai", "artificial", "intelligence", "openai", "anthropic", "claude", "gpt", "gemini", "model", "llm", "neural", "code", "robot", "data"],
    "chip": ["chip", "semiconductor", "nvidia", "tsmc", "micron", "sk", "hbm", "wafer", "circuit", "server", "gpu", "processor"],
    "finance": ["stock", "market", "ipo", "fed", "rate", "bond", "bitcoin", "crypto", "finance", "trading", "wall", "street"],
    "robot": ["robot", "humanoid", "unitree", "figure", "automation", "drone", "mechanical", "factory", "autonomous"],
    "space": ["space", "spacex", "starship", "starlink", "rocket", "launch", "nasa", "orbit", "satellite", "moon", "mars", "earth"],
    "health": ["health", "medical", "fitbit", "wearable", "bio", "dna", "drug", "pharma", "genome", "fitness"],
    "ev": ["ev", "tesla", "electric", "vehicle", "battery", "charging", "autonomous", "lidar", "car"],
    "economy": ["economy", "trade", "tariff", "inflation", "gdp", "dollar", "shipping", "supply", "global", "port"],
    "telecom": ["telecom", "5g", "6g", "network", "fiber", "satellite", "antenna", "data", "server", "internet"],
    "bigtech": ["google", "apple", "meta", "microsoft", "amazon", "software", "developer", "cloud", "platform", "app"],
    "policy": ["policy", "regulation", "court", "law", "congress", "government", "legal", "safety", "compliance"],
    "defense": ["defense", "military", "drone", "fighter", "radar", "satellite", "security", "weapon", "army", "naval"],
}

CATEGORY_EXTRA_IMAGES = {
    "ai": [
        ("1531297484001-80022131f5a1", "Premium laptop display dark setup", "Ales Nesetril", ["laptop", "coding", "developer", "screen", "software", "ai"]),
        ("1580927752452-89d86da3fa0a", "Developer coding laptop dark room", "Christopher Gower", ["coding", "developer", "programming", "software", "llm", "model"]),
        ("1498050108023-c5249f4df085", "Laptop displaying code in dark environment", "Christopher Gower", ["code", "screen", "developer", "software", "ai"]),
        ("1573804633927-bfcbcd909acd", "Modern tech company open office", "Marvin Meyer", ["startup", "technology", "office", "ai", "platform"]),
        ("1517245386807-bb43f82c33c4", "Devices laptop tablet phone clean desk", "Thomas Lefebvre", ["device", "app", "software", "technology", "platform"]),
        ("1496181133206-80ce9b88a853", "Backlit laptop keyboard close-up", "Ales Nesetril", ["keyboard", "developer", "coding", "software", "dark"]),
        ("1606765962248-7ff407b51667", "Data center server racks blue illuminated", "Taylor Vick", ["compute", "server", "data", "cloud", "ai"]),
        ("1544197150-b99a580bb7a8", "Fiber optic cables in server rack", "Alina Grubnyak", ["network", "data", "server", "compute", "ai"]),
        ("1516321318423-f06f85e504b3", "Digital node hub connection abstract", "Alina Grubnyak", ["network", "node", "digital", "data", "ai"]),
        ("1607604276583-eef5d076aa5f", "Blue neon motherboard circuit detail", "Olivier Collet", ["circuit", "hardware", "chip", "ai", "compute"]),
        ("1591453089816-0fbb971b454c", "Abstract semiconductor lattice grid", "Laura Ockel", ["chip", "semiconductor", "grid", "hardware", "ai"]),
        ("1555664424-778a1e5e1b48", "Circuit board traces macro close-up", "Alex Andrews", ["circuit", "board", "hardware", "compute", "ai"]),
    ],
    "space": [
        ("1506084868230-bb9d95c24759", "Aircraft vapor trails in night sky", "Amir Kabirov", ["sky", "flight", "aerospace", "night", "space"]),
        ("1517976487492-5750f3195933", "Fighter jet cockpit interior panel", "Lasseter Wen", ["cockpit", "aerospace", "flight", "control", "mission"]),
        ("1569003339405-ea396a5a8a90", "Dark security zone restricted fence", "Ehud Neuhaus", ["security", "mission", "base", "space", "night"]),
        ("1600132806370-bf17e65e942f", "Tall antenna mast communications", "Thomas Kelley", ["antenna", "signal", "satellite", "network", "space"]),
        ("1497366216548-37526070297c", "Blue fiber optic light strands", "Umberto", ["starlink", "network", "signal", "satellite", "data"]),
        ("1544197150-b99a580bb7a8", "Server rack fiber optic cables", "Alina Grubnyak", ["starlink", "network", "satellite", "data", "spacex"]),
        ("1606765962248-7ff407b51667", "Data center server racks blue", "Taylor Vick", ["mission", "control", "data", "satellite", "network"]),
        ("1450133064473-71024230f91b", "Solemn columns and sky silhouette", "Louis Velazquez", ["nasa", "government", "mission", "space", "policy"]),
        ("1508873535684-277a3cbcc4e8", "Helicopter dark hangar silhouette", "David Henrichs", ["aerospace", "hangar", "flight", "mission", "rocket"]),
        ("1473163928189-364b2c4e1135", "Radar scan line screen display", "Chris Henry", ["radar", "tracking", "orbit", "satellite", "mission"]),
        ("1516849841032-87cbac4d88f7", "Rocket bright exhaust flame", "SpaceX", ["rocket", "launch", "spacex", "flame", "liftoff"]),
        ("1541185933-ef5d8ed016c2", "Rocket launch trajectory night sky", "SpaceX", ["rocket", "launch", "starship", "spacex", "night"]),
    ],
}

_SHARED_EXTRAS = [
    ("1504711434969-e33886168f5c", "Aerial city lights skyline night view", "Maximalfocus"),
    ("1451187580459-43490279c0fa", "Blue Earth viewed from dark outer space", "NASA"),
    ("1498050108023-c5249f4df085", "Laptop displaying code in dark environment", "Christopher Gower"),
    ("1522071820081-009f0129c71c", "Tech team collaborating on laptops in office", "Annie Spratt"),
    ("1606765962248-7ff407b51667", "Data center server racks blue illuminated", "Taylor Vick"),
    ("1544197150-b99a580bb7a8", "Server rack fiber optic cables blue glow", "Alina Grubnyak"),
    ("1486406146926-c627a92ad1ab", "Glass skyscrapers financial district twilight", "Sean Pollock"),
    ("1611974789855-9c2a0a7236a3", "Stock market chart dark monitor", "Maxim Hopman"),
    ("1517976487492-5750f3195933", "Fighter jet cockpit interior control panel", "Lasseter Wen"),
    ("1507679799987-c73779587ccf", "Wooden gavel courtroom justice symbol", "Tingey Injury Law Firm"),
    ("1593941707882-a5bba14938c7", "Electric vehicle charging port glowing blue", "dcbel"),
    ("1571019613454-1cb2f99b2d8b", "Pharmaceutical drug vials medical dark", "Nguyen Dang Hoang Nhu"),
]


def _augment_category_image_map() -> None:
    for category, pool in CATEGORY_IMAGE_MAP.items():
        base_tags = CATEGORY_SMART_TAGS.get(category, [])
        for img in pool:
            if not img.get("tags"):
                img["tags"] = list(base_tags)

        extras = CATEGORY_EXTRA_IMAGES.get(category)
        if extras is None:
            extras = [
                (photo_id, alt, credit, base_tags)
                for photo_id, alt, credit in _SHARED_EXTRAS
            ]

        cursor = 0
        while len(pool) < 24:
            photo_id, alt, credit, tags = extras[cursor % len(extras)]
            pool.append(_img(photo_id, alt, credit, tags=tags or base_tags))
            cursor += 1


_augment_category_image_map()


def smart_pick_image(pool: list, article_text: str) -> dict | None:
    """
    기사 텍스트와 이미지 tags를 비교해 의미상 가장 가까운 이미지를 선택.
    매칭 점수가 없으면 None을 반환해 기존 hash+dedup 로직으로 fallback.
    """
    text = article_text.lower()
    best_img = None
    best_score = 0

    for img in pool:
        score = sum(1 for tag in img.get("tags", []) if tag and tag in text)
        if score > best_score and img.get("id") not in _dedup_window:
            best_img = img
            best_score = score

    if best_img and best_score > 0:
        _dedup_window.append(best_img["id"])
        return best_img

    return None


def select_from_pool(pool: list, title: str, date_str: str = "") -> dict:
    """
    제목+날짜 해시 → 결정론적 기본 인덱스 산출.
    중복 차단: _dedup_window에 있는 ID면 index +1 shift 우회.
    """
    seed     = f"{title}_{date_str}".encode("utf-8")
    base_idx = int(hashlib.md5(seed).hexdigest(), 16) % len(pool)

    for shift in range(len(pool)):
        idx       = (base_idx + shift) % len(pool)
        candidate = pool[idx]
        if candidate["id"] not in _dedup_window:
            _dedup_window.append(candidate["id"])
            return candidate

    # 풀 전체가 윈도우 안에 있을 때 → 강제 반환
    fallback = pool[base_idx]
    _dedup_window.append(fallback["id"])
    return fallback


def parse_title_segments(raw_title: str) -> list:
    """파이프(|) 분할 -> 개별 기사 제목 리스트."""
    return [t.strip() for t in raw_title.split('|') if t.strip()]


def parse_summary_sentences(raw_summary: str) -> list:
    """마침표+공백 분할 -> 문장 리스트."""
    return [s.strip() for s in re.split(r'\.\s+', raw_summary) if s.strip()]


def detect_category(title: str, summary: str) -> str | None:
    """
    스코어링 기반 카테고리 탐지.
    텍스트 초반 매칭일수록 높은 가중치(1.0→0.1),
    전체 매칭 횟수×가중치 합산 후 최고점 카테고리 반환.
    """
    text = title + " " + summary
    text_len = max(len(text), 1)

    best_cat   = None
    best_score = 0.0

    for category_key, pattern in CATEGORY_PATTERNS:
        score = 0.0
        for m in re.finditer(pattern, text, re.IGNORECASE):
            pos_weight = 1.0 - (m.start() / text_len) * 0.9
            score += pos_weight

        if score > best_score:
            best_score = score
            best_cat   = category_key

    return best_cat if best_score > 0.0 else None


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
        return {
            "hero_url":     src,
            "hero_url_sm":  src,
            "thumb_url":    src,
            "thumb_url_xs": src,
        }
    pid = img_meta["id"]
    return {
        "hero_url":     BASE + pid + PARAMS_HERO,
        "hero_url_sm":  BASE + pid + PARAMS_HERO_SM,
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
        pool = CATEGORY_IMAGE_MAP[cat]
        img = smart_pick_image(pool, f"{title} {summary}")
        if img:
            return img, "smart_pick"

        img = select_from_pool(pool, title, date_str)
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

    img_meta, source = resolve_image(soup, title, date, summ)
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
        "hero_url":         urls["hero_url"],
        "hero_url_sm":      urls["hero_url_sm"],
        "hero_alt":         img_meta["alt"],
        "hero_credit_name": img_meta.get("credit_name", ""),
        "hero_credit_url":  img_meta.get("credit_url", ""),
        "hero_source":      source,
        "thumb_url":        urls["thumb_url"],
        "thumb_url_xs":     urls["thumb_url_xs"],
        "thumb_alt":        img_meta["alt"],
        "thumb_category":   cat,
    }


def get_log_source(meta: dict) -> str:
    if meta.get("hero_source"):
        return meta["hero_source"]
    if not meta.get("thumb_url", "").startswith(BASE):
        return "article_image"
    if meta.get("thumb_category") == "default":
        return "handpick_default"
    return "handpick_category"


def build_segments_with_images(raw_title: str, raw_summary: str, date_str: str) -> list:
    """
    타이틀 파이프 분할 + 요약 비례 배분 + 세그먼트별 독립 이미지 매칭.
    반환: [{title, summary, thumb_url, thumb_url_xs, thumb_alt, thumb_category}, ...]
    """
    titles    = parse_title_segments(raw_title)
    sentences = parse_summary_sentences(raw_summary)

    if not titles:
        return []

    n        = len(titles)
    per_slot = len(sentences) // n if sentences else 0
    remain   = len(sentences) % n if sentences else 0
    segments = []
    cursor   = 0

    for i, title in enumerate(titles):
        count   = per_slot + (remain if i == n - 1 else 0)
        chunk   = sentences[cursor:cursor + count]
        summary = '. '.join(chunk) + ('.' if chunk else '')
        cursor += count

        cat = detect_category(title, summary)

        if cat and cat in CATEGORY_IMAGE_MAP:
            pool     = CATEGORY_IMAGE_MAP[cat]
            smart    = smart_pick_image(pool, title + " " + summary)
            img_meta = smart if smart else select_from_pool(pool, title, date_str)
        else:
            img_meta = select_from_pool(DEFAULT_IMAGE_POOL, title, date_str)
            cat = "default"

        urls = make_urls(img_meta)
        segments.append({
            "title":          title,
            "summary":        summary,
            "thumb_url":      urls["thumb_url"],
            "thumb_url_xs":   urls["thumb_url_xs"],
            "thumb_alt":      img_meta.get("alt", ""),
            "thumb_category": cat or "default",
        })

    return segments


def _process_list(items: list, label: str) -> None:
    """briefings / weekly / specials 공통 후처리 루프."""
    for item in items:
        for key in HERO_META_KEYS:
            item.pop(key, None)

        date      = item.get("date", "")
        html_path = ARCHIVE_DIR / f"{date}.html"
        if not html_path.exists():
            print(f"[SKIP-{label}] {date}.html not found")
            continue

        meta = process_article(html_path, item)
        item.update(meta)
        item.pop("segments", None)
        raw_title   = item.get("title", "")
        raw_summary = item.get("summary", "")
        segs = build_segments_with_images(raw_title, raw_summary, date)
        if segs:
            item["segments"] = segs
        print(f"  -> {len(segs)} segments: {[s['thumb_category'] for s in segs]}")
        print(f"[OK-{label}] {date} cat={meta['thumb_category']} src={get_log_source(meta)}")


def main():
    data = json.loads(BRIEFINGS_JSON.read_text("utf-8"))

    _process_list(data.get("briefings", []), "briefing")
    _process_list(data.get("weekly",    []), "weekly")
    _process_list(data.get("specials",  []), "special")

    BRIEFINGS_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), "utf-8"
    )
    print("[DONE] briefings.json updated.")

if __name__ == "__main__":
    main()
