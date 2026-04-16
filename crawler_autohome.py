"""
汽车之家数据爬虫 v2
爬取极氪车型数据：参数、图片、口碑
"""
import requests
import json
import time
import re
from pathlib import Path
from bs4 import BeautifulSoup
import random

class AutohomeCrawler:
    """汽车之家数据爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://www.autohome.com.cn"
        })
        self.data_dir = Path("e:/pyspace/zeeker/crawler_data")
        self.data_dir.mkdir(exist_ok=True)
        
    def _safe_get(self, url, encoding='utf-8', max_retries=2):
        """安全的GET请求"""
        for i in range(max_retries):
            try:
                resp = self.session.get(url, timeout=15)
                # 尝试不同编码
                if encoding == 'gbk':
                    try:
                        resp.encoding = 'gbk'
                    except:
                        resp.encoding = 'utf-8'
                else:
                    resp.encoding = 'utf-8'
                
                if resp.status_code == 200:
                    # 清理非法字符
                    text = resp.text
                    try:
                        return text.encode('utf-8', errors='ignore').decode('utf-8')
                    except:
                        return text
                time.sleep(1)
            except Exception as e:
                print(f"  ⚠️ 请求失败: {e}")
                time.sleep(3)
        return None
    
    def crawl_series_info(self, car_key, series_id):
        """爬取车型主页信息"""
        print(f"\n🚗 爬取 极氪{car_key}...")
        
        url = f"https://www.autohome.com.cn/{series_id}/"
        html = self._safe_get(url, encoding='utf-8')
        
        if not html:
            print(f"  ❌ 页面获取失败")
            return {}
        
        soup = BeautifulSoup(html, 'html.parser')
        data = {"车型": f"极氪{car_key}", "series_id": series_id}
        
        # 提取价格
        price_elem = soup.select_one('.price-range, .car-price, [class*="price"]')
        if price_elem:
            data["价格区间"] = price_elem.text.strip()
        
        # 提取参数标签
        param_items = soup.select('.config-item, .param-item, [class*="spec"]')
        params = {}
        for item in param_items[:15]:
            spans = item.select('span, label')
            if len(spans) >= 2:
                key = spans[0].text.strip()
                val = spans[1].text.strip()
                if key and val and len(key) < 20:
                    params[key] = val
        data["基本参数"] = params
        
        # 提取配置亮点
        highlights = soup.select('.highlight-item, .feature-item, [class*="feature"]')
        data["配置亮点"] = [h.text.strip() for h in highlights[:8] if h.text.strip()]
        
        # 提取图片URL
        img_pattern = re.compile(r'https?://[^\s"\'<>]+\.(?:jpg|jpeg|png)', re.I)
        images = list(set(img_pattern.findall(html)))[:30]
        data["图片URL"] = images
        
        # 保存数据
        out_file = self.data_dir / f"zeekr_{car_key}_autohome.json"
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  ✅ 保存到: {out_file}")
        print(f"     - 基本参数: {len(params)} 项")
        print(f"     - 配置亮点: {len(data['配置亮点'])} 项")
        print(f"     - 图片: {len(images)} 张")
        
        return data
    
    def crawl_specs_detail(self, car_key, series_id):
        """爬取详细参数页"""
        print(f"\n📊 爬取 极氪{car_key} 详细参数...")
        
        url = f"https://www.autohome.com.cn/{series_id}/params.html"
        html = self._safe_get(url)
        
        if not html:
            return {}
        
        soup = BeautifulSoup(html, 'html.parser')
        specs = {}
        
        # 参数表格
        tables = soup.select('table, .params-table')
        for table in tables:
            rows = table.select('tr, dl')
            for row in rows:
                cells = row.select('td, dt, dd')
                if len(cells) >= 2:
                    key = cells[0].text.strip()
                    val = cells[1].text.strip()
                    if key and val and len(key) < 30:
                        specs[key] = val
        
        return specs
    
    def crawl_photo_list(self, car_key, series_id):
        """爬取图片列表"""
        print(f"\n🖼️ 爬取 极氪{car_key} 图片列表...")
        
        url = f"https://www.autohome.com.cn/{series_id}/photo.html"
        html = self._safe_get(url)
        
        if not html:
            return []
        
        # 提取图片URL
        img_pattern = re.compile(r'https?://[^\s"\'<>]+\.(?:jpg|jpeg|png)', re.I)
        images = list(set(img_pattern.findall(html)))
        
        print(f"  📷 找到 {len(images)} 张图片URL")
        return images
    
    def crawl_koubei(self, car_key, series_id):
        """爬取口碑摘要"""
        print(f"\n💬 爬取 极氪{car_key} 口碑...")
        
        url = f"https://k.autohome.com.cn/{series_id}"
        html = self._safe_get(url)
        
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        koubei = []
        
        items = soup.select('.kouzi-item, .review-item, [class*="koubei"]')
        for item in items[:5]:
            title = item.select_one('h4, .title, a')
            text = item.select_one('.text, .con, p')
            if title:
                koubei.append({
                    "标题": title.text.strip()[:50],
                    "内容": text.text.strip()[:100] if text else ""
                })
        
        print(f"  💬 找到 {len(koubei)} 条口碑")
        return koubei
    
    def run(self):
        """运行爬虫"""
        print("=" * 55)
        print("   🚗 汽车之家 - 极氪车型数据爬虫 v2")
        print("=" * 55)
        
        # 极氪车型ID映射
        zeeks_series = {
            "001": "7440",
            "007": "7869", 
            "X": "7281",
            "009": "7377",
            "7X": "8349",
        }
        
        all_data = {}
        
        for car_key, series_id in zeeks_series.items():
            print(f"\n{'='*50}")
            print(f"  🚗 极氪{car_key} (ID: {series_id})")
            print(f"{'='*50}")
            
            car_data = {}
            
            # 1. 主页信息
            series_data = self.crawl_series_info(car_key, series_id)
            car_data.update(series_data)
            time.sleep(random.uniform(1, 2))
            
            # 2. 详细参数
            specs = self.crawl_specs_detail(car_key, series_id)
            if specs:
                car_data["详细参数"] = specs
            time.sleep(random.uniform(1, 2))
            
            # 3. 图片列表
            images = self.crawl_photo_list(car_key, series_id)
            car_data["图片URL列表"] = images
            time.sleep(random.uniform(1, 2))
            
            # 4. 口碑
            koubei = self.crawl_koubei(car_key, series_id)
            car_data["口碑摘要"] = koubei
            
            all_data[car_key] = car_data
            
            # 保存单车型数据
            out_file = self.data_dir / f"zeekr_{car_key}_full.json"
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(car_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n  💾 {car_key} 数据已保存")
            time.sleep(random.uniform(2, 4))
        
        # 保存汇总
        summary_file = self.data_dir / "all_zeeks_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 55)
        print("✅ 爬取完成!")
        print(f"📁 数据目录: {self.data_dir}")
        print("=" * 55)
        
        # 打印摘要
        print("\n📊 数据摘要:")
        for key, data in all_data.items():
            print(f"\n  🚗 极氪{key}:")
            print(f"     价格: {data.get('价格区间', 'N/A')}")
            print(f"     参数: {len(data.get('基本参数', {}))} 项")
            print(f"     图片: {len(data.get('图片URL列表', []))} 张")
            print(f"     口碑: {len(data.get('口碑摘要', []))} 条")
        
        return all_data


def main():
    print("""
========================================================
   [AUTOHOME] 汽车之家极氪数据爬虫 v2
========================================================
  将爬取: 极氪001、007、X、009、7X
  数据包括: 参数配置、口碑、图片链接
========================================================
    """)
    
    crawler = AutohomeCrawler()
    
    try:
        data = crawler.run()
    except KeyboardInterrupt:
        print("\n⚠️ 已中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
