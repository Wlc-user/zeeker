"""
生成ZEEKR车型专业占位图
使用PIL生成带有车型名称的科技感图片
"""
import os
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

# ZEEKR车型数据
ZEEKR_CARS = {
    "zeekr_001.jpg": {
        "name": "ZEEKR 001",
        "subtitle": "豪华猎装轿跑",
        "price": "26.9-76.9万",
        "color": (0, 100, 200)  # 蓝色
    },
    "zeekr_007.jpg": {
        "name": "ZEEKR 007", 
        "subtitle": "纯电豪华轿车",
        "price": "20.99-29.99万",
        "color": (0, 180, 220)  # 青色
    },
    "zeekr_x.jpg": {
        "name": "ZEEKR X",
        "subtitle": "新奢全能SUV",
        "price": "18.98-22.98万",
        "color": (120, 0, 200)  # 紫色
    },
    "zeekr_009.jpg": {
        "name": "ZEEKR 009",
        "subtitle": "豪华纯电MPV",
        "price": "50-58万",
        "color": (50, 50, 150)  # 深蓝
    },
    "zeekr_fr.jpg": {
        "name": "ZEEKR 001 FR",
        "subtitle": "纯电猎装超跑",
        "price": "76.9万",
        "color": (220, 0, 100)  # 红色
    }
}

def create_car_image(filename, data):
    """创建车型图片"""
    width, height = 800, 500
    
    # 创建渐变背景
    img = Image.new('RGB', (width, height), data['color'])
    draw = ImageDraw.Draw(img)
    
    # 绘制渐变效果
    for i in range(height):
        ratio = i / height
        r = int(data['color'][0] * (1 - ratio * 0.5))
        g = int(data['color'][1] * (1 - ratio * 0.3))
        b = int(data['color'][2] + (255 - data['color'][2]) * ratio * 0.3)
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    # 绘制网格线（科技感）
    draw = ImageDraw.Draw(img)
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=(255, 255, 255), width=1)
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=(255, 255, 255), width=1)
    
    # 绘制车型名称
    try:
        font_large = ImageFont.truetype("arial.ttf", 72)
        font_medium = ImageFont.truetype("arial.ttf", 36)
        font_small = ImageFont.truetype("arial.ttf", 28)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # 车型名称
    bbox = draw.textbbox((0, 0), data['name'], font=font_large)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) / 2, 120), data['name'], fill=(255, 255, 255), font=font_large)
    
    # 副标题
    bbox = draw.textbbox((0, 0), data['subtitle'], font=font_medium)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) / 2, 210), data['subtitle'], fill=(200, 200, 200), font=font_medium)
    
    # 价格
    bbox = draw.textbbox((0, 0), data['price'], font=font_small)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) / 2, 280), data['price'], fill=(255, 215, 0), font=font_small)
    
    # 绘制简约车辆轮廓
    car_color = (255, 255, 255)
    # 车身轮廓线
    points = [
        (150, 380), (180, 340), (280, 320), (520, 320), (620, 340), (650, 380),
        (650, 400), (150, 400)
    ]
    draw.polygon(points, fill=None, outline=car_color, width=3)
    
    # 车轮
    draw.ellipse([200, 390, 250, 440], fill=(50, 50, 50), outline=car_color, width=2)
    draw.ellipse([550, 390, 600, 440], fill=(50, 50, 50), outline=car_color, width=2)
    
    # 保存图片
    filepath = os.path.join(ASSETS_DIR, filename)
    img.save(filepath, quality=95)
    print(f"Created: {filename}")

if __name__ == "__main__":
    print("Generating ZEEKR car images...\n")
    for filename, data in ZEEKR_CARS.items():
        create_car_image(filename, data)
    print("\nDone!")
