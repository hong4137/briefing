#!/usr/bin/env python3
"""
Build search index from archive HTML files.
Parses all HTML files in archive/ folder and creates search-index.json

v4: Handles ALL HTML formats including:
- Early briefings without <article> tags
- Weekly briefings with different structure
- Various daily briefing formats
"""

import os
import re
import json
from html.parser import HTMLParser
from datetime import datetime


class BriefingParser(HTMLParser):
    """Parse briefing HTML to extract articles - handles all format versions."""
    
    def __init__(self):
        super().__init__()
        self.articles = []
        self.current_section = ""
        self.is_claudes_pick = False
        
        # Current article being built
        self.pending_title = ""
        self.pending_title_kr = ""
        self.pending_summary = ""
        
        # Tag state
        self.in_h2 = False
        self.in_h3 = False
        self.in_p = False
        self.current_class = ""
        self.current_text = ""
        
        # Track if we're inside an article tag
        self.in_article_tag = False

        # post_process.py가 구워둔 카드 앵커(id="art-N"). 순번을 추정하지 않는다.
        self.current_anchor = None
        
    def _save_pending_article(self):
        """Save the pending article if it has required fields."""
        title = self.pending_title_kr or self.pending_title
        summary = self.pending_summary
        
        if title and summary and len(summary) > 20:
            self.articles.append({
                'title': title.strip(),
                'summary': summary.strip()[:300],
                'section': self.current_section,
                'is_pick': self.is_claudes_pick,
                'anchor': self.current_anchor
            })
        
        # Reset pending
        self.pending_title = ""
        self.pending_title_kr = ""
        self.pending_summary = ""
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.current_class = attrs_dict.get('class', '')

        # 카드 경계는 태그 이름이 아니라 정규화된 id로 잡는다.
        # 주간·초기판은 <article>이 아니라 <div>를 쓰므로 이쪽이 모든 세대에 통한다.
        el_id = attrs_dict.get('id', '')
        if el_id.startswith('art-'):
            self._save_pending_article()
            self.current_anchor = el_id

        if tag == 'article':
            self.in_article_tag = True
            # Save any pending article before starting new one
            self._save_pending_article()
            
        if tag == 'h2':
            self.in_h2 = True
            self.current_text = ""
            
        if tag == 'h3':
            # New h3 means new article - save previous if exists
            if self.pending_title and not self.in_article_tag:
                self._save_pending_article()
            self.in_h3 = True
            self.current_text = ""
            
        if tag == 'p':
            self.in_p = True
            self.current_text = ""
                
    def handle_endtag(self, tag):
        if tag == 'article':
            self.in_article_tag = False
            self._save_pending_article()
            
        if tag == 'h2' and self.in_h2:
            self.in_h2 = False
            section = self.current_text.strip()
            self.current_section = section
            
            # Detect Claude's Pick section
            pick_keywords = ["Claude's Pick", "클로드", "💎", "Pick", "PICK"]
            section_keywords = ["TOP", "🔥", "AI", "🤖", "경제", "💰", "반도체", "💾", "글로벌", "🌏", "🌐", "Headlines", "기술"]
            
            if any(x in section for x in pick_keywords):
                self.is_claudes_pick = True
            elif any(x in section for x in section_keywords):
                self.is_claudes_pick = False
                
            self.current_text = ""
            
        if tag == 'h3' and self.in_h3:
            self.in_h3 = False
            title = self.current_text.strip()
            # Remove badges
            title = re.sub(r'\s*(HOT|NEW|PICK)\s*$', '', title).strip()
            
            if title:
                # Check if this is Korean title based on class or content
                if 'kr' in self.current_class.lower():
                    self.pending_title_kr = title
                elif re.search(r'[가-힣]', title):
                    # Contains Korean characters
                    self.pending_title_kr = title
                else:
                    self.pending_title = title
                    
            self.current_class = ""
            self.current_text = ""
            
        if tag == 'p' and self.in_p:
            self.in_p = False
            text = self.current_text.strip()
            text = re.sub(r'\s+', ' ', text)
            
            if text and len(text) > 15:
                # Determine what this paragraph is
                if 'title-kr' in self.current_class or 'article-title-kr' in self.current_class:
                    self.pending_title_kr = text
                elif 'summary' in self.current_class:
                    self.pending_summary = text
                elif not self.pending_summary and (self.pending_title or self.pending_title_kr):
                    # First substantial paragraph after title is summary
                    # Skip if it looks like metadata (sources, dates)
                    if not re.match(r'^(TechCrunch|Bloomberg|CNBC|BBC|Wired|Reuters|📅|Score:)', text):
                        self.pending_summary = text
                        
            self.current_class = ""
            self.current_text = ""
            
    def handle_data(self, data):
        if self.in_h2 or self.in_h3 or self.in_p:
            self.current_text += data
            
    def get_articles(self):
        # Save any remaining pending article
        self._save_pending_article()
        return self.articles


