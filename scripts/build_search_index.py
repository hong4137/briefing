#!/usr/bin/env python3
"""
Build search index from archive HTML files.
Parses all HTML files in archive/ folder and creates search-index.json

v2: Added Claude's Pick support + improved section detection
"""

import os
import re
import json
from html.parser import HTMLParser
from datetime import datetime


class BriefingParser(HTMLParser):
    """Parse briefing HTML to extract articles."""
    
    def __init__(self):
        super().__init__()
        self.articles = []
        self.current_article = {}
        self.in_title = False
        self.in_summary = False
        self.capture_text = False
        self.current_text = ""
        self.current_section = ""
        self.is_claudes_pick = False
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        # Detect section headers (h2 tags)
        if tag == 'h2':
            self.capture_text = True
            self.current_text = ""
            
        # Capture article titles (h3 tags)
        if tag == 'h3':
            self.in_title = True
            self.capture_text = True
            self.current_text = ""
            
        # Capture summaries (p tags after h3)
        if tag == 'p' and self.current_article.get('title'):
            if not self.current_article.get('summary'):
                self.in_summary = True
                self.capture_text = True
                self.current_text = ""
                
        # Capture article links
        if tag == 'a' and self.current_article.get('title'):
            href = attrs_dict.get('href', '')
            if href.startswith('http') and not self.current_article.get('url'):
                self.current_article['url'] = href
                
    def handle_endtag(self, tag):
        if tag == 'h2':
            if self.capture_text and self.current_text:
                section = self.current_text.strip()
                self.current_section = section
                # Check if this is Claude's Pick section
                if "Claude's Pick" in section or "클로드" in section or "💎" in section:
                    self.is_claudes_pick = True
                else:
                    self.is_claudes_pick = False
            self.capture_text = False
            self.current_text = ""
            
        if tag == 'h3':
            if self.in_title and self.current_text:
                # Save previous article if exists
                if self.current_article.get('title') and self.current_article.get('summary'):
                    self.articles.append(self.current_article.copy())
                
                # Start new article
                title = self.current_text.strip()
                # Remove tags like HOT, NEW, PICK
                title = re.sub(r'\s*(HOT|NEW|PICK)\s*$', '', title).strip()
                
                self.current_article = {
                    'title': title,
                    'section': self.current_section,
                    'is_pick': self.is_claudes_pick
                }
                
            self.in_title = False
            self.capture_text = False
            self.current_text = ""
            
        if tag == 'p' and self.in_summary:
            if self.current_text:
                summary = self.current_text.strip()
                # Clean up summary
                summary = re.sub(r'\s+', ' ', summary)
                if len(summary) > 20:  # Only save meaningful summaries
                    self.current_article['summary'] = summary
            self.in_summary = False
            self.capture_text = False
            self.current_text = ""
            
    def handle_data(self, data):
        if self.capture_text:
            self.current_text += data
            
    def get_articles(self):
        # Don't forget last article
        if self.current_article.get('title') and self.current_article.get('summary'):
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
    keywords.update(word.lower() for word in proper_nouns)
    
    # Extract Korean company/product names
    korean_patterns = [
        r'삼성|Samsung', r'SK하이닉스|SK Hynix|하이닉스',
        r'네이버|Naver', r'카카오|Kakao',
        r'엔비디아|Nvidia|NVIDIA', r'인텔|Intel',
        r'AMD|에이엠디', r'TSMC',
        r'애플|Apple', r'구글|Google', r'마이크로소프트|Microsoft',
        r'아마존|Amazon', r'메타|Meta|Facebook',
        r'테슬라|Tesla', r'OpenAI|오픈AI',
        r'Anthropic|앤트로픽|클로드|Claude',
        r'반도체', r'HBM', r'AI|인공지능',
        r'로봇', r'자율주행', r'전기차|EV',
        r'트럼프|Trump', r'중국|China',
    ]
    
    for pattern in korean_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                keywords.add(match.group().lower())
    
    return list(keywords)


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
    
    # Add date and keywords to each article
    result = []
    for article in articles:
        if article.get('title') and article.get('summary'):
            result.append({
                'date': date,
                'file': filename.replace('.html', ''),
                'title': article['title'],
                'summary': article['summary'],
                'keywords': extract_keywords(
                    article.get('title', ''),
                    article.get('summary', '')
                ),
                'section': article.get('section', ''),
                'is_pick': article.get('is_pick', False)
            })
    
    return result


def build_search_index(archive_dir='archive'):
    """Build search index from all archive files."""
    if not os.path.exists(archive_dir):
        print(f"Archive directory '{archive_dir}' not found")
        return {'articles': [], 'total': 0, 'updated': datetime.now().isoformat()}
    
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
    print("Building search index (v2 - with Claude's Pick)...")
    
    index = build_search_index('archive')
    
    # Write to file
    output_file = 'search-index.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"\nSearch index created: {output_file}")
    print(f"Total articles indexed: {index['total']}")
    print(f"Claude's Picks: {index['picks']}")


if __name__ == '__main__':
    main()
