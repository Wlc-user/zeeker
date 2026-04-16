# ZEEKR 极氪智能销售助手

一款基于 Streamlit 的极氪汽车智能销售辅助系统，集车型知识图谱、多维度图片检索、智能对话、客户管理于一体。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
<img width="1842" height="827" alt="image" src="https://github.com/user-attachments/assets/0f23ac63-b717-47ba-9414-bf82759d2796" />
<img width="1868" height="894" alt="image" src="https://github.com/user-attachments/assets/1f83177c-40b9-4b83-99da-bea8805cc2ed" />
<img width="1906" height="953" alt="image" src="https://github.com/user-attachments/assets/d4ee9386-9fba-4f19-bf06-ced0392e8662" />
<img width="1918" height="888" alt="image" src="https://github.com/user-attachments/assets/44e72ba4-30f1-412d-b52b-180e9fdd4b1b" />
<img width="1906" height="864" alt="image" src="https://github.com/user-attachments/assets/2fe144f0-5efd-4b22-9be8-960fa53a9aef" />
<img width="1900" height="846" alt="image" src="https://github.com/user-attachments/assets/85d44d7b-23d0-493c-be13-03b95383416e" />
<img width="1770" height="880" alt="image" src="https://github.com/user-attachments/assets/c857365d-e1d6-484c-9583-9822a1780073" />
<img width="1915" height="908" alt="image" src="https://github.com/user-attachments/assets/82d3cb86-84dc-4212-96a2-8820e8cdd9e2" />

## 功能特性

### 🚗 车型图谱
- 极氪全系车型展示（001/007/X/009/7X/001 FR）
- 配置参数、价格、颜色选项详情
- 车型图片画廊展示

### 📷 图片库
- 基于六维分类的图片检索系统
- 按车型、主题、设计语言筛选
- 批量图片预览与管理

### 💬 智能卖车助手
- 模拟豆包风格的对话界面
- 根据客户需求智能推荐车型
- 支持配置咨询、价格计算、预约试驾

### 📊 竞品对比
- 与特斯拉、蔚来、小米等品牌对比
- 多维度参数对比表格
- 优劣势分析

### 🧮 购车计算器
- 首付/月供计算
- 落地价估算
- 费用明细清单

### 📅 试驾预约
- 客户信息收集
- 意向车型登记
- 预约时间管理

### 👥 CRM客户管理
- 客户画像生成
- 需求分析与标签
- 跟进记录管理

### 📈 数据看板
- 车型热度分析
- 客户意向分布
- 真实数据联动

### 📖 购车指南
- 购车流程指引
- 用车知识科普
- 费用说明详解
- 常见问题解答

## 快速开始

### 环境要求
- Python 3.8+
- Windows/macOS/Linux

### 安装依赖

```bash
pip install streamlit pandas pillow
```

### 运行应用

```bash
cd zeeker
streamlit run app.py
```

应用将自动打开浏览器访问 http://localhost:8502

## 项目结构

```
zeeker/
├── app.py                    # 主应用入口
├── knowledge/                # 知识库模块
│   ├── car_graph.py          # 车型知识图谱
│   ├── image_database.py     # 图片数据库
│   ├── sales_chatbot.py      # 智能销售助手
│   ├── sales_scripts.py      # 销售话术库
│   ├── crm.py                # 客户关系管理
│   └── clean_images.py       # 图片清洗工具
└── README.md
```

## 数据说明

### 车型数据
车型信息存储在 `knowledge/sales_chatbot.py` 的 `CAR_DATA` 字典中，包含：
- 价格、类型、续航、加速性能
- 配置列表、颜色选项
- 竞品对比信息

### 图片数据
- 图片文件夹路径：`e:\pyspace\joker\zeeker\官网图片_已清洗`
- 支持按车型（极氪001/007/X/009/7X/9X）分类
- 使用前请确保图片文件夹存在

### 客户数据
- 使用 Streamlit Session State 存储
- 支持增删改查操作
- 数据仅保存在当前会话中

## 扩展开发

### 添加新车型
在 `knowledge/sales_chatbot.py` 的 `CAR_DATA` 中添加：

```python
"新车型名称": {
    "价格": "XX万",
    "类型": "车型类型",
    "续航": "XXXkm",
    # ... 其他配置
}
```

### 添加销售话术
在 `knowledge/sales_scripts.py` 中添加场景话术模板。

## 技术栈

- **前端**: Streamlit
- **数据处理**: Pandas
- **图片处理**: Pillow
- **状态管理**: Streamlit Session State

## 界面预览

系统采用深色主题设计，具有现代科技感的UI界面。

## License

MIT License - 欢迎开源使用和二次开发

## 联系方式

如有问题或建议，欢迎提交 Issue 或 Pull Request。
