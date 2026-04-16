"""
极氪智能卖车助手 v3
新增功能：
- 购车计算器（月供、首付）
- 配置选择器
- 竞品对比
- 多轮对话上下文
- 试驾预约表单
"""
import os
from pathlib import Path
from typing import List, Dict, Optional
import random

# 图片目录
ZEEKR_IMAGES = {
    "ZEEKR 001": [
        "e:/pyspace/zeeker/assets/zeekr_001.jpg",
        "e:/pyspace/joker/zeeker/官网图片_已清洗/极氪001/极氪001_1.jpg",
        "e:/pyspace/joker/zeeker/官网图片_已清洗/极氪001/极氪001_2.jpg",
        "e:/pyspace/zeeker/assets/autohome/zeekr_001/zeekr_001_autohome_01.png",
        "e:/pyspace/zeeker/assets/autohome/zeekr_001/zeekr_001_autohome_02.png",
        "e:/pyspace/zeeker/assets/autohome/zeekr_001/zeekr_001_autohome_03.png",
    ],
    "ZEEKR 007": [
        "e:/pyspace/zeeker/assets/zeekr_007.jpg",
        "e:/pyspace/joker/zeeker/官网图片_已清洗/极氪007/极氪007_1.png",
        "e:/pyspace/joker/zeeker/官网图片_已清洗/极氪007/极氪007_2.png",
        "e:/pyspace/zeeker/assets/autohome/zeekr_007/zeekr_007_autohome_01.jpg",
        "e:/pyspace/zeeker/assets/autohome/zeekr_007/zeekr_007_autohome_02.jpg",
    ],
    "ZEEKR X": [
        "e:/pyspace/zeeker/assets/zeekr_x.jpg",
        "e:/pyspace/joker/zeeker/官网图片_已清洗/极氪X/极氪X_3.jpg",
        "e:/pyspace/joker/zeeker/官网图片_已清洗/极氪X/极氪X_4.jpg",
        "e:/pyspace/zeeker/assets/autohome/zeekr_X/zeekr_X_autohome_01.jpg",
    ],
    "ZEEKR 009": [
        "e:/pyspace/zeeker/assets/zeekr_009.jpg",
        "e:/pyspace/joker/zeeker/官网图片_已清洗/极氪009/极氪009_1.png",
        "e:/pyspace/joker/zeeker/官网图片_已清洗/极氪009/极氪009_2.png",
        "e:/pyspace/zeeker/assets/autohome/zeekr_009/zeekr_009_autohome_01.jpg",
        "e:/pyspace/zeeker/assets/autohome/zeekr_009/zeekr_009_autohome_02.jpg",
    ],
    "ZEEKR 7X": [
        "e:/pyspace/zeeker/assets/zeekr_7x.jpg",
        "e:/pyspace/joker/zeeker/官网图片_已清洗/极氪7X/极氪7X_3.jpg",
        "e:/pyspace/zeeker/assets/autohome/zeekr_7X/zeekr_7X_autohome_01.jpg",
    ],
    "ZEEKR 001 FR": [
        "e:/pyspace/zeeker/assets/zeekr_fr.jpg",
    ]
}

