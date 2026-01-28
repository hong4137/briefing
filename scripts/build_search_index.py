#!/usr/bin/env python3
"""
Build search index from archive HTML files.
Parses all HTML files in archive/ folder and creates search-index.json

v3: Handles multiple HTML format versions + Claude's Pick support
"""

import os
import re
import json
from html.parser import HTMLParser
from datetime import datetime


class BriefingParser(HTMLParser):
    """Parse briefing HTML to extract articles - handles multiple format versions."""
    
    def __init__(self):
        super().__init__()
        self.articles = []
        self.current_article = {}
        self.current_section = ""
        self.is_claudes_pick = False
        
        # Tag tracking
        self.in_h2 = False
        self.in_h3 = False
        self.in_p = False
        self.in_article = False
        
        # Class detection
        self.current_tag_class = ""
        self.current_text = ""
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        class_name = attrs_dict.get('class', '')
        
        # Track article container
        if tag == 'article':
            self.in_article = True
            # Save previous article if complete
            if self._is_article_complete():
                self.articles.append(self.current_article.copy())
            self.current_article = {
                'section': self.current_section,
                'is_pick': self.is_claudes_pick
            }
            
        # Section headers (h2 tags)
        if tag == 'h2':
            self.in_h2 = True
            self.current_text = ""
            
        # Article titles (h3 tags)
        if tag == 'h3':
            self.in_h3 = True
            self.current_tag_class = class_name
            self.current_text = ""
            
        # Paragraphs - check class for different content types
        if tag == 'p':
            self.in_p = True
            self.current_tag_class = class_name
            self.current_text = ""
                
    def handle_endtag(self, tag):
        if tag == 'h2' and self.in_h2:
            self.in_h2 = False
            section = self.current_text.strip()
            self.current_section = section
            # Check if this is Claude's Pick section
            if any(x in section for x in ["Claude's Pick", "클로드", "💎", "Pick"]):
                self.is_claudes_pick = True
            elif any(x in section for x in ["TOP", "🔥", "AI", "🤖", "경제", "💰", "반도체", "💾", "글로벌", "🌏", "🌐"]):
                self.is_claudes_pick = False
            self.current_text = ""
            
        if tag == 'h3' and self.in_h3:
            self.in_h3 = False
            title = self.current_text.strip()
            # Remove badges like HOT, NEW, PICK
            title = re.sub(r'\s*(HOT|NEW|PICK)\s*$', '', title).strip()
            if title:
                # This could be English title or Korean title depending on format
                if 'article-title' in self.current_tag_class and 'kr' not in self.current_tag_class:
                    self.current_article['title_en'] = title
                else:
                    self.current_article['title'] = title
            self.current_tag_class = ""
            self.current_text = ""
            
        if tag == 'p' and self.in_p:
            self.in_p = False
            text = self.current_text.strip()
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            
            if text and len(text) > 10:
                if 'article-title-kr' in self.current_tag_class:
                    # Korean title
                    self.current_article['title'] = text
                elif 'article-summary' in self.current_tag_class:
                    # Summary
                    self.current_article['summary'] = text
                elif 'summary' not in self.current_article and self.in_article:
                    # First paragraph after title is usually summary
                    if 'title' in self.current_article or 'title_en' in self.current_article:
                        self.current_article['summary'] = text
                        
            self.current_tag_class = ""
            self.current_text = ""
            
        if tag == 'article':
            self.in_article = False
            # Save article when closing article tag
            if self._is_article_complete():
                self.articles.append(self.current_article.copy())
                self.current_article = {
                    'section': self.current_section,
                    'is_pick': self.is_claudes_pick
                }
            
    def handle_data(self, data):
        if self.in_h2 or self.in_h3 or self.in_p:
            self.current_text += data
            
    def _is_article_complete(self):
        """Check if current article has required fields."""
        has_title = 'title' in self.current_article or 'title_en' in self.current_article
        has_summary = 'summary' in self.current_article
        return has_title and has_summary
            
    def get_articles(self):
        # Don't forget last article
        if self._is_article_complete():
            self.articles.append(self.current_article.copy())
        return self.articles


def extract_date_from_filename(filename):
    """Extract date from filename like 2026-01-28.html"""
    match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    # Handle special files
    if 'weekly' in filename.lower():
        match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        if match:
            return match.group(1)
    if 'special' in filename.lower():
        return filename.replace('.html', '')
    return None


def extract_keywords(title, summary):
    """Extract searchable keywords from title and summary."""
    text = f"{title} {summary}".lower()
    
    keywords = set()
    
    # Extract capitalized words (likely proper nouns)
    proper_nouns = re.findall(r'\b[A-Z][a-zA-Z]+\b', f"{title} {summary}")
    keywords.update(word.lower() for word in proper_nouns if len(word) > 2)
    
    # Extract Korean/English company/product names
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
        r'Netflix|넷플릭스', r'DOGE',
        r'CES', r'IPO', r'투자|펀딩',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            keywords.add(match.group().lower())
    
    return list(keywords)[:15]  # Limit keywords


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
    
    # Process and normalize articles
    result = []
    seen_titles = set()
    
    for article in articles:
        # Get best title (prefer Korean, fallback to English)
        title = article.get('title') or article.get('title_en', '')
        summary = article.get('summary', '')
        
        if not title or not summary:
            continue
            
        # Skip duplicates
        if title in seen_titles:
            continue
        seen_titles.add(title)
        
        result.append({
            'date': date,
            'file': filename.replace('.html', ''),
            'title': title,
            'summary': summary[:300],  # Limit summary length
            'keywords': extract_keywords(title, summary),
            'section': article.get('section', ''),
            'is_pick': article.get('is_pick', False)
        })
    
    return result


def build_search_index(archive_dir='archive'):
    """Build search index from all archive files."""
    if not os.path.exists(archive_dir):
        print(f"Archive directory '{archive_dir}' not found")
        return {'articles': [], 'total': 0, 'picks': 0, 'updated': datetime.now().isoformat()}
    
    all_articles = []
    pick_count = 0
    
    # Process all HTML files
    for filename in sorted(os.listdir(archive_dir), reverse=True):
        if filename.endswith('.html'):
            filepath = os.path.join(archive_dir, filename)
            articles = parse_briefing_file(filepath)
            
            # Count picks
            picks = sum(1 for a in articles if a.get('is_pick'))
            pick_count += picks
            
            all_articles.extend(articles)
            print(f"Parsed {filename}: {len(articles)} articles ({picks} picks)")
    
    # Create index
    index = {
        'articles': all_articles,
        'total': len(all_articles),
        'picks': pick_count,
        'updated': datetime.now().isoformat()
    }
    
    return index


def main():
    """Main entry point."""
    print("Building search index (v3 - multi-format support)...")
    print("=" * 50)
    
    index = build_search_index('archive')
    
    # Write to file
    output_file = 'search-index.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print("=" * 50)
    print(f"Search index created: {output_file}")
    print(f"Total articles indexed: {index['total']}")
    print(f"Claude's Picks: {index['picks']}")


if __name__ == '__main__':
    main()
