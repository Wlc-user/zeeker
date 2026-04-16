"""
下载汽车之家爬取的图片
"""
import requests
import json
import os
from pathlib import Path

DATA_DIR = Path("e:/pyspace/zeeker/crawler_data")
SAVE_DIR = Path("e:/pyspace/zeeker/assets/autohome")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
    "Referer": "https://www.autohome.com.cn"
}

# 过滤有效图片URL
def is_valid_car_image(url):
    """判断是否为有效的车型图片"""
    invalid_patterns = [
        'logo', 'icon', 'app_', 'star_', 'blank', 
        'qrcode', 'aad-', 'pcm/', 'topbar', 'footer',
        'wechat', 'weather', 'video'
    ]
    url_lower = url.lower()
    return (
        ('autoimg.cn' in url or 'autohome' in url) and
        not any(p in url_lower for p in invalid_patterns) and
        ('.jpg' in url_lower or '.jpeg' in url_lower) and
        len(url) > 50
    )

# 车型文件映射
car_files = {
    "001": "zeekr_001_autohome.json",
    "007": "zeekr_007_autohome.json",
    "X": "zeekr_X_autohome.json",
    "009": "zeekr_009_autohome.json",
    "7X": "zeekr_7X_autohome.json"
}

total_downloaded = 0

for car_key, filename in car_files.items():
    filepath = DATA_DIR / filename
    if not filepath.exists():
        print(f"[{car_key}] 文件不存在: {filename}")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    urls = data.get("图片URL", [])
    valid_urls = [u for u in urls if is_valid_car_image(u)]
    
    print(f"\n[极氪{car_key}] 有效图片: {len(valid_urls)}/{len(urls)}")
    
    car_save_dir = SAVE_DIR / f"zeekr_{car_key}"
    car_save_dir.mkdir(exist_ok=True)
    
    downloaded = 0
    for i, url in enumerate(valid_urls[:30]):  # 每车型最多30张
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200 and len(resp.content) > 5000:  # 大于5KB
                ext = 'jpg' if '.jpg' in url.lower() else 'png'
                filename = f"zeekr_{car_key}_autohome_{i+1:02d}.{ext}"
                filepath = car_save_dir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(resp.content)
                
                downloaded += 1
                print(f"  [{i+1}] {filename} ({len(resp.content)//1024}KB)")
        except Exception as e:
            print(f"  [x] 失败: {str(e)[:50]}")
    
    total_downloaded += downloaded
    print(f"  -> {downloaded} 张已下载")

print(f"\n" + "="*50)
print(f"总计下载: {total_downloaded} 张图片")
print(f"保存目录: {SAVE_DIR}")
print("="*50)