# 车型详细数据（含配置）
CAR_DATA = {
    "ZEEKR 001": {
        "价格": "26.9-76.9万",
        "价格区间": [26.9, 76.9],
        "类型": "纯电猎装轿跑",
        "级别": "中大型车",
        "续航": "712-1032km CLTC",
        "加速": "3.8秒破百",
        "特点": ["猎装造型", "3.8秒破百", "空气悬架", "雅马哈音响", "浩瀚智驾2.0"],
        "适合": ["追求个性", "驾驶乐趣", "家庭使用", "科技玩家"],
        "竞品": ["特斯拉Model 3", "蔚来ET7", "小米SU7"],
        "配置列表": [
            {"名称": "YOU版 100kWh", "价格": 29.9, "特点": "100度电池，续航741km"},
            {"名称": "ME版 100kWh", "价格": 31.9, "特点": "空气悬架，CCD电磁减震"},
            {"名称": "WE版 86kWh", "价格": 26.9, "特点": "入门首选，城市通勤"},
            {"名称": "FR版", "价格": 76.9, "特点": "四电机，2.02秒破百，赛道利器"},
        ],
        "颜色": ["极昼白", "极夜黑", "电光蓝", "镭射灰", "碳素黑"],
        "内饰颜色": ["怀旧岩灰", "氮蓝", "铂尊棕", "撞色（蓝白）"],
    },
    "ZEEKR 007": {
        "价格": "20.99-29.99万",
        "价格区间": [20.99, 29.99],
        "类型": "纯电轿车",
        "级别": "中型车",
        "续航": "688-870km CLTC",
        "加速": "2.84秒破百（四驱性能版）",
        "特点": ["星际之门灯幕", "8295芯片", "激光雷达", "最长870km续航"],
        "适合": ["科技玩家", "城市通勤", "年轻人第一台电车"],
        "竞品": ["特斯拉Model 3", "小米SU7", "小鹏P7"],
        "配置列表": [
            {"名称": "后驱增强版", "价格": 20.99, "特点": "城市通勤首选"},
            {"名称": "四驱性能版", "价格": 29.99, "特点": "2.84秒破百，极致性能"},
            {"名称": "后驱长续航版", "价格": 23.99, "特点": "870km超长续航"},
        ],
        "颜色": ["曙光棕", "极夜蓝", "烟雨灰", "皎月白", "星暮紫"],
        "内饰颜色": ["深月灰", "纯氧蓝", "日升米"],
    },
    "ZEEKR X": {
        "价格": "16.98-19.98万",
        "价格区间": [16.98, 19.98],
        "类型": "新奢SUV",
        "级别": "小型SUV",
        "续航": "512-560km CLTC",
        "加速": "5.6秒破百",
        "特点": ["小巧灵活", "对开式车门", "4座布局", "适合城市", "魔方座椅"],
        "适合": ["女性用户", "新手司机", "城市代步", "家庭第二台车"],
        "竞品": ["Smart精灵#1", "欧拉芭蕾猫", "比亚迪海豚"],
        "配置列表": [
            {"名称": "ME版五座", "价格": 16.98, "特点": "五座实用版"},
            {"名称": "YOU版四座", "价格": 18.98, "特点": "对开式车门，4座新奢"},
            {"名称": "LS版", "价格": 19.98, "特点": "顶配，舒适配置拉满"},
        ],
        "颜色": ["巴黎米", "洛杉矶粉", "悉尼蓝", "柏林银", "东京红"],
        "内饰颜色": ["氮蓝", "铂银", "洛依花紫"],
    },
    "ZEEKR 009": {
        "价格": "50-78万",
        "价格区间": [50.0, 78.0],
        "类型": "豪华MPV",
        "级别": "中大型MPV",
        "续航": "702-822km CLTC",
        "加速": "4.5秒破百",
        "特点": ["六座/四座", "NAPPA真皮", "小桌板+屏幕", "气场强大", "零重力座椅"],
        "适合": ["商务接待", "家庭出行", "保姆车", "公司用车"],
        "竞品": ["丰田埃尔法", "腾势D9", "理想MEGA", "岚图梦想家"],
        "配置列表": [
            {"名称": "WE版六座", "价格": 50.0, "特点": "入门即豪华"},
            {"名称": "ME版六座", "价格": 58.8, "特点": "140度电池，超长续航"},
            {"名称": "YOU版四座", "价格": 78.0, "特点": "旗舰四座，极致豪华"},
        ],
        "颜色": ["极昼白", "极夜黑", "霞光紫", "星辰银"],
        "内饰颜色": ["白金蓝", "全粒面真皮"],
    },
    "ZEEKR 7X": {
        "价格": "22.99-26.99万",
        "价格区间": [22.99, 26.99],
        "类型": "纯电中型SUV",
        "级别": "中型SUV",
        "续航": "605-780km CLTC",
        "加速": "3.8秒破百",
        "特点": ["家用首选", "浩瀚智驾2.0", "8295芯片", "超600km续航", "安全堡垒"],
        "适合": ["家庭用户", "增购换购", "安全至上", "全能家用"],
        "竞品": ["特斯拉Model Y", "小鹏G6", "问界M5", "比亚迪唐EV"],
        "配置列表": [
            {"名称": "75kWh后驱", "价格": 22.99, "特点": "家用入门首选"},
            {"名称": "100kWh后驱", "价格": 24.99, "特点": "780km超长续航"},
            {"名称": "100kWh四驱", "价格": 26.99, "特点": "3.8秒破百，性能强劲"},
        ],
        "颜色": ["极昼白", "极夜黑", "浮光蓝", "星暮金", "暮光紫"],
        "内饰颜色": ["怀旧灰", "纯氧蓝", "黑檀木"],
    },
    "ZEEKR 001 FR": {
        "价格": "76.9万起",
        "价格区间": [76.9, 76.9],
        "类型": "纯电超跑",
        "级别": "性能超跑",
        "续航": "550km CLTC",
        "加速": "2.02秒破百",
        "特点": ["四电机", "碳陶刹车", "赛道利器", "F1冠军调校"],
        "适合": ["性能发烧友", "追求极致", "赛道日玩家"],
        "竞品": ["特斯拉Model S Plaid", "保时捷Taycan Turbo S"],
        "配置列表": [
            {"名称": "FR版", "价格": 76.9, "特点": "出厂即巅峰"},
        ],
        "颜色": ["竞速橙", "性能银", "碳纤维裸漆"],
        "内饰颜色": ["Alcantara竞速内饰"],
    },
    "尊界 S800": {
        "价格": "70.8-101.8万",
        "价格区间": [70.8, 101.8],
        "类型": "超豪华智能轿车",
        "级别": "大型车",
        "续航": "纯电版702km / 增程版",
        "加速": "3.9秒破百",
        "特点": ["途灵龙行平台", "七项智能化技术", "天使轮主动安全", "横着走", "华为赋能", "自主智能天花版"],
        "适合": ["顶级商务", "成功人士", "追求极致科技", "国产超豪华"],
        "竞品": ["迈巴赫S级", "劳斯莱斯古斯特", "宾利飞驰"],
        "配置列表": [
            {"名称": "纯电 Ultra", "价格": 70.8, "特点": "纯电旗舰入门"},
            {"名称": "增程 Ultra", "价格": 70.8, "特点": "增程版可油可电"},
            {"名称": "增程 Art", "价格": 80.8, "特点": "艺术设计语言"},
            {"名称": "增程 Ultra 典藏版", "价格": 101.8, "特点": "顶配旗舰极致奢华"},
        ],
        "颜色": ["星耀黑", "曙光金", "星辰紫", "云白色"],
        "内饰颜色": ["夜阑墨棕+哑光胡桃木", "煦日浅棕+哑光胡桃木"],
    }
}

