"""
极氪图片元数据库
基于六维分类体系
"""
import os
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from enum import Enum

# 图片库根目录
IMAGE_LIB_PATH = r"e:\pyspace\joker\zeeker\官网图片_已清洗"

@dataclass
class ImageMetadata:
    """图片元数据"""
    path: str                          # 图片路径
    filename: str                      # 文件名
    car_series: str                    # 车型系列
    content_theme: List[str] = field(default_factory=list)  # 内容主题
    design_language: List[str] = field(default_factory=list)  # 设计语言
    marketing_theme: List[str] = field(default_factory=list)  # 营销主题
    market_position: str = ""           # 市场定位
    image_type: str = "官图"           # 图片类型
    resolution: str = ""               # 分辨率
    status: str = "可用"              # 使用状态
    description: str = ""              # 图片描述

# ============================================================
# 车型映射 (英文键,文件夹名为中文)
# ============================================================
# 文件夹实际名称 -> 英文键 的映射
FOLDER_TO_KEY = {
    "极氪001": "ZEEKR 001",
    "极氪007": "ZEEKR 007",
    "极氪X": "ZEEKR X",
    "极氪009": "ZEEKR 009",
    "极氪7X": "ZEEKR 7X",
    "极氪001FR": "ZEEKR 001 FR",
    "极氪001 FR": "ZEEKR 001 FR",
}

# 英文键 -> 文件夹名 的映射
KEY_TO_FOLDER = {v: k for k, v in FOLDER_TO_KEY.items()}

CAR_SERIES_MAP = {
    "ZEEKR 001": {"name": "ZEEKR 001", "position": "高端旗舰", "type": "猎装轿跑"},
    "ZEEKR 007": {"name": "ZEEKR 007", "position": "中坚力量", "type": "豪华轿车"},
    "ZEEKR X": {"name": "ZEEKR X", "position": "入门走量", "type": "都市精品SUV"},
    "ZEEKR 009": {"name": "ZEEKR 009", "position": "高端旗舰", "type": "豪华MPV"},
    "ZEEKR 7X": {"name": "ZEEKR 7X", "position": "中坚力量", "type": "豪华SUV"},
    "ZEEKR 001 FR": {"name": "ZEEKR 001 FR", "position": "极致性能", "type": "纯电超跑"},
    "尊界 S800": {"name": "尊界 S800", "position": "超豪华旗舰", "type": "超豪华轿车"},
}

# ============================================================
# 内容主题分类
# ============================================================
CONTENT_THEMES = {
    "外观全览": ["整车外观", "前脸", "侧身", "尾部", "45度角"],
    "内饰细节": ["座椅", "仪表盘", "方向盘", "中控", "内饰整体"],
    "核心科技": ["STARGATE灯幕", "800V高压", "电机", "电池", "智能驾驶"],
    "驾驶动态": ["赛道", "公路", "加速", "姿态", "夜景"],
    "空间体验": ["后备箱", "后排空间", "储物", "座舱"],
    "场景融入": ["家庭", "商务", "露营", "旅行"],
    "品牌格调": ["科技感", "豪华感", "简约", "国韵"],
}

# ============================================================
# 设计语言分类
# ============================================================
DESIGN_LANGUAGES = {
    "Hidden Energy": ["隐藏能量", "渐变", "光影"],
    "极简主义": ["简约", "干净", "克制"],
    "科技新奢": ["科技", "豪华", "精致"],
    "东方国韵": ["国韵", "东方", "中式"],
}

# ============================================================
# 市场定位
# ============================================================
MARKET_POSITIONS = {
    "入门走量": ["X"],
    "中坚力量": ["007", "7X"],
    "高端旗舰": ["001", "009"],
    "极致性能": ["001 FR"],
}

# ============================================================
# 自动分析文件名关键词
# ============================================================
def analyze_filename_keywords(filename: str) -> Dict:
    """根据文件名自动分析可能的标签"""
    filename_lower = filename.lower()
    
    themes = []
    design = []
    description = ""
    
    # 内容主题关键词
    theme_keywords = {
        "外观全览": ["外观", "全览", "整车", "外观图", "正面", "侧面", "尾部"],
        "内饰细节": ["内饰", "座椅", "仪表", "中控", "方向盘", "内部"],
        "核心科技": ["科技", "灯光", "灯幕", "800v", "电机", "电池", "智驾"],
        "驾驶动态": ["赛道", "动态", "加速", "行驶", "公路", "姿态"],
        "空间体验": ["空间", "后备箱", "储物", "后排"],
        "场景融入": ["家庭", "商务", "露营", "户外", "生活"],
        "品牌格调": ["设计", "风格", "美学"],
    }
    
    for theme, keywords in theme_keywords.items():
        if any(k in filename_lower for k in keywords):
            themes.append(theme)
    
    if not themes:
        themes.append("外观全览")  # 默认
        
    # 设计语言关键词
    design_keywords = {
        "Hidden Energy": ["hidden", "能量", "渐变"],
        "极简主义": ["简约", "极简", "干净"],
        "科技新奢": ["科技", "豪华", "新奢"],
        "东方国韵": ["国韵", "东方", "国风"],
    }
    
    for dl, keywords in design_keywords.items():
        if any(k in filename_lower for k in keywords):
            design.append(dl)
    
    if not design:
        design.append("科技新奢")  # 默认
    
    # 生成描述
    description = f"{' '.join(themes)} - {' '.join(design)}风格"
    
    return {
        "themes": themes,
        "design": design,
        "description": description
    }

