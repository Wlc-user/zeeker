"""
客户跟进管理系统
记录和管理潜在客户的跟进状态
"""

from datetime import datetime, timedelta
from typing import List, Optional

class Customer:
    """客户类"""
    def __init__(self, name: str, phone: str, source: str = "自然到店"):
        self.id = f"CRM_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.name = name
        self.phone = phone[-4:] if len(phone) >= 4 else phone
        self.source = source
        self.level = "A级"
        self.status = "新线索"
        self.interest_car = ""
        self.budget = ""
        self.intent = ""
        self.follow_records = []
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.next_follow = ""
        self.remark = ""
        
    def add_follow(self, action: str, content: str):
        self.follow_records.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "action": action,
            "content": content
        })
        
    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "phone": self.phone,
            "source": self.source, "level": self.level, "status": self.status,
            "interest_car": self.interest_car, "budget": self.budget,
            "intent": self.intent, "follow_records": self.follow_records,
            "created_at": self.created_at, "next_follow": self.next_follow, "remark": self.remark
        }

class CustomerManager:
    """客户管理器"""
    def __init__(self):
        self.customers: List[Customer] = []
        
    def add_customer(self, customer: Customer):
        self.customers.append(customer)
        
    def get_all(self) -> List[Customer]:
        return self.customers
    
    def get_by_status(self, status: str) -> List[Customer]:
        return [c for c in self.customers if c.status == status]
    
    def get_overdue(self) -> List[Customer]:
        overdue = []
        for c in self.customers:
            if c.next_follow:
                try:
                    next_date = datetime.strptime(c.next_follow, "%Y-%m-%d")
                    if next_date.date() < datetime.now().date() and c.status not in ["已成交", "已流失"]:
                        overdue.append(c)
                except:
                    pass
        return overdue
    
    def get_statistics(self) -> dict:
        total = len(self.customers)
        if total == 0:
            return {"total": 0, "new_leads": 0, "following": 0, "invited": 0, "converted": 0, "lost": 0, "a_rate": 0}
        return {
            "total": total,
            "new_leads": len(self.get_by_status("新线索")),
            "following": len(self.get_by_status("跟进中")),
            "invited": len(self.get_by_status("已邀约")),
            "converted": len(self.get_by_status("已成交")),
            "lost": len(self.get_by_status("已流失")),
            "a_rate": round(len([c for c in self.customers if c.level == "A级"]) / total * 100, 1)
        }

# 全局客户管理器
customer_manager = CustomerManager()

# 初始化示例客户
def init_sample_customers():
    samples = [
        {"name": "张先生", "phone": "138****1234", "source": "线上留资", "level": "A级", "status": "跟进中", "interest_car": "ZEEKR 7X", "budget": "25-30万"},
        {"name": "李女士", "phone": "139****5678", "source": "老客推荐", "level": "A级", "status": "已邀约", "interest_car": "ZEEKR 009", "budget": "50-60万"},
        {"name": "王先生", "phone": "136****9012", "source": "自然到店", "level": "B级", "status": "新线索", "interest_car": "ZEEKR 007", "budget": "20-25万"},
        {"name": "刘先生", "phone": "135****3456", "source": "展会", "level": "C级", "status": "跟进中", "interest_car": "ZEEKR 001", "budget": "30-40万"},
        {"name": "陈先生", "phone": "137****7890", "source": "线上留资", "level": "A级", "status": "已成交", "interest_car": "ZEEKR 7X", "budget": "25万"},
    ]
    for s in samples:
        c = Customer(s["name"], s["phone"], s["source"])
        c.level = s["level"]
        c.status = s["status"]
        c.interest_car = s["interest_car"]
        c.budget = s["budget"]
        customer_manager.add_customer(c)

init_sample_customers()