# 竞品对比数据
COMPETITORS = {
    "特斯拉Model 3": {
        "价格": "24.59-28.59万",
        "续航": "606-713km",
        "加速": "3.3-4.4秒",
        "优势": ["品牌力强", "充电网络完善", "自动驾驶领先"],
        "劣势": ["内饰简约", "隔音一般", "售后服务争议"]
    },
    "特斯拉Model Y": {
        "价格": "26.39-35.99万",
        "续航": "554-688km",
        "加速": "3.7-5秒",
        "优势": ["销量王者", "空间大", "充电网络"],
        "劣势": ["内饰简陋", "座椅偏硬", "等车久"]
    },
    "蔚来ET7": {
        "价格": "42.8-51.6万",
        "续航": "530-665km",
        "加速": "3.8秒",
        "优势": ["换电方便", "服务好", "内饰豪华"],
        "劣势": ["价格偏高", "能耗较高", "品牌小众"]
    },
    "小米SU7": {
        "价格": "21.59-29.99万",
        "续航": "700-830km",
        "加速": "2.78-5.28秒",
        "优势": ["生态联动好", "外观漂亮", "性价比高"],
        "劣势": ["新品牌", "交付压力大", "售后网络待完善"]
    },
    "小鹏P7": {
        "价格": "20.99-33.99万",
        "续航": "550-702km",
        "加速": "4.3-6.4秒",
        "优势": ["智驾领先", "性价比高", "外观好看"],
        "劣势": ["品牌力弱", "服务网点少", "做工一般"]
    },
    "比亚迪汉": {
        "价格": "16.98-29.98万",
        "续航": "506-715km",
        "加速": "3.9-7.9秒",
        "优势": ["性价比高", "质量可靠", "售后网络广"],
        "劣势": ["智驾一般", "品牌定位", "设计保守"]
    },
}

def get_car_images(car_name: str, count: int = 4) -> List[str]:
    """获取车型的可用图片"""
    images = ZEEKR_IMAGES.get(car_name, [])
    valid_images = [img for img in images if Path(img).exists()]
    if valid_images:
        return random.sample(valid_images, min(count, len(valid_images)))
    return []

def calculate_monthly_payment(principal: float, years: int, rate: float = 0.035) -> float:
    """计算月供"""
    monthly_rate = rate / 12
    months = years * 12
    if monthly_rate == 0:
        return principal / months
    payment = principal * monthly_rate * (1 + monthly_rate) ** months / ((1 + monthly_rate) ** months - 1)
    return round(payment, 2)

def format_price(price: float) -> str:
    """格式化价格显示"""
    if price >= 100:
        return f"{price:.0f}万"
    else:
        return f"{price:.2f}万"