# ============================================================
# 构建图片数据库
# ============================================================
def build_image_database() -> Dict[str, List[ImageMetadata]]:
    """扫描并构建图片数据库"""
    database = {}
    
    for car_folder, car_info in CAR_SERIES_MAP.items():
        # 使用中文文件夹名来查找
        folder_name = KEY_TO_FOLDER.get(car_folder, car_folder)
        folder_path = os.path.join(IMAGE_LIB_PATH, folder_name)
        if not os.path.exists(folder_path):
            # 尝试直接使用 car_folder 查找
            folder_path = os.path.join(IMAGE_LIB_PATH, car_folder)
            if not os.path.exists(folder_path):
                continue
        
        images = []
        for filename in os.listdir(folder_path):
            if not filename.endswith(('.jpg', '.png', '.jpeg')):
                continue
            
            filepath = os.path.join(folder_path, filename)
            
            # 分析文件名
            analysis = analyze_filename_keywords(filename)
            
            # 确定市场定位
            position = car_info["position"]
            for pos, cars in MARKET_POSITIONS.items():
                if any(c.lower() in car_folder.lower() for c in cars):
                    position = pos
                    break
            
            metadata = ImageMetadata(
                path=filepath,
                filename=filename,
                car_series=car_folder,  # 使用英文键
                content_theme=analysis["themes"],
                design_language=analysis["design"],
                marketing_theme=["官方素材"],  # 默认
                market_position=position,
                image_type="官图",
                status="可用",
                description=analysis["description"]
            )
            images.append(metadata)
        
        # 使用英文键作为数据库的键
        database[car_folder] = images
        print(f"{car_folder}: {len(images)}张图片")
    
    return database

# ============================================================
# 检索功能
# ============================================================
def search_images(
    database: Dict[str, List[ImageMetadata]],
    car: str = None,
    theme: str = None,
    design: str = None,
    position: str = None,
    keyword: str = None
) -> List[ImageMetadata]:
    """多维度检索图片"""
    results = []
    
    # 先按车型筛选
    if car:
        cars = [car] if car in database else [k for k in database.keys() if car.lower() in k.lower()]
        for c in cars:
            results.extend(database.get(c, []))
    else:
        for images in database.values():
            results.extend(images)
    
    # 按主题筛选
    if theme:
        results = [img for img in results if theme in img.content_theme]
    
    # 按设计语言筛选
    if design:
        results = [img for img in results if any(design in d for d in img.design_language)]
    
    # 按市场定位筛选
    if position:
        results = [img for img in results if position in img.market_position]
    
    # 按关键词搜索
    if keyword:
        keyword_lower = keyword.lower()
        results = [
            img for img in results 
            if keyword_lower in img.filename.lower() or keyword_lower in img.description.lower()
        ]
    
    return results

# 全局数据库实例
IMAGE_DATABASE = build_image_database()

def get_all_images() -> List[ImageMetadata]:
    """获取所有图片"""
    all_imgs = []
    for images in IMAGE_DATABASE.values():
        all_imgs.extend(images)
    return all_imgs

def get_car_images(car: str, limit: int = 0) -> List[ImageMetadata]:
    """获取某车型的所有图片
    
    Args:
        car: 车型名称 (如 "ZEEKR 001")
        limit: 限制返回数量, 0表示不限制
    Returns:
        图片元数据列表
    """
    for key in IMAGE_DATABASE.keys():
        if car.lower() in key.lower():
            images = IMAGE_DATABASE[key]
            return images[:limit] if limit > 0 else images
    return []

def search_by_keyword(keyword: str) -> List[ImageMetadata]:
    """关键词搜索"""
    return search_images(IMAGE_DATABASE, keyword=keyword)

def search_by_theme(car: str, theme: str) -> List[ImageMetadata]:
    """按主题搜索某车型图片"""
    return search_images(IMAGE_DATABASE, car=car, theme=theme)

if __name__ == "__main__":
    print("\n=== 极氪图片数据库 ===\n")
    print(f"总图片数: {len(get_all_images())}")
    print("\n按车型统计:")
    for car, images in IMAGE_DATABASE.items():
        print(f"  {car}: {len(images)}张")
    
    print("\n=== 测试检索 ===")
    results = search_images(IMAGE_DATABASE, car="001", theme="外观全览")
    print(f"001外观全览: {len(results)}张")
