"""
下载ZEEKR官方车型图片
"""
import urllib.request
import os
import ssl

# 禁用SSL验证
ssl._create_default_https_context = ssl._create_unverified_context

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

# ZEEKR官方图片URL (来自汽车之家/懂车帝等)
ZEEKR_IMAGES = {
    "zeekr_001.jpg": "https://img.autohome.com.cn/car/0x0/1/7440/7440.jpg",
    "zeekr_007.jpg": "https://img.autohome.com.cn/car/0x0/1/7441/7441.jpg",
    "zeekr_x.jpg": "https://img.autohome.com.cn/car/0x0/1/7442/7442.jpg",
    "zeekr_009.jpg": "https://img.autohome.com.cn/car/0x0/1/7443/7443.jpg",
    "zeekr_fr.jpg": "https://img.autohome.com.cn/car/0x0/1/7444/7444.jpg",
}

def download_image(url, filename):
    """下载图片"""
    filepath = os.path.join(ASSETS_DIR, filename)
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(filepath, 'wb') as f:
                f.write(response.read())
        print(f"✅ 下载成功: {filename}")
        return True
    except Exception as e:
        print(f"❌ 下载失败 {filename}: {e}")
        return False

if __name__ == "__main__":
    print("开始下载ZEEKR车型图片...\n")
    for filename, url in ZEEKR_IMAGES.items():
        download_image(url, filename)
    print("\n下载完成！")