class SalesAssistant:
    """极氪智能卖车助手 v3 - 豆包风格"""
    
    def __init__(self):
        self.context = {
            "mentioned_cars": [],
            "current_car": None,
            "conversation_history": [],
            "detected_need": None,
            "user_profile": {},
        }
        
        # 意图识别关键词
        self.intents = {
            "车型咨询": ["有什么车", "有哪些", "车型", "看看", "全部", "全部车型"],
            "价格咨询": ["多少钱", "价格", "报价", "预算", "落地", "首付", "月供"],
            "配置咨询": ["配置", "选哪个", "怎么选", "有什么区别"],
            "颜色咨询": ["颜色", "有哪些颜色", "什么颜色好看"],
            "对比咨询": ["和", "比", "区别", "哪个好", "差异", "对比", "竞品"],
            "家用推荐": ["家里", "有孩子", "小孩", "全家", "家用", "带娃", "家庭"],
            "商务推荐": ["商务", "接待", "老板", "谈生意", "公司", "商务接待"],
            "科技推荐": ["科技", "智能", "自动驾驶", "大屏", "ota", "芯片"],
            "性能推荐": ["快", "加速", "动力", "飙车", "驾驶", "性能", "飙"],
            "女性推荐": ["女", "老婆", "好停", "简单", "操作", "小巧", "女性"],
            "续航咨询": ["续航", "充电", "里程", "电池", "快充", "能跑多远"],
            "内饰咨询": ["内饰", "座椅", "方向盘", "里面"],
            "外观咨询": ["外观", "好看", "漂亮", "颜值", "设计"],
            "试驾预约": ["试驾", "体验", "试试", "预约", "到店"],
            "购车计算": ["计算", "月供", "首付", "贷款", "算一下"],
            "确认购车": ["定了", "就买这个", "订车", "购买", "下单"],
            "感谢告别": ["谢谢", "好的", "再见", "拜拜", "了解了"],
        }
        
        # 需求到车型的映射
        self.need_to_cars = {
            "家用推荐": ["ZEEKR 7X", "ZEEKR 009", "ZEEKR 001"],
            "商务推荐": ["ZEEKR 009", "ZEEKR 001", "ZEEKR 007"],
            "科技推荐": ["ZEEKR 007", "ZEEKR 7X", "ZEEKR 001 FR"],
            "性能推荐": ["ZEEKR 001 FR", "ZEEKR 001", "ZEEKR 007"],
            "女性推荐": ["ZEEKR X", "ZEEKR 007", "ZEEKR 7X"],
        }
        
        # 竞品关键词映射
        self.competitor_keywords = {
            "特斯拉": ["特斯拉", "model 3", "model y", "model s", "model x"],
            "蔚来": ["蔚来", "et5", "et7", "es6", "es8"],
            "小鹏": ["小鹏", "p7", "p5", "g6", "g9"],
            "小米": ["小米", "su7", "su"],
            "比亚迪": ["比亚迪", "汉", "唐", "海豹"],
            "理想": ["理想", "l7", "l8", "l9", "mega"],
            "问界": ["问界", "m5", "m7", "m9"],
            "腾势": ["腾势", "d9", "n7", "n8"],
        }
    
    def detect_intent(self, text: str) -> List[str]:
        """识别用户意图"""
        text_lower = text.lower()
        detected = []
        for intent, keywords in self.intents.items():
            if any(kw in text_lower for kw in keywords):
                detected.append(intent)
        if not detected:
            detected = ["通用咨询"]
        return detected
    
    def detect_car(self, text: str) -> Optional[str]:
        """识别提到的车型"""
        text_lower = text.lower()
        car_mapping = {
            "001": "ZEEKR 001",
            "007": "ZEEKR 007", 
            "x": "ZEEKR X",
            "7x": "ZEEKR 7X",
            "009": "ZEEKR 009",
            "fr": "ZEEKR 001 FR",
            "极氪001": "ZEEKR 001",
            "极氪007": "ZEEKR 007",
            "极氪x": "ZEEKR X",
            "极氪7x": "ZEEKR 7X",
            "极氪009": "ZEEKR 009",
            "极氪001fr": "ZEEKR 001 FR",
        }
        for keyword, car in car_mapping.items():
            if keyword in text_lower:
                return car
        return None
    
    def detect_competitor(self, text: str) -> Optional[str]:
        """识别竞品"""
        text_lower = text.lower()
        for brand, keywords in self.competitor_keywords.items():
            if any(kw in text_lower for kw in keywords):
                # 匹配具体车型
                for competitor in COMPETITORS.keys():
                    if competitor.lower() in text_lower:
                        return competitor
                    if brand.lower() in text_lower:
                        return competitor
        return None
    
    def detect_need(self, text: str) -> Optional[str]:
        """识别需求类型"""
        text_lower = text.lower()
        needs = {
            "家用": ["家里", "孩子", "小孩", "家用", "家庭", "带娃", "空间大"],
            "商务": ["商务", "接待", "老板", "谈生意", "公司"],
            "科技": ["科技", "智能", "自动驾驶", "ota", "芯片"],
            "性能": ["快", "加速", "动力", "性能", "飙车", "驾驶"],
            "女性": ["女", "老婆", "好停", "小巧", "简单操作"],
            "续航": ["续航", "里程", "充电", "电池"],
        }
        for need, keywords in needs.items():
            if any(k in text_lower for k in keywords):
                return need
        return None
    
    def generate_response(self, user_input: str) -> Dict:
        """生成回复 - 豆包风格"""
        intents = self.detect_intent(user_input)
        detected_car = self.detect_car(user_input)
        detected_need = self.detect_need(user_input)
        
        response = {
            "text": "",
            "images": [],
            "suggestions": [],
            "action": None  # 用于触发特殊组件
        }
        
        # 记录对话历史
        self.context["conversation_history"].append(user_input)
        
        # 更新当前车型
        if detected_car:
            self.context["current_car"] = detected_car
            if detected_car not in self.context["mentioned_cars"]:
                self.context["mentioned_cars"].append(detected_car)
        
        # 记录需求
        if detected_need:
            self.context["detected_need"] = detected_need
        
        # 路由处理 - 优先级从高到低
        if any(i in intents for i in ["确认购车", "感谢告别"]):
            response = self._handle_farewell()
        elif any(i in intents for i in ["试驾预约"]):
            response = self._handle_test_drive()
        elif any(i in intents for i in ["购车计算"]):
            response = self._handle_calculator()
        elif any(i in intents for i in ["对比咨询"]):
            response = self._handle_compare()
        elif any(i in intents for i in ["颜色咨询"]):
            response = self._handle_color()
        elif any(i in intents for i in ["配置咨询"]):
            response = self._handle_config()
        elif any(i in intents for i in ["价格咨询"]):
            response = self._handle_price()
        elif any(i in intents for i in ["内饰咨询"]):
            response = self._handle_interior()
        elif any(i in intents for i in ["外观咨询"]):
            response = self._handle_exterior()
        elif any(i in intents for i in ["续航咨询"]):
            response = self._handle_battery()
        elif any(i in intents for i in ["家用推荐"]):
            response = self._handle_recommend("家用推荐", "ZEEKR 7X")
        elif any(i in intents for i in ["商务推荐"]):
            response = self._handle_recommend("商务推荐", "ZEEKR 009")
        elif any(i in intents for i in ["科技推荐"]):
            response = self._handle_recommend("科技推荐", "ZEEKR 007")
        elif any(i in intents for i in ["性能推荐"]):
            response = self._handle_recommend("性能推荐", "ZEEKR 001 FR")
        elif any(i in intents for i in ["女性推荐"]):
            response = self._handle_recommend("女性推荐", "ZEEKR X")
        elif any(i in intents for i in ["车型咨询"]):
            response = self._handle_explore()
        else:
            response = self._handle_general()
        
        return response
    
    def _handle_explore(self) -> Dict:
        """处理车型了解请求"""
        cars = list(CAR_DATA.keys())
        intro = "极氪目前有 **6款** 在售车型：\n\n"
        
        for i, car in enumerate(cars, 1):
            data = CAR_DATA[car]
            intro += f"{i}. **{car}** - {data['类型']}（{data['价格']}）\n"
            intro += f"   亮点: {', '.join(data['特点'][:2])}\n\n"
        
        intro += "请问您对哪款感兴趣？或者告诉我您的购车需求，我帮您推荐～"
        
        # 展示一组车型图片
        images = []
        for car in ["ZEEKR 007", "ZEEKR 7X", "ZEEKR 009", "ZEEKR 001"]:
            images.extend(get_car_images(car, 1))
        
        return {
            "text": intro,
            "images": images[:4],
            "suggestions": ["我想买家用车", "适合商务接待的", "科技感强的推荐", "价格多少"]
        }
    
    def _handle_recommend(self, need: str, car: str) -> Dict:
        """处理推荐请求"""
        data = CAR_DATA[car]
        images = get_car_images(car, 4)
        
        # 根据需求定制话术
        need_messages = {
            "家用推荐": f"家庭用车最重要的就是安全和大空间，我强烈推荐 **{car}**！",
            "商务推荐": f"商务接待需要气场和舒适度，**{car}** 是这个价位的最佳选择！",
            "科技推荐": f"追求科技感的话，**{car}** 的智能化配置绝对不会让您失望！",
            "性能推荐": f"想要极致性能？**{car}** 的加速体验堪称同级别天花板！",
            "女性推荐": f"女士开车最重要的是好停、好开、好看，**{car}** 完全满足！",
        }
        
        text = need_messages.get(need, f"根据您的需求，我推荐 **{car}**！\n\n")
        text += f"**{data['类型']}** | {data['价格']}\n\n"
        text += "**核心亮点：**\n"
        for h in data['特点']:
            text += f"- {h}\n"
        text += "\n**非常适合：**" + " | ".join(data['适合']) + "\n\n"
        text += "我给您展示一下这台车："
        
        return {
            "text": text,
            "images": images,
            "suggestions": [
                f"看看配置怎么选",
                "有哪些颜色",
                "算一下月供",
                "能试驾吗"
            ]
        }
    
    def _handle_price(self) -> Dict:
        """处理价格咨询"""
        car = self.context.get("current_car") or "ZEEKR 007"
        data = CAR_DATA.get(car, {})
        configs = data.get("配置列表", [])
        
        text = f"**{car}** 的价格：\n\n"
        
        if configs:
            text += "**在售配置：**\n"
            for cfg in configs:
                text += f"- **{cfg['名称']}**: {format_price(cfg['价格'])}万\n"
                text += f"  {cfg['特点']}\n"
        
        text += "\n**价格包含：**\n"
        text += "- 裸车价格\n"
        text += "- 免购置税（国家政策）\n"
        text += "- 免费安装充电桩\n"
        text += "- 基础保养\n\n"
        text += "想知道具体月供多少吗？我可以帮您计算！"
        
        images = get_car_images(car, 2)
        
        return {
            "text": text,
            "images": images,
            "suggestions": ["算一下月供", "看看配置怎么选", "有哪些颜色", "和竞品比怎么样"]
        }
    
    def _handle_config(self) -> Dict:
        """处理配置咨询"""
        car = self.context.get("current_car") or "ZEEKR 007"
        data = CAR_DATA.get(car, {})
        configs = data.get("配置列表", [])
        
        if not configs:
            return {
                "text": f"**{car}** 目前配置较少，建议到店详询。",
                "images": get_car_images(car, 2),
                "suggestions": ["看看其他车型", "价格多少", "能试驾吗"]
            }
        
        text = f"**{car}** 配置选择指南：\n\n"
        
        for i, cfg in enumerate(configs, 1):
            text += f"**{i}. {cfg['名称']}** - {format_price(cfg['价格'])}万\n"
            text += f"   {cfg['特点']}\n\n"
        
        # 根据上下文推荐
        if self.context.get("detected_need") == "家用":
            text += "💡 **推荐**：如果是家用的话，100度电池版本续航更长，一周充一次就够了。"
        elif self.context.get("detected_need") == "性能":
            text += "💡 **推荐**：追求性能的话首选四驱版本，3.8秒破百的加速体验绝对让您满意！"
        else:
            text += "💡 **推荐**：入门版配置已经很丰富了，如果不是特别追求续航或性能，入门版性价比最高。"
        
        images = get_car_images(car, 2)
        
        return {
            "text": text,
            "images": images,
            "suggestions": ["算一下月供", "有哪些颜色", "和竞品比怎么样", "能试驾吗"]
        }
    
    def _handle_color(self) -> Dict:
        """处理颜色咨询"""
        car = self.context.get("current_car") or "ZEEKR 007"
        data = CAR_DATA.get(car, {})
        colors = data.get("颜色", [])
        interior_colors = data.get("内饰颜色", [])
        
        text = f"**{car}** 可选颜色：\n\n"
        text += "**外观颜色：**\n"
        for color in colors:
            text += f"- {color}\n"
        
        text += "\n**内饰颜色：**\n"
        for color in interior_colors:
            text += f"- {color}\n"
        
        # 根据用户画像推荐颜色
        if self.context.get("detected_need") == "商务":
            text += "\n💡 **推荐**：商务接待建议选择 **极昼白** 或 **极夜黑**，经典大气。"
        elif self.context.get("detected_need") == "女性":
            text += "\n💡 **推荐**：女士开车的话，**洛杉矶粉** 或 **极昼白** 都很受欢迎。"
        else:
            text += "\n💡 **推荐**：白色和黑色是最保值的颜色，以后换车不亏。"
        
        images = get_car_images(car, 2)
        
        return {
            "text": text,
            "images": images,
            "suggestions": ["看看配置怎么选", "算一下落地价", "能试驾吗", "和竞品比怎么样"]
        }
    
    def _handle_calculator(self) -> Dict:
        """处理购车计算"""
        car = self.context.get("current_car") or "ZEEKR 007"
        data = CAR_DATA.get(car, {})
        price_range = data.get("价格区间", [20, 30])
        base_price = (price_range[0] + price_range[1]) / 2
        
        text = f"**{car}** 购车费用计算（按中配估算）\n\n"
        text += f"**指导价**: {format_price(base_price)}万\n\n"
        
        # 首付30%
        down_payment_30 = base_price * 0.3
        text += f"📌 **首付30%**: {format_price(down_payment_30)}万\n"
        monthly_3y = calculate_monthly_payment(base_price - down_payment_30, 3)
        monthly_5y = calculate_monthly_payment(base_price - down_payment_30, 5)
        text += f"   - 3年月供: {format_price(monthly_3y)}万/月\n"
        text += f"   - 5年月供: {format_price(monthly_5y)}万/月\n\n"
        
        # 首付50%
        down_payment_50 = base_price * 0.5
        text += f"📌 **首付50%**: {format_price(down_payment_50)}万\n"
        monthly_3y_50 = calculate_monthly_payment(base_price - down_payment_50, 3)
        monthly_5y_50 = calculate_monthly_payment(base_price - down_payment_50, 5)
        text += f"   - 3年月供: {format_price(monthly_3y_50)}万/月\n"
        text += f"   - 5年月供: {format_price(monthly_5y_50)}万/月\n\n"
        
        # 费用说明
        text += "**其他费用：**\n"
        text += "- 保险: 约8000-12000元（第一年）\n"
        text += "- 上牌: 约500元\n"
        text += "- 充电桩: 免费（厂配）\n\n"
        text += "🎯 **预估落地价**: 指导价 + 保险 + 上牌 ≈ "
        text += f"{format_price(base_price + 1)}万起\n\n"
        text += "想详细了解哪个配置的价格？"
        
        images = get_car_images(car, 2)
        
        return {
            "text": text,
            "images": images,
            "suggestions": ["看看配置怎么选", "有哪些颜色", "能试驾吗", "和竞品比怎么样"]
        }
    
    def _handle_compare(self) -> Dict:
        """处理竞品对比"""
        car = self.context.get("current_car") or "ZEEKR 007"
        competitor = self.context.get("mentioned_cars", [None])
        
        # 获取竞品信息
        text = f"**{car} vs 竞品对比**\n\n"
        
        # 和主要竞品对比
        main_competitors = {
            "ZEEKR 001": ["特斯拉Model 3", "蔚来ET7"],
            "ZEEKR 007": ["特斯拉Model 3", "小米SU7", "小鹏P7"],
            "ZEEKR X": ["Smart精灵#1", "欧拉芭蕾猫"],
            "ZEEKR 009": ["腾势D9", "理想MEGA", "丰田埃尔法"],
            "ZEEKR 7X": ["特斯拉Model Y", "小鹏G6", "问界M5"],
            "ZEEKR 001 FR": ["特斯拉Model S Plaid", "保时捷Taycan"],
        }
        
        competitors_to_show = main_competitors.get(car, ["特斯拉Model Y"])
        
        for comp_name in competitors_to_show[:2]:
            comp_data = COMPETITORS.get(comp_name)
            if not comp_data:
                continue
                
            text += f"### vs {comp_name}\n\n"
            text += f"**{comp_name}**: {comp_data['价格']}\n"
            text += f"**续航**: {comp_data['续航']}\n"
            text += f"**加速**: {comp_data['加速']}\n\n"
            
            text += f"**{car} 的优势：**\n"
            if "ZEEKR" in car:
                text += "- 浩瀚架构，技术领先\n"
                text += "- 8295芯片，智能座舱\n"
                text += "- 浩瀚智驾2.0，体验更好\n"
                text += "- 同价位配置更丰富\n"
            
            text += f"\n**{comp_name} 的优势：**\n"
            for adv in comp_data.get('优势', [])[:2]:
                text += f"- {adv}\n"
            text += "\n---\n\n"
        
        text += "想了解具体哪款配置的差异？或者预约试驾对比体验？"
        
        images = get_car_images(car, 2)
        
        return {
            "text": text,
            "images": images,
            "suggestions": ["看看配置怎么选", "算一下月供", "能试驾吗", "还是买极氪"]
        }
    
    def _handle_interior(self) -> Dict:
        """处理内饰咨询"""
        car = self.context.get("current_car") or "ZEEKR 007"
        
        interior_desc = {
            "ZEEKR 001": "极氪001的内饰采用了家族式设计，15.4英寸中控大屏搭配全液晶仪表盘，Nappa真皮座椅支持通风、加热、按摩功能，还有14喇叭雅马哈音响系统。",
            "ZEEKR 007": "007的内饰更加科技化，星际之门灯幕是最大亮点，车内几乎没有物理按键，15.05英寸2.5K OLED中控屏，8295芯片加持，反应超流畅。",
            "ZEEKR X": "X的内饰设计精致小巧，14.6英寸中控屏可以滑移，副驾娱乐屏选装，4座布局让每个座位都很舒适。",
            "ZEEKR 009": "009的内饰是旗舰级水准，六座版配备二排独立座椅（腿托、小桌板、娱乐屏），四座版更是奢华，后排堪比头等舱。",
            "ZEEKR 7X": "7X的内饰温馨实用，大五座布局空间宽敞，Nappa真皮座椅，全景天窗，氛围灯营造豪华感。",
            "ZEEKR 001 FR": "FR版内饰采用Alcantara材质赛车方向盘，碳纤维装饰板，运动座椅包裹性极强，还有一键漂移模式！",
        }
        
        text = f"**{car}** 的内饰：\n\n"
        text += interior_desc.get(car, "内饰设计精美，配置丰富。")
        text += "\n\n我给您展示一下实车内饰："
        
        images = get_car_images(car, 4)
        
        return {
            "text": text,
            "images": images,
            "suggestions": ["看看外观", "配置怎么选", "价格多少", "能试驾吗"]
        }
    
    def _handle_exterior(self) -> Dict:
        """处理外观咨询"""
        car = self.context.get("current_car") or "ZEEKR 007"
        data = CAR_DATA.get(car, {})
        
        text = f"**{car}** 的外观设计是一大亮点！\n\n"
        text += f"**{data.get('类型', '运动轿跑')}** 造型独特\n"
        text += "- 线条流畅，辨识度极高\n"
        text += "- LED大灯组，夜间效果惊艳\n"
        text += f"- 多种颜色可选（{', '.join(data.get('颜色', [])[:3])}等）\n\n"
        text += "我给您展示一下外观："
        
        images = get_car_images(car, 4)
        
        return {
            "text": text,
            "images": images,
            "suggestions": ["看看内饰", "配置怎么选", "价格多少", "有现车吗"]
        }
    
    def _handle_battery(self) -> Dict:
        """处理续航咨询"""
        car = self.context.get("current_car") or "ZEEKR 007"
        
        battery_info = {
            "ZEEKR 001": {"续航": "712-1032km CLTC", "快充": "30分钟30%-80%", "亮点": "100度麒麟电池"},
            "ZEEKR 007": {"续航": "688-870km CLTC", "快充": "15分钟10%-80%", "亮点": "金砖电池/麒麟电池"},
            "ZEEKR X": {"续航": "512-560km CLTC", "快充": "30分钟10%-80%", "亮点": "城市通勤足够"},
            "ZEEKR 009": {"续航": "702-822km CLTC", "快充": "28分钟10%-80%", "亮点": "140度超大电池"},
            "ZEEKR 7X": {"续航": "605-780km CLTC", "快充": "15分钟10%-80%", "亮点": "全系800V高压"},
            "ZEEKR 001 FR": {"续航": "550km CLTC", "快充": "30分钟30%-80%", "亮点": "四电机高性能"},
        }
        
        info = battery_info.get(car, {})
        
        text = f"**{car}** 的续航表现：\n\n"
        text += f"**CLTC续航**: {info.get('续航', '长续航')}\n"
        text += f"**快充时间**: {info.get('快充', '快充')}\n"
        text += f"**电池技术**: {info.get('亮点', '先进技术')}\n\n"
        text += "**充电方式：**\n"
        text += "1. **家用慢充**: 约8-12小时（预约夜间充电）\n"
        text += "2. **直流快充**: 极氪自建超充站，15分钟补能100km+\n"
        text += "3. **家用充电桩**: 随车赠送，7kW功率\n\n"
        text += "💡 **日常使用建议**：\n"
        text += "- 长续航版：一周充一次就够用\n"
        text += "- 城市通勤：75度电池完全足够\n"
        text += "- 跑长途：提前规划超充站路线"
        
        images = get_car_images(car, 2)
        
        return {
            "text": text,
            "images": images,
            "suggestions": ["算一下月供", "配置怎么选", "有哪些颜色", "能试驾吗"]
        }
    
    def _handle_test_drive(self) -> Dict:
        """处理试驾预约"""
        car = self.context.get("current_car") or "任意车型"
        
        text = f"好的！预约 **{car}** 试驾体验 🚗\n\n"
        text += "**试驾信息：**\n"
        text += "• 试驾时长：约30-60分钟\n"
        text += "• 携带证件：身份证 + 驾照\n"
        text += "• 试驾范围：城市道路 + 快速路\n\n"
        text += "**请确认以下信息：**\n"
        text += "1️⃣ 您在哪个城市？\n"
        text += "2️⃣ 周末还是工作日方便？\n"
        text += "3️⃣ 上午还是下午？\n\n"
        text += "我可以帮您预约最近的极氪中心！"
        
        return {
            "text": text,
            "images": [],
            "suggestions": ["预约周六上午", "预约周日下午", "工作日晚上可以吗"],
            "action": "test_drive_form"  # 触发预约表单
        }
    
    def _handle_farewell(self) -> Dict:
        """处理告别"""
        text = "感谢您的咨询！😊\n\n"
        text += "**总结一下今天聊的内容：**\n"
        
        if self.context.get("current_car"):
            text += f"- 您关注的是 **{self.context['current_car']}**\n"
        
        if self.context.get("detected_need"):
            text += f"- 您的需求是 **{self.context['detected_need']}**\n"
        
        text += "\n**后续服务：**\n"
        text += "• 想好了可以随时找我预约试驾\n"
        text += "• 也可以到附近的极氪中心看车\n"
        text += "• 有任何问题随时问我\n\n"
        text += "祝您选到心仪的车！🚗"
        
        return {
            "text": text,
            "images": [],
            "suggestions": ["再看一遍", "推荐其他车型", "算了还是考虑特斯拉"]
        }
    
    def _handle_general(self) -> Dict:
        """处理一般问题"""
        # 根据上下文智能回复
        if self.context.get("current_car"):
            car = self.context["current_car"]
            text = f"关于 **{car}**，您想了解哪方面？\n\n"
            text += "- 价格和配置\n"
            text += "- 颜色选择\n"
            text += "- 内饰外观\n"
            text += "- 续航充电\n"
            text += "- 竞品对比\n"
            text += "- 购车计算\n\n"
            text += "或者直接告诉我您的疑问～"
        else:
            text = "您好！我是极氪销售助手 🤖\n\n"
            text += "我可以帮您：\n"
            text += "- 根据需求推荐车型\n"
            text += "- 查询价格和配置\n"
            text += "- 展示车型图片\n"
            text += "- 对比竞品车型\n"
            text += "- 计算购车费用\n"
            text += "- 预约试驾体验\n\n"
            text += "请问您今天想了解什么？"
        
        # 展示热门车型图片
        images = get_car_images("ZEEKR 007", 2)
        images.extend(get_car_images("ZEEKR 7X", 2))
        
        return {
            "text": text,
            "images": images[:4] if self.context.get("current_car") else [],
            "suggestions": ["我想买家用车", "商务接待用什么好", "科技感强的推荐", "价格多少"]
        }
    
    def reset(self):
        """重置对话"""
        self.context = {
            "mentioned_cars": [],
            "current_car": None,
            "conversation_history": [],
            "detected_need": None,
            "user_profile": {},
        }

# 全局实例
assistant = SalesAssistant()
