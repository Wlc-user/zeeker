"""
ZEEKR 销售推荐智能体
根据客户需求智能推荐车型和话术
"""
from typing import List, Dict, Optional
from knowledge.car_graph import ZEEKR_MODELS, CUSTOMER_PROFILES, CarRecommender

class SalesAgent:
    """销售智能体"""
    
    def __init__(self):
        self.recommender = CarRecommender()
    
    def analyze_needs(self, needs_text: str) -> Dict:
        """分析客户需求"""
        needs_lower = needs_text.lower()
        
        # 关键词匹配
        keywords = {
            "家庭": ["家庭", "孩子", "父母", "全家", "二孩", "三孩", "空间大"],
            "商务": ["商务", "接待", "老板", "公司", "会议", "谈生意"],
            "性能": ["快", "加速", "动力", "飙车", "赛道", "驾驶乐趣", "激情"],
            "科技": ["科技", "智能", "自动驾驶", "大屏", "芯片", "OTA"],
            "性价比": ["便宜", "划算", "实惠", "省钱", "性价比", "预算"],
            "外观": ["好看", "漂亮", "颜值", "帅", "拉风", "好看"],
            "女性": ["女", "老婆", "老婆开", "好停", "简单"]
        }
        
        matched = []
        for category, words in keywords.items():
            if any(w in needs_lower for w in words):
                matched.append(category)
        
        return {"matched_needs": matched, "raw_text": needs_text}
    
    def recommend(self, needs_text: str) -> Dict:
        """综合推荐"""
        needs_analysis = self.analyze_needs(needs_text)
        matched = needs_analysis["matched_needs"]
        
        results = {
            "需求分析": needs_analysis,
            "推荐车型": [],
            "推荐话术": [],
            "对比建议": ""
        }
        
        # 根据需求匹配客户类型
        customer_type_map = {
            "家庭": "家庭用户",
            "商务": "商务精英",
            "性能": "性能玩家",
            "科技": "科技极客",
            "性价比": "年轻首购",
            "女性": "女性车主"
        }
        
        # 去重获取推荐车型
        seen_models = set()
        for need in matched:
            customer_type = customer_type_map.get(need)
            if customer_type:
                for rec in self.recommender.recommend_by_customer(customer_type):
                    if rec["车型"] not in seen_models:
                        seen_models.add(rec["车型"])
                        results["推荐车型"].append(rec)
        
        # 如果没有匹配，默认推荐007
        if not results["推荐车型"]:
            results["推荐车型"].append({
                "车型": "ZEEKR 007",
                "价格": "20.99-29.99万",
                "类别": "纯电豪华轿车",
                "核心卖点": "性价比之王，入门即豪华"
            })
        
        # 生成话术
        for rec in results["推荐车型"]:
            model_name = rec["车型"]
            if model_name in ZEEKR_MODELS:
                model = ZEEKR_MODELS[model_name]
                # 根据需求定制话术
                customized_talk = []
                
                for need in matched:
                    if need in model.sales_talk:
                        customized_talk.append(model.sales_talk[need])
                    elif need == "家庭" and "家庭出游" in model.use_scenes:
                        customized_talk.append(f"{model_name}的空间非常适合{need}出行")
                    elif need == "性价比":
                        customized_talk.append(f"{model_name}在同价位中配置最丰富，{model.highlights[0]}")
                    elif need == "女性":
                        customized_talk.append(f"{model_name}非常好开，{model.highlights[-1]}")
                
                results["推荐话术"].append({
                    "车型": model_name,
                    "话术": customized_talk or [model.sales_talk.get("开场", "")]
                })
        
        return results
    
    def get_full_sales_script(self, model_name: str) -> Dict:
        """获取完整销售话术"""
        if model_name not in ZEEKR_MODELS:
            return {}
        
        model = ZEEKR_MODELS[model_name]
        
        return {
            "车型": model.name,
            "定位": f"{model.category} | {model.price}",
            "核心卖点": model.highlights,
            "目标客户": model.target_customer,
            "完整话术": model.sales_talk,
            "使用场景": model.use_scenes,
            "竞品对比": model.competitors,
            "参数": model.specs
        }


# 话术模板
SALES_TEMPLATES = {
    "开场白": {
        "通用": "您好，欢迎来到极氪！请问您今天想了解哪款车型呢？",
        "自然进店": "您好！看您气质不凡，是第一次来了解极氪吗？我可以为您详细介绍",
        "已预约": "您好！感谢您的预约，我已经为您准备好了几款适合您的车型资料"
    },
    "需求挖掘": [
        "您今天主要是想了解什么级别的车型呢？",
        "您之前有开过电车吗？",
        "平时主要是谁开？家用还是商务用比较多？",
        "您对续航里程有特别要求吗？",
        "您预算大概在什么范围呢？"
    ],
    "异议处理": {
        "价格": "您今天的价格确实很合适，而且电车保养成本只有油车的1/3，用车成本很低",
        "续航": "我们最新款007支持800V快充，15分钟就能补能500km，长途出行完全没问题",
        "充电": "我们有家用充电桩安装服务，而且全国公共充电桩覆盖率很高",
        "保值": "极氪品牌升值潜力很大，而且我们提供置换补贴政策",
        "竞品": "极氪背靠吉利大厂，品质有保障，而且浩瀚架构是目前最先进的纯电平台"
    },
    "促成成交": [
        "这款车现在下定可以享受限时权益，要帮您留一台吗？",
        "您的眼光真好，这款是目前的爆款车型，订车要趁早",
        "我们店今天有专属优惠，错过就没了",
        "帮您算一下月供吧，很划算的"
    ]
}
