"""
ZEEKR 极氪车型知识图谱
包含车型参数、竞品对比、客户画像、销售话术
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
import networkx as nx
import os

# 获取assets目录路径
ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets')

# ============================================================
# 车型数据库
# ============================================================

@dataclass
class CarModel:
    """车型数据类"""
    name: str                      # 车型名称
    price: str                     # 价格区间
    category: str                  # 类别
    target_customer: List[str]     # 目标客户
    highlights: List[str]          # 核心卖点
    specs: Dict[str, str]          # 核心参数
    competitors: List[str]         # 竞品
    sales_talk: Dict[str, str]     # 销售话术
    use_scenes: List[str]         # 使用场景
    image: str = ""                # 车型图片路径

# ZEEKR 全系车型
ZEEKR_MODELS = {
    "ZEEKR 001": CarModel(
        name="ZEEKR 001",
        price="26.9-76.9万",
        category="豪华猎装轿跑",
        target_customer=["科技爱好者", "追求驾驶乐趣", "家庭出行", "商务兼顾家用"],
        highlights=[
            "3.8秒百公里加速",
            "CLTC续航最高1032km",
            "空气悬架",
            "雅马哈音响",
            "浩瀚智能驾驶平台"
        ],
        specs={
            "长宽高": "4970×1999×1560mm",
            "轴距": "3005mm",
            "电机功率": "400kW",
            "电池容量": "100kWh/140kWh",
            "快充时间": "30分钟(10%-80%)",
            "智能驾驶": "ZAD完全自动驾驶辅助"
        },
        competitors=["特斯拉Model 3", "比亚迪汉", "蔚来ET7", "小鹏P7"],
        sales_talk={
            "开场": "001是极氪品牌的旗舰车型，将轿跑的优雅与SUV的空间完美融合",
            "性能": "双电机400kW功率，3.8秒破百，推背感堪比超跑",
            "续航": "140度麒麟电池版本，续航超过1000公里，长途无忧",
            "空间": "3005mm超长轴距，后排腿部空间超过1米",
            "智能": "浩瀚架构，支持OTA升级，智能化持续进化"
        },
        use_scenes=["家庭出游", "商务接待", "周末郊游", "日常通勤"],
        image=os.path.join(ASSETS_DIR, "zeekr_001.jpg")
    ),
    
    "ZEEKR 007": CarModel(
        name="ZEEKR 007",
        price="20.99-29.99万",
        category="纯电豪华轿车",
        target_customer=["年轻家庭", "首购新能源", "科技数码用户", "城市通勤族"],
        highlights=[
            "2.84秒百公里加速(四驱)",
            "870km CLTC续航",
            "8295芯片",
            "最大97寸AR-HUD",
            "V2L外放电"
        ],
        specs={
            "长宽高": "4865×1900×1450mm",
            "轴距": "2928mm",
            "电机功率": "475kW(四驱)",
            "电池容量": "75kWh/100kWh",
            "快充时间": "15分钟(10%-80%)",
            "智能驾驶": "浩瀚智驾2.0"
        },
        competitors=["特斯拉Model 3", "小米SU7", "比亚迪海豹", "极氪007"],
        sales_talk={
            "开场": "007是极氪最亲民的中型纯电轿车，入门即豪华",
            "性价比": "20万出头就能买到800V平台，性能却超越同价燃油钢炮",
            "科技": "8295芯片+97寸AR-HUD，科技感拉满",
            "续航": "入门版605km，长续航版870km，满足一周通勤",
            "补能": "800V快充15分钟补能500km，喝杯咖啡的时间"
        },
        use_scenes=["城市通勤", "周末自驾", "年轻人第一台电车", "网约车"],
        image=os.path.join(ASSETS_DIR, "zeekr_007.jpg")
    ),
    
    "ZEEKR X": CarModel(
        name="ZEEKR X",
        price="18.98-22.98万",
        category="新奢全能SUV",
        target_customer=["女性车主", "单身贵族", "城市精致生活", "新手司机"],
        highlights=[
            "3.7秒百公里加速",
            "小巧灵活车身",
            "百变空间",
            "零重力座椅",
            "14.6寸电动滑移屏"
        ],
        specs={
            "长宽高": "4450×1836×1572mm",
            "轴距": "2750mm",
            "电机功率": "315kW",
            "电池容量": "66kWh",
            "续航": "512-560km CLTC",
            "快充时间": "29分钟(10%-80%)"
        },
        competitors=["smart精灵#1", "比亚迪海豚", "欧拉好猫", "大众ID.3"],
        sales_talk={
            "开场": "X是极氪最精致的都市SUV，小巧但气场十足",
            "外观": "都市四驱版有Brembo刹车+19寸轮毂，颜值即正义",
            "空间": "2750mm轴距营造超大空间，后排放倒可当床",
            "灵活": "5.5米转弯半径，窄路掉头一把过",
            "安全": "Euro NCAP五星安全认证，主动安全领先"
        },
        use_scenes=["闺蜜出行", "购物代步", "新手练车", "周末遛娃"],
        image=os.path.join(ASSETS_DIR, "zeekr_x.jpg")
    ),
    
    "ZEEKR 009": CarModel(
        name="ZEEKR 009",
        price="50-58万",
        category="豪华纯电MPV",
        target_customer=["企业高管", "多孩家庭", "追求舒适", "商务接待"],
        highlights=[
            "4.5秒百公里加速",
            "空气悬架+CDC",
            "Sofaro头等舱座椅",
            "15.6寸后排娱乐屏",
            "零重力座椅"
        ],
        specs={
            "长宽高": "5209×2024×1856mm",
            "轴距": "3205mm",
            "电机功率": "400kW",
            "电池容量": "116kWh/140kWh",
            "续航": "702-822km CLTC",
            "座椅": "6座/4座"
        },
        competitors=["腾势D9", "岚图梦想家", "理想MEGA", "别克GL8"],
        sales_talk={
            "开场": "009重新定义了豪华MPV，开它出去老板都夸你有品味",
            "性能": "MPV也能3秒级加速，驾驶乐趣与乘坐舒适兼得",
            "座椅": "Sofaro零重力座椅，按摩加热通风一应俱全",
            "空间": "3205mm超长轴距，三排空间比埃尔法还大",
            "隐私": "后排玻璃私密设计，配小桌板办公舒适"
        },
        use_scenes=["商务接待", "机场接送", "家庭出游", "保姆车"],
        image=os.path.join(ASSETS_DIR, "zeekr_009.jpg")
    ),
    
    "ZEEKR 7X": CarModel(
        name="ZEEKR 7X",
        price="22.99-26.99万",
        category="纯电中型SUV",
        target_customer=["家庭用户", "增购换购", "智能科技爱好者", "安全至上用户"],
        highlights=[
            "3.8秒百公里加速",
            "浩瀚智驾2.0",
            "8295芯片",
            "超600km续航",
            "激光雷达标配"
        ],
        specs={
            "长宽高": "4820×1930×1660mm",
            "轴距": "2925mm",
            "电机功率": "475kW(四驱)",
            "电池容量": "75kWh/100kWh",
            "续航": "605-780km CLTC",
            "快充时间": "15分钟(10%-80%)"
        },
        competitors=["特斯拉Model Y", "小鹏G6", "问界M5", "蔚来ES6"],
        sales_talk={
            "开场": "7X是极氪最新推出的全能SUV，一台车满足全家需求",
            "安全": "标配激光雷达，主动安全领先同级，全家出行更安心",
            "空间": "2925mm轴距超大空间，六座布局灵活多变",
            "智能": "8295芯片+浩瀚智驾2.0，智能座舱天花板",
            "续航": "最长780km续航，一周通勤不用充电"
        },
        use_scenes=["家庭出行", "周末郊游", "日常通勤", "长途自驾"],
        image=os.path.join(ASSETS_DIR, "zeekr_7x.jpg")
    ),
    
    "ZEEKR 001 FR": CarModel(
        name="ZEEKR 001 FR",
        price="76.9万",
        category="纯电猎装超跑",
        target_customer=["性能玩家", "超跑爱好者", "社交达人", "赛道爱好者"],
        highlights=[
            "1.8秒破百",
            "四电机1265kW",
            "碳纤维外观套件",
            "Brembo碳陶刹车",
            "KW绞牙悬架"
        ],
        specs={
            "长宽高": "5018×1999×1545mm",
            "轴距": "3005mm",
            "电机功率": "1265kW(四电机)",
            "电池容量": "100kWh",
            "续航": "550km CLTC",
            "极速": "280km/h"
        },
        competitors=["特斯拉Model S Plaid", "保时捷Taycan Turbo S", "小米SU7 Ultra"],
        sales_talk={
            "开场": "001 FR是中国品牌加速最快的量产车，76万买千万级性能",
            "加速": "1.8秒破百，比法拉利458还快一代",
            "四电机": "四个电机独立控制扭矩，操控极限极高",
            "赛道": "原厂就能下赛道，KW绞牙+碳陶刹车上车",
            "稀有": "每月限量99台，开出去绝对不撞款"
        },
        use_scenes=["赛道日", "社交炸街", "性能收藏", "体验极致"],
        image=os.path.join(ASSETS_DIR, "zeekr_fr.jpg")
    )
}

# ============================================================
# 客户画像
# ============================================================

CUSTOMER_PROFILES = {
    "科技极客": {
        "特征": ["追求最新科技", "参数控", "喜欢对比测评", "愿意为新技术买单"],
        "推荐车型": ["ZEEKR 001", "ZEEKR 007", "ZEEKR 001 FR"],
        "话术重点": ["8295芯片", "浩瀚架构", "OTA升级", "加速性能"]
    },
    "家庭用户": {
        "特征": ["有孩子", "重视安全", "空间需求大", "考虑全家出行"],
        "推荐车型": ["ZEEKR 009", "ZEEKR 001", "ZEEKR 007"],
        "话术重点": ["空间大", "安全配置", "续航长", "舒适性"]
    },
    "商务精英": {
        "特征": ["企业高管", "注重形象", "经常接待", "时间宝贵"],
        "推荐车型": ["ZEEKR 009", "ZEEKR 001"],
        "话术重点": ["豪华感", "品牌调性", "乘坐舒适", "静音效果好"]
    },
    "年轻首购": {
        "特征": ["25-30岁", "首台车", "预算有限", "追求性价比"],
        "推荐车型": ["ZEEKR 007", "ZEEKR X"],
        "话术重点": ["价格亲民", "用车成本低", "颜值高", "好停车"]
    },
    "女性车主": {
        "特征": ["注重外观", "驾驶技术一般", "城市用车为主", "喜欢精致"],
        "推荐车型": ["ZEEKR X", "ZEEKR 007"],
        "话术重点": ["颜值高", "好停车", "安全配置", "内饰精致"]
    },
    "性能玩家": {
        "特征": ["喜欢驾驶", "下赛道", "社交分享", "追求极致"],
        "推荐车型": ["ZEEKR 001 FR", "ZEEKR 001"],
        "话术重点": ["加速快", "操控好", "赛道成绩", "稀有度"]
    }
}

# ============================================================
# 知识图谱构建
# ============================================================

def build_knowledge_graph():
    """构建ZEEKR车型知识图谱"""
    G = nx.DiGraph()
    
    # 添加车型节点
    for model_name, model in ZEEKR_MODELS.items():
        G.add_node(model_name, type="车型", **model.__dict__)
        
        # 添加卖点节点
        for highlight in model.highlights:
            G.add_node(f"{model_name}_{highlight}", type="卖点", value=highlight)
            G.add_edge(model_name, f"{model_name}_{highlight}", relation="拥有")
        
        # 添加目标客户节点
        for customer in model.target_customer:
            if customer not in G:
                G.add_node(customer, type="客户画像")
            G.add_edge(model_name, customer, relation="目标客户")
        
        # 添加竞品节点
        for comp in model.competitors:
            if comp not in G:
                G.add_node(comp, type="竞品")
            G.add_edge(model_name, comp, relation="竞品对比")
        
        # 添加使用场景
        for scene in model.use_scenes:
            if scene not in G:
                G.add_node(scene, type="使用场景")
            G.add_edge(model_name, scene, relation="适用场景")
    
    # 添加客户画像节点
    for profile_name, profile in CUSTOMER_PROFILES.items():
        G.add_node(profile_name, type="客户画像", **profile)
    
    return G

# ============================================================
# 推荐引擎
# ============================================================

class CarRecommender:
    """车型推荐引擎"""
    
    def __init__(self):
        self.models = ZEEKR_MODELS
        self.profiles = CUSTOMER_PROFILES
        self.graph = build_knowledge_graph()
    
    def recommend_by_customer(self, customer_type: str) -> List[Dict]:
        """根据客户类型推荐"""
        if customer_type not in self.profiles:
            return []
        
        profile = self.profiles[customer_type]
        recommendations = []
        
        for model_name in profile["推荐车型"]:
            if model_name in self.models:
                model = self.models[model_name]
                recommendations.append({
                    "车型": model.name,
                    "价格": model.price,
                    "类别": model.category,
                    "核心卖点": ", ".join(model.highlights[:3]),
                    "匹配话术": profile["话术重点"]
                })
        
        return recommendations
    
    def recommend_by_budget(self, budget_min: int, budget_max: int) -> List[Dict]:
        """根据预算推荐"""
        # 简化逻辑，实际应该解析价格字符串
        all_recommendations = []
        for model_name, model in self.models.items():
            # 提取最低价格（万）
            try:
                price_str = model.price.split("-")[0].replace("万", "")
                price = float(price_str)
                if budget_min <= price <= budget_max:
                    all_recommendations.append({
                        "车型": model.name,
                        "价格": model.price,
                        "类别": model.category,
                        "核心卖点": ", ".join(model.highlights[:3])
                    })
            except:
                continue
        
        return all_recommendations
    
    def recommend_by_scene(self, scene: str) -> List[Dict]:
        """根据使用场景推荐"""
        recommendations = []
        for model_name, model in self.models.items():
            if scene in model.use_scenes:
                recommendations.append({
                    "车型": model.name,
                    "价格": model.price,
                    "类别": model.category,
                    "核心卖点": ", ".join(model.highlights[:3]),
                    "场景话术": model.sales_talk.get("开场", "")
                })
        return recommendations
    
    def get_sales_talk(self, model_name: str, angle: str = "开场") -> str:
        """获取销售话术"""
        if model_name not in self.models:
            return "未找到该车型"
        return self.models[model_name].sales_talk.get(angle, "")
    
    def compare_models(self, model1: str, model2: str) -> Dict:
        """竞品对比"""
        if model1 not in self.models or model2 not in self.models:
            return {}
        
        m1 = self.models[model1]
        m2 = self.models[model2]
        
        return {
            "车型1": {"名称": m1.name, "价格": m1.price, "类别": m1.category},
            "车型2": {"名称": m2.name, "价格": m2.price, "类别": m2.category},
            "各自优势": {
                m1.name: m1.highlights,
                m2.name: m2.highlights
            }
        }


if __name__ == "__main__":
    recommender = CarRecommender()
    
    # 测试推荐
    print("=== 按客户类型推荐 ===")
    for rec in recommender.recommend_by_customer("年轻首购"):
        print(rec)
    
    print("\n=== 按使用场景推荐 ===")
    for rec in recommender.recommend_by_scene("周末自驾"):
        print(rec)