def extract_date_from_filename(filename):
    """Extract date from filename."""
    match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    if 'weekly' in filename.lower():
        match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        if match:
            return match.group(1)
    if 'special' in filename.lower():
        return filename.replace('.html', '')
    return None


def extract_keywords(title, summary):
    """Extract searchable keywords."""
    text = f"{title} {summary}".lower()
    keywords = set()
    
    # Proper nouns
    proper_nouns = re.findall(r'\b[A-Z][a-zA-Z]+\b', f"{title} {summary}")
    keywords.update(word.lower() for word in proper_nouns if len(word) > 2)
    
    # Known patterns
    patterns = [
        r'삼성|Samsung', r'SK하이닉스|SK Hynix|하이닉스',
        r'네이버|Naver', r'카카오|Kakao',
        r'엔비디아|Nvidia|NVIDIA', r'인텔|Intel',
        r'AMD|에이엠디', r'TSMC', r'마이크론|Micron',
        r'애플|Apple', r'구글|Google', r'마이크로소프트|Microsoft',
        r'아마존|Amazon', r'메타|Meta|Facebook',
        r'테슬라|Tesla', r'OpenAI|오픈AI|GPT',
        r'Anthropic|앤트로픽|클로드|Claude',
        r'반도체', r'HBM', r'AI|인공지능',
        r'로봇', r'자율주행', r'전기차|EV',
        r'트럼프|Trump', r'중국|China',
        r'BYD|비야디', r'Grok', r'xAI',
        r'Netflix|넷플릭스', r'DOGE', r'TikTok|틱톡',
        r'CES|다보스', r'IPO', r'투자|펀딩',
        r'Groq', r'금|Gold', r'은|Silver',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            keywords.add(match.group().lower())
    
    return list(keywords)[:15]


def parse_briefing_file(filepath):
    """Parse a single briefing HTML file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []
    
    filename = os.path.basename(filepath)
    date = extract_date_from_filename(filename)
    
    parser = BriefingParser()
    try:
        parser.feed(content)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return []
    
    articles = parser.get_articles()
    
    # Deduplicate and format
    result = []
    seen_titles = set()
    
    for article in articles:
        title = article.get('title', '')
        summary = article.get('summary', '')
        
        if not title or not summary:
            continue
            
        # Skip duplicates (case-insensitive)
        title_key = title.lower()[:50]
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)
        
        result.append({
            'date': date,
            'file': filename.replace('.html', ''),
            'title': title,
            'summary': summary,
            'keywords': extract_keywords(title, summary),
            'section': article.get('section', ''),
            'is_pick': article.get('is_pick', False),
            'anchor': article.get('anchor')
        })
    
    return result


def build_search_index(archive_dir='archive'):
    """Build search index from all archive files."""
    if not os.path.exists(archive_dir):
        print(f"Archive directory '{archive_dir}' not found")
        return {'articles': [], 'total': 0, 'picks': 0, 'updated': datetime.now().isoformat()}
    
    all_articles = []
    pick_count = 0
    
    for filename in sorted(os.listdir(archive_dir), reverse=True):
        if filename.endswith('.html'):
            filepath = os.path.join(archive_dir, filename)
            articles = parse_briefing_file(filepath)
            
            picks = sum(1 for a in articles if a.get('is_pick'))
            pick_count += picks
            
            all_articles.extend(articles)
            print(f"Parsed {filename}: {len(articles)} articles ({picks} picks)")
    
    with_anchor = sum(1 for a in all_articles if a.get('anchor'))
    rate = (with_anchor * 100 // len(all_articles)) if all_articles else 0
    print(f"[ANCHOR] {with_anchor}/{len(all_articles)} ({rate}%) 항목에 앵커 부여")
    if rate < 90:
        print("[ANCHOR][WARN] 앵커 매칭률 90% 미만 — post_process.py 백필이 선행됐는지 확인할 것")

    index = {
        'articles': all_articles,
        'total': len(all_articles),
        'picks': pick_count,
        'updated': datetime.now().isoformat()
    }
    
    return index


def main():
    """Main entry point."""
    print("Building search index (v4 - universal format support)...")
    print("=" * 50)
    
    index = build_search_index('archive')
    
    output_file = 'search-index.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print("=" * 50)
    print(f"Search index created: {output_file}")
    print(f"Total articles indexed: {index['total']}")
    print(f"Claude's Picks: {index['picks']}")


if __name__ == '__main__':
    main()
