"""
图片清洗脚本
1. 删除尺寸过小的图片（二维码通常很小）
2. 删除宽高比异常的 图片
3. 检查并过滤无效图片
"""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image

IMAGE_LIB_PATH = r"e:\pyspace\joker\zeeker\官网图片_已清洗"

# 小图片阈值（像素）- 二维码通常小于 300x300
MIN_WIDTH = 300
MIN_HEIGHT = 300

# 宽高比异常阈值 - 极端的宽高比可能是非车型图片
MIN_ASPECT_RATIO = 0.3  # 高/宽
MAX_ASPECT_RATIO = 3.0  # 高/宽

def clean_folder(folder_path):
    """清洗单个文件夹"""
    deleted = []
    kept = []
    
    if not os.path.exists(folder_path):
        print(f"  文件夹不存在: {folder_path}")
        return deleted, kept
    
    for filename in os.listdir(folder_path):
        if not filename.endswith(('.jpg', '.png', '.jpeg', '.JPG', '.PNG')):
            continue
        
        filepath = os.path.join(folder_path, filename)
        
        try:
            with Image.open(filepath) as img:
                width, height = img.size
                aspect_ratio = height / width if width > 0 else 0
                
                # 检查1: 尺寸过小
                if width < MIN_WIDTH or height < MIN_HEIGHT:
                    deleted.append((filename, f"尺寸太小: {width}x{height}"))
                    os.remove(filepath)
                    continue
                
                # 检查2: 宽高比异常 (排除极窄或极宽的图片)
                if aspect_ratio < MIN_ASPECT_RATIO or aspect_ratio > MAX_ASPECT_RATIO:
                    deleted.append((filename, f"宽高比异常: {aspect_ratio:.2f}"))
                    # os.remove(filepath)  # 暂不删除，只记录
                    # continue
                
                kept.append((filename, f"{width}x{height}"))
                
        except Exception as e:
            deleted.append((filename, f"读取错误: {e}"))
            try:
                os.remove(filepath)
            except:
                pass
    
    return deleted, kept

def main():
    print("=" * 60)
    print("图片清洗工具")
    print(f"路径: {IMAGE_LIB_PATH}")
    print(f"最小尺寸: {MIN_WIDTH}x{MIN_HEIGHT}")
    print("=" * 60)
    
    total_deleted = 0
    total_kept = 0
    
    for folder in os.listdir(IMAGE_LIB_PATH):
        folder_path = os.path.join(IMAGE_LIB_PATH, folder)
        if not os.path.isdir(folder_path):
            continue
        
        print(f"\n📁 {folder}")
        deleted, kept = clean_folder(folder_path)
        
        if deleted:
            print(f"  🗑️  删除: {len(deleted)} 张")
            for name, reason in deleted[:5]:  # 只显示前5个
                print(f"     - {name}: {reason}")
            if len(deleted) > 5:
                print(f"     ... 还有 {len(deleted) - 5} 张")
        
        if kept:
            print(f"  ✅ 保留: {len(kept)} 张")
        
        total_deleted += len(deleted)
        total_kept += len(kept)
    
    print("\n" + "=" * 60)
    print(f"总计: 删除 {total_deleted} 张, 保留 {total_kept} 张")
    print("=" * 60)

if __name__ == "__main__":
    main()
