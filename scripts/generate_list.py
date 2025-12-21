import os
import json
import re

# briefing 저장소 루트 기준 경로 설정
ARCHIVE_DIR = 'archive'  # HTML 파일들이 있는 폴더
LIST_FILE = 'list.json'  # 업데이트할 리스트 파일

def get_title_from_html(file_path):
    """HTML 파일에서 제목 추출"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            if match:
                return match.group(1).replace("Jae's Briefing - ", "").strip()
            match_h1 = re.search(r'<h1>(.*?)</h1>', content, re.IGNORECASE)
            if match_h1:
                return match_h1.group(1).strip()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return "제목 없음"

def main():
    if not os.path.exists(ARCHIVE_DIR):
        print(f"❌ 폴더를 찾을 수 없음: {ARCHIVE_DIR}")
        return

    briefing_list = []
    
    # 파일 목록 읽기 (최신 날짜가 위로 오게 정렬)
    files = [f for f in os.listdir(ARCHIVE_DIR) if f.endswith('.html')]
    files.sort(reverse=True)

    print(f"📂 {len(files)}개의 파일 발견. 리스트 갱신 중...")

    for filename in files:
        date_str = filename.replace('.html', '')
        file_path = os.path.join(ARCHIVE_DIR, filename)
        title = get_title_from_html(file_path)
        
        # [중요] 대시보드에서 링크를 열 수 있도록 전체 주소(URL)로 저장
        # 대시보드는 다른 저장소에 있으므로 절대 경로가 필요함
        full_link = f"https://hong4137.github.io/briefing/archive/{filename}"
        
        briefing_list.append({
            "date": date_str,
            "title": title,
            "link": full_link
        })

    with open(LIST_FILE, 'w', encoding='utf-8') as f:
        json.dump(briefing_list, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {LIST_FILE} 업데이트 완료!")

if __name__ == "__main__":
    main()
