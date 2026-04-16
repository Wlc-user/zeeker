"""
ZEEKR 极氪车型知识图谱与销售推荐系统 v3
新增功能:
- 用户认证系统 (注册/登录/忘记密码)
- 数据看板真实联动
- 购车指南完善
"""
import streamlit as st
import pandas as pd
from knowledge.car_graph import ZEEKR_MODELS, CUSTOMER_PROFILES, CarRecommender
from knowledge.image_database import (
    IMAGE_DATABASE, get_all_images, get_car_images,
    search_by_keyword, search_by_theme,
    CONTENT_THEMES, DESIGN_LANGUAGES, MARKET_POSITIONS
)
from knowledge.sales_chatbot import SalesAssistant, assistant, CAR_DATA, COMPETITORS
from knowledge.sales_scripts import SALES_SCRIPTS, get_script_by_scene, get_all_scenes
from knowledge.crm import Customer, CustomerManager, customer_manager
from knowledge.auth import (
    init_auth_data, is_authenticated, get_current_user, logout,
    login as auth_login, register as auth_register,
    verify_email as auth_verify, forgot_password as auth_forgot,
    reset_password as auth_reset, change_password as auth_change,
    resend_verification_code, is_valid_email
)
import time
from datetime import datetime, timedelta

# 初始化认证数据
init_auth_data()

# 辅助函数: 获取图片路径 (支持 ImageMetadata 或字符串)
def get_image_path(img):
    """从 ImageMetadata 或路径字符串获取图片路径"""
    if hasattr(img, 'path'):
        return img.path
    return str(img)

# ============================================================
# 认证页面
# ============================================================
def show_auth_page():
    """显示登录/注册页面"""
    
    # 检查URL参数
    query_params = st.query_params
    if "token" in query_params:
        # 重置密码页面
        token = query_params["token"]
        show_reset_password_page(token)
        return
    
    # 初始化session state
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "登录"  # 登录/注册/忘记密码/验证邮箱
    if "pending_email" not in st.session_state:
        st.session_state.pending_email = None
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h1 style="font-size: 2.5rem; background: linear-gradient(90deg, #00d4ff, #00ff88); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">ZEEKR 极氪</h1>
            <h3 style="color: #888; margin-top: 0.5rem;">智能销售助手</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Tab切换
        tab1, tab2, tab3 = st.tabs(["登录", "注册", "忘记密码"])
        
        with tab1:
            show_login_form()
        
        with tab2:
            show_register_form()
        
        with tab3:
            show_forgot_password_form()

def show_login_form():
    """登录表单"""
    st.markdown("### 登录")
    
    with st.form("login_form"):
        email = st.text_input("邮箱", placeholder="your@email.com", key="login_email")
        password = st.text_input("密码", type="password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("登录", use_container_width=True)
        with col2:
            if st.form_submit_button("忘记密码？", use_container_width=True):
                st.session_state.auth_mode = "忘记密码"
                st.rerun()
        
        if submitted:
            if not email or not password:
                st.error("请填写所有字段")
            else:
                success, msg = auth_login(email, password)
                if success:
                    st.success(msg)
                    st.session_state.show_auth = False
                    st.rerun()
                else:
                    st.error(msg)

def show_register_form():
    """注册表单"""
    st.markdown("### 注册新账号")
    
    with st.form("register_form"):
        name = st.text_input("姓名", placeholder="您的姓名", key="reg_name")
        email = st.text_input("邮箱", placeholder="your@email.com", key="reg_email")
        password = st.text_input("密码", type="password", placeholder="至少6个字符", key="reg_password")
        confirm_password = st.text_input("确认密码", type="password", key="reg_confirm")
        
        submitted = st.form_submit_button("注册", use_container_width=True)
        
        if submitted:
            success, msg = auth_register(name, email, password, confirm_password)
            if success:
                st.success(msg)
                st.session_state.pending_email = email
                st.session_state.auth_mode = "验证邮箱"
                st.rerun()
            else:
                st.error(msg)
    
    # 验证邮箱表单
    if st.session_state.get("auth_mode") == "验证邮箱" and st.session_state.pending_email:
        show_verify_form(st.session_state.pending_email)

def show_verify_form(email: str):
    """验证邮箱表单"""
    st.markdown("---")
    st.markdown("### 验证邮箱")
    st.info(f"请输入发送至 **{email}** 的验证码")
    
    with st.form("verify_form"):
        code = st.text_input("验证码", placeholder="6位数字", key="verify_code")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("验证", use_container_width=True)
        with col2:
            if st.form_submit_button("重新发送", use_container_width=True):
                success, msg = resend_verification_code(email)
                if success:
                    st.info(msg)
                else:
                    st.error(msg)
        
        if submitted:
            if not code:
                st.error("请输入验证码")
            else:
                success, msg = auth_verify(email, code)
                if success:
                    st.success(msg + " 请登录")
                    st.session_state.auth_mode = "登录"
                    st.rerun()
                else:
                    st.error(msg)

def show_forgot_password_form():
    """忘记密码表单"""
    st.markdown("### 忘记密码")
    st.caption("输入您的注册邮箱，我们将发送密码重置链接")
    
    with st.form("forgot_form"):
        email = st.text_input("邮箱", placeholder="your@email.com", key="forgot_email")
        
        submitted = st.form_submit_button("发送重置链接", use_container_width=True)
        
        if submitted:
            if not email:
                st.error("请输入邮箱")
            else:
                success, msg = auth_forgot(email)
                if success:
                    st.success(msg)

def show_reset_password_page(token: str):
    """重置密码页面"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1 style="font-size: 2rem; background: linear-gradient(90deg, #00d4ff, #00ff88); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">重置密码</h1>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("reset_form"):
        st.markdown("### 设置新密码")
        new_password = st.text_input("新密码", type="password", placeholder="至少6个字符", key="reset_password")
        confirm_password = st.text_input("确认新密码", type="password", key="reset_confirm")
        
        submitted = st.form_submit_button("确认重置", use_container_width=True)
        
        if submitted:
            success, msg = auth_reset(token, new_password, confirm_password)
            if success:
                st.success(msg)
                st.info("即将跳转到登录页面...")
                time.sleep(2)
                st.query_params.clear()
                st.rerun()
            else:
                st.error(msg)
        
        st.markdown("[返回登录页面](./?auth=login)")

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="ZEEKR 销售助手",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS样式 - 现代化设计
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {background: linear-gradient(135deg, #0f1419 0%, #1a1f26 100%);}
    
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00d4ff, #00ff88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        text-align: center;
        color: #888;
        margin-bottom: 2rem;
        font-size: 1rem;
    }
    
    .section-title {
        font-size: 1.3rem;
        color: #fff;
        margin: 1.5rem 0 1rem 0;
        padding-left: 0.5rem;
        border-left: 3px solid #00d4ff;
    }
    
    .car-card {
        background: linear-gradient(145deg, #1e2328, #2a2f36);
        border-radius: 16px;
        padding: 1.2rem;
        border: 1px solid #333;
        transition: all 0.3s ease;
    }
    
    .car-card:hover {
        border-color: #00d4ff;
        transform: translateY(-2px);
    }
    
    .price-tag {
        background: linear-gradient(90deg, #00d4ff, #00ff88);
        color: #000;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .feature-tag {
        background: #2a2f36;
        color: #aaa;
        padding: 0.25rem 0.6rem;
        border-radius: 8px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
    
    .stats-card {
        background: linear-gradient(145deg, #1e2328, #2a2f36);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #333;
    }
    
    .stats-number {
        font-size: 2rem;
        font-weight: 700;
        color: #00d4ff;
    }
    
    .compare-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }
    
    .compare-table th, .compare-table td {
        padding: 0.75rem;
        text-align: left;
        border-bottom: 1px solid #333;
    }
    
    .compare-table th {
        color: #00d4ff;
        font-weight: 600;
    }
    
    .highlight-row {
        background: rgba(0, 212, 255, 0.1);
    }
    
    div[data-testid="stHorizontalBlock"] button {
        background: #1e2328 !important;
        border: 1px solid #333 !important;
        color: #fff !important;
        border-radius: 12px !important;
    }
    
    div[data-testid="stHorizontalBlock"] button:hover {
        border-color: #00d4ff !important;
        background: #2a2f36 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 登录检查
# ============================================================
# 初始化show_auth状态
if "show_auth" not in st.session_state:
    st.session_state.show_auth = False

# 如果用户未登录且未显示登录页面，显示登录页面
if not is_authenticated() and st.session_state.show_auth:
    show_auth_page()
    st.stop()

# 如果用户未登录，显示提示
if not is_authenticated():
    st.warning("请登录后使用完整功能 [登录](./?auth=login)")

# ============================================================
# 侧边栏导航
# ============================================================
with st.sidebar:
    st.markdown("### 🚗 ZEEKR")
    st.markdown("销售智能系统 v3")
    
    # 用户登录状态
    if is_authenticated():
        user = get_current_user()
        st.success(f"欢迎, {user['name']}")
        if st.button("退出登录", use_container_width=True):
            logout()
            st.rerun()
    else:
        st.info("未登录")
        if st.button("登录/注册", use_container_width=True):
            st.session_state.show_auth = True
            st.rerun()
    
    st.divider()
    
    page = st.radio(
        "导航",
        [
            "🏠 首页概览", 
            "🚗 车型图谱", 
            "📷 图片库", 
            "💬 卖车助手", 
            "📊 竞品对比",
            "🧮 购车计算",
            "📅 试驾预约",
            "📝 话术库",
            "👥 客户跟进",
            "📈 数据看板",
            "👥 客户画像",
            "📖 购车指南"
        ],
        label_visibility="collapsed"
    )
    
    st.divider()
    st.markdown("**系统信息**")
    st.caption(f"登录用户: {get_current_user()['name'] if is_authenticated() else '游客'}")
    st.caption(f"车型数: {len(ZEEKR_MODELS)}")
    st.caption(f"图片数: {len(get_all_images())}")

# ============================================================
# 首页概览
# ============================================================
if page == "🏠 首页概览":
    st.markdown('<div class="main-header">ZEEKR 极氪</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">智能销售系统 · 车型知识图谱 · 多维度图片检索</div>', unsafe_allow_html=True)
    
    # 统计卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("在售车型", "6款", "001/007/X/009/7X/FR")
    with col2:
        st.metric("图片总数", f"{len(get_all_images())}张", "+汽车之家")
    with col3:
        st.metric("价格区间", "17-77万", "入门到旗舰")
    with col4:
        st.metric("客户画像", f"{len(CUSTOMER_PROFILES)}种", "精准匹配")
    
    st.divider()
    
    # 车型矩阵
    st.markdown('<div class="section-title">车型矩阵</div>', unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, (name, model) in enumerate(ZEEKR_MODELS.items()):
        with cols[i % 3]:
            car_imgs = get_car_images(name)
            
            if car_imgs:
                st.image(car_imgs[0].path, use_container_width=True)
            
            st.markdown(f"**{model.name}**")
            st.write(f"📌 {model.category}")
            st.markdown(f'<span class="price-tag">{model.price}</span>', unsafe_allow_html=True)
            st.write(f"📷 {len(car_imgs)}张图片")
            
            highlights = model.highlights[:3]
            st.markdown(" ".join([f'<span class="feature-tag">{h}</span>' for h in highlights]), unsafe_allow_html=True)

# ============================================================
# 车型图谱 + 图片库(整合)
# ============================================================
elif page == "🚗 车型图谱":
    st.markdown('<div class="main-header">车型图谱</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">查看车型详情 · 浏览车型图片 · 了解配置价格</div>', unsafe_allow_html=True)
    
    # 左侧:车型列表 + 详情
    # 右侧:该车型全部图片
    
    car_list = list(CAR_DATA.keys())
    
    # 检查是否有从图片库跳转过来的车型
    default_car = st.session_state.get("selected_car", None)
    if default_car and default_car not in car_list:
        default_car = car_list[0]
    
    col_left, col_right = st.columns([1, 1.2])
    
    with col_left:
        if default_car:
            selected = st.selectbox("选择车型", car_list, index=car_list.index(default_car))
            # 清除传递的车型,避免下次进入时还是同一个
            st.session_state.selected_car = None
        else:
            selected = st.selectbox("选择车型", car_list)
        data = CAR_DATA[selected]
        
        # 车型基本信息
        st.markdown(f"### 🚗 {selected}")
        st.markdown(f"**类型**: {data['类型']}")
        st.markdown(f"**级别**: {data['级别']}")
        st.markdown(f'<span class="price-tag">{data["价格"]}</span>', unsafe_allow_html=True)
        
        st.markdown("### ✨ 核心亮点")
        for h in data['特点']:
            st.markdown(f"- {h}")
        
        st.markdown("### 👥 适合人群")
        for s in data['适合']:
            st.markdown(f"- {s}")
        
        st.markdown("### 📊 技术参数")
        specs_data = {
            "续航": data.get("续航", "N/A"),
            "加速": data.get("加速", "N/A"),
        }
        df = pd.DataFrame([specs_data]).T
        df.columns = ['参数']
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # 配置选择
        st.markdown("### 🔧 在售配置")
        for cfg in data.get("配置列表", []):
            with st.expander(f"{cfg['名称']} - {cfg['价格']}万"):
                st.write(cfg['特点'])
        
        # 颜色选择
        st.markdown("### 🎨 可选颜色")
        st.write("**外观**: " + " | ".join(data.get("颜色", [])))
        st.write("**内饰**: " + " | ".join(data.get("内饰颜色", [])))
    
    with col_right:
        st.markdown(f"### 📷 {selected} 车型图片")
        
        car_imgs = get_car_images(selected)
        st.caption(f"共 {len(car_imgs)} 张图片")
        
        if car_imgs:
            # 图片画廊
            for i in range(0, len(car_imgs), 2):
                img_cols = st.columns(2)
                with img_cols[0]:
                    st.image(get_image_path(car_imgs[i]), use_container_width=True)
                if i + 1 < len(car_imgs):
                    with img_cols[1]:
                        st.image(get_image_path(car_imgs[i+1]), use_container_width=True)
        else:
            st.info("暂无图片")
        
        # 底部快捷操作
        st.markdown("### 💡 快速操作")
        op_cols = st.columns(2)
        with op_cols[0]:
            if st.button("💬 咨询这台车", use_container_width=True):
                st.session_state.pending_input = f"我想了解{selected}"
        with op_cols[1]:
            if st.button("📅 预约试驾", use_container_width=True):
                st.session_state.page = "📅 试驾预约"
                st.rerun()
    
    # 全部车型快速对比
    st.markdown("---")
    st.markdown("### 🔍 全部车型快速对比")
    
    # 简化对比表
    compare_df = []
    for car, info in CAR_DATA.items():
        car_imgs = get_car_images(car)
        compare_df.append({
            "车型": car,
            "类型": info.get("类型", ""),
            "价格": info.get("价格", ""),
            "续航": info.get("续航", ""),
            "加速": info.get("加速", ""),
            "图片数": len(car_imgs)
        })
    
    compare_table = pd.DataFrame(compare_df)
    st.dataframe(compare_table, use_container_width=True, hide_index=True)

# ============================================================
# 卖车助手
# ============================================================
elif page == "💬 卖车助手":
    st.markdown('<div class="main-header">极氪智能卖车助手</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">豆包风格 · 对话中实时展示相关图片 · 智能推荐</div>', unsafe_allow_html=True)
    
    # 初始化
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "assistant" not in st.session_state:
        st.session_state.assistant = SalesAssistant()
    
    # 处理来自其他页面的跳转
    if hasattr(st.session_state, 'pending_input') and st.session_state.pending_input:
        pending = st.session_state.pending_input
        st.session_state.pending_input = ""
        st.session_state.chat_history.append({
            "role": "user",
            "content": pending,
            "idx": len(st.session_state.chat_history)
        })
        response = st.session_state.assistant.generate_response(pending)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response["text"],
            "images": response.get("images", []),
            "suggestions": response.get("suggestions", []),
            "idx": len(st.session_state.chat_history)
        })
    
    # 显示对话历史
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
                if msg.get("images"):
                    cols = st.columns(min(4, len(msg["images"])))
                    for i, img in enumerate(msg["images"][:4]):
                        with cols[i]:
                            try:
                                # img 可能是 ImageMetadata 或路径字符串
                                img_path = img.path if hasattr(img, 'path') else str(img)
                                st.image(img_path, use_container_width=True)
                            except Exception as e:
                                pass
                if msg.get("suggestions"):
                    st.write("**推荐追问:**")
                    cols = st.columns(min(4, len(msg["suggestions"])))
                    for i, s in enumerate(msg["suggestions"][:4]):
                        with cols[i]:
                            if st.button(s, key=f"sug_{msg.get('idx', 0)}_{i}"):
                                st.session_state.pending_input = s
                                st.rerun()
    
    # 处理pending_input
    if hasattr(st.session_state, 'pending_input') and st.session_state.pending_input:
        pending = st.session_state.pending_input
        del st.session_state.pending_input
        st.session_state.chat_history.append({
            "role": "user",
            "content": pending,
            "idx": len(st.session_state.chat_history)
        })
        response = st.session_state.assistant.generate_response(pending)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response["text"],
            "images": response.get("images", []),
            "suggestions": response.get("suggestions", []),
            "idx": len(st.session_state.chat_history)
        })
        st.rerun()
    
    user_input = st.text_input(
        "输入客户需求...",
        placeholder="例如:30岁,家里有小孩,想要科技感强一点的...",
        key="chat_input",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        send_btn = st.button("发送", type="primary", use_container_width=True)
    with col2:
        if st.button("清空对话", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.assistant.reset()
            st.rerun()
    
    if send_btn and user_input:
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "idx": len(st.session_state.chat_history)
        })
        
        response = st.session_state.assistant.generate_response(user_input)
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response["text"],
            "images": response.get("images", []),
            "suggestions": response.get("suggestions", []),
            "idx": len(st.session_state.chat_history)
        })
        
        st.rerun()
    
    st.divider()
    st.markdown("**💡 快捷问题**")
    quick_questions = [
        ("🏠 家用车推荐", "家里有小孩,想买空间大的车"),
        ("💼 商务接待", "需要商务接待用什么车好"),
        ("🚀 科技感强的", "想要科技感强一点的电动车"),
        ("⚡ 性能车", "想要加速快动力强的"),
        ("💰 算月供", "帮我算一下月供多少钱"),
        ("🔍 和小米对比", "和特斯拉对比怎么样"),
    ]
    
    for i in range(0, len(quick_questions), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(quick_questions):
                label, question = quick_questions[i + j]
                with cols[j]:
                    if st.button(label, use_container_width=True):
                        st.session_state.chat_history.append({
                            "role": "user",
                            "content": question,
                            "idx": len(st.session_state.chat_history)
                        })
                        response = st.session_state.assistant.generate_response(question)
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response["text"],
                            "images": response.get("images", []),
                            "suggestions": response.get("suggestions", []),
                            "idx": len(st.session_state.chat_history)
                        })
                        st.rerun()

# ============================================================
# 竞品对比
# ============================================================
elif page == "📊 竞品对比":
    st.markdown('<div class="main-header">竞品对比</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">极氪 vs 竞品车型对比分析</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        zeekr_car = st.selectbox("选择极氪车型", list(CAR_DATA.keys()), key="zeekr_compare")
    with col2:
        competitor_options = list(COMPETITORS.keys()) + ["请选择竞品..."]
        competitor = st.selectbox("选择竞品", competitor_options, key="competitor")
    
    if zeekr_car in CAR_DATA:
        zeekr_data = CAR_DATA[zeekr_car]
        
        st.markdown("---")
        
        compare_data = {
            "项目": ["价格", "类型", "续航", "加速", "核心特点"],
            zeekr_car: [
                zeekr_data.get("价格", "N/A"),
                zeekr_data.get("类型", "N/A"),
                zeekr_data.get("续航", "N/A"),
                zeekr_data.get("加速", "N/A"),
                " | ".join(zeekr_data.get("特点", [])[:3])
            ]
        }
        
        if competitor != "请选择竞品..." and competitor in COMPETITORS:
            comp_data = COMPETITORS[competitor]
            compare_data[competitor] = [
                comp_data.get("价格", "N/A"),
                "轿车/SUV/MPV",
                comp_data.get("续航", "N/A"),
                comp_data.get("加速", "N/A"),
                " | ".join(comp_data.get("优势", [])[:3])
            ]
        
        df = pd.DataFrame(compare_data)
        df = df.set_index("项目")
        st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### ✅ {zeekr_car} 优势")
            st.markdown("- **浩瀚架构**: 技术领先,迭代快")
            st.markdown("- **性价比高**: 同价位配置更丰富")
            st.markdown("- **8295芯片**: 智能座舱更流畅")
            st.markdown("- **浩瀚智驾2.0**: 智能驾驶体验好")
            
            car_imgs = get_car_images(zeekr_car, 2)
            if car_imgs:
                st.image(car_imgs[0], use_container_width=True)
        
        with col2:
            if competitor != "请选择竞品..." and competitor in COMPETITORS:
                st.markdown(f"### ✅ {competitor} 优势")
                for adv in COMPETITORS[competitor].get("优势", []):
                    st.markdown(f"- **{adv}**")
                
                st.markdown("### ❌ 对比劣势")
                for dis in COMPETITORS[competitor].get("劣势", []):
                    st.markdown(f"- {dis}")
        
        st.markdown("---")
        st.markdown("### 💡 购车建议")
        
        if "家用" in zeekr_data.get("适合", []):
            st.info("🏠 家用推荐:ZEEKR 7X 空间大,安全配置高,非常适合家庭用户")
        if "商务" in zeekr_data.get("适合", []):
            st.info("💼 商务推荐:ZEEKR 009 气场强大,内饰豪华,接待客户有面子")
        if "科技" in zeekr_data.get("适合", []):
            st.info("🚀 科技推荐:ZEEKR 007 星际之门灯幕+8295芯片,科技感满满")

# ============================================================
# 购车计算
# ============================================================
elif page == "🧮 购车计算":
    st.markdown('<div class="main-header">购车计算器</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">计算首付,月供,落地价</div>', unsafe_allow_html=True)
    
    car = st.selectbox("选择车型", list(CAR_DATA.keys()), key="calc_car")
    data = CAR_DATA[car]
    
    configs = data.get("配置列表", [])
    if configs:
        selected_config = st.selectbox(
            "选择配置",
            [cfg["名称"] for cfg in configs],
            key="calc_config"
        )
        for cfg in configs:
            if cfg["名称"] == selected_config:
                car_price = cfg["价格"]
                break
    else:
        price_range = data.get("价格区间", [20, 30])
        car_price = (price_range[0] + price_range[1]) / 2
    
    st.markdown(f"### 📋 购车费用明细")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        down_payment_ratio = st.slider("首付比例", 10, 50, 30, key="down_ratio") / 100
    with col2:
        loan_years = st.selectbox("贷款年限", [3, 5, 7], key="loan_years")
    with col3:
        loan_rate = st.selectbox("贷款利率", [0.028, 0.035, 0.049], 
                                  format_func=lambda x: f"{x*100:.1f}%", key="loan_rate")
    
    down_payment = car_price * down_payment_ratio
    loan_amount = car_price - down_payment
    monthly_rate = loan_rate / 12
    months = loan_years * 12
    
    if monthly_rate > 0:
        monthly_payment = loan_amount * monthly_rate * (1 + monthly_rate) ** months / ((1 + monthly_rate) ** months - 1)
    else:
        monthly_payment = loan_amount / months
    monthly_payment = round(monthly_payment, 2)
    
    insurance = car_price * 0.035 + 800
    tax = 0
    total_price = car_price + insurance + tax + 0.05
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("指导价", f"{car_price:.2f}万")
    with col2:
        st.metric(f"首付({int(down_payment_ratio*100)}%)", f"{down_payment:.2f}万")
    with col3:
        st.metric("贷款金额", f"{loan_amount:.2f}万")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("月供", f"{monthly_payment:.2f}万", f"{loan_years}年还清")
    with col2:
        st.metric("保险预估", f"{insurance:.2f}万")
    with col3:
        st.metric("预估落地价", f"{total_price:.2f}万", "含保险上牌")
    
    st.markdown("---")
    st.markdown("### 📊 还款明细(前12期)")
    
    monthly_data = {
        "期数": [],
        "本金(万)": [],
        "利息(万)": [],
        "月供(万)": [],
        "剩余本金(万)": []
    }
    
    remaining = loan_amount
    total_interest = 0
    
    for month in range(1, min(13, months + 1)):
        monthly_data["期数"].append(f"第{month}期")
        interest = remaining * monthly_rate
        principal = monthly_payment - interest
        monthly_data["本金(万)"].append(f"{principal:.4f}")
        monthly_data["利息(万)"].append(f"{interest:.4f}")
        monthly_data["月供(万)"].append(f"{monthly_payment:.4f}")
        monthly_data["剩余本金(万)"].append(f"{remaining:.4f}")
        remaining -= principal
        total_interest += interest
    
    df = pd.DataFrame(monthly_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.info(f"💡 总利息支出: {total_interest:.2f}万")
    
    st.markdown("---")
    st.markdown("### 💡 温馨提示")
    st.markdown("- 新能源车免购置税,节省大笔费用")
    st.markdown("- 贷款方案灵活,可提前还款")
    st.markdown("- 极氪门店可协助办理分期")

# ============================================================
# 图片库
# ============================================================
elif page == "📷 图片库":
    st.markdown('<div class="main-header">极氪图片库</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">浏览全部车型图片 · 按车型/主题筛选</div>', unsafe_allow_html=True)
    
    # 按车型分类展示
    car_options = ["全部"] + list(CAR_DATA.keys())
    selected_car = st.selectbox("按车型筛选", car_options)
    
    # 筛选条件
    col1, col2, col3 = st.columns(3)
    with col1:
        show_type = st.selectbox("图片类型", ["全部", "外观", "内饰", "细节"])
    with col2:
        sort_by = st.selectbox("排序方式", ["默认", "按车型"])
    with col3:
        show_count = st.slider("每行数量", 2, 4, 3)
    
    # 获取图片
    if selected_car != "全部":
        imgs = get_car_images(selected_car)
        car_data = CAR_DATA.get(selected_car, {})
    else:
        imgs = get_all_images()
        car_data = None
    
    # 根据类型筛选
    if show_type != "全部":
        keyword_map = {
            "外观": ["外观", "整车", "前脸", "侧面"],
            "内饰": ["内饰", "座椅", "中控", "方向盘"],
            "细节": ["细节", "灯", "轮毂", "天线"]
        }
        keywords = keyword_map.get(show_type, [])
        if keywords:
            filtered_imgs = []
            for img in imgs:
                if any(k in str(img.content_theme) for k in keywords):
                    filtered_imgs.append(img)
            imgs = filtered_imgs if filtered_imgs else imgs
    
    # 统计
    total = len(get_all_images())
    st.markdown(f"**当前筛选: {len(imgs)}张** | **图片库总计: {total}张**")
    
    st.divider()
    
    # 如果选择了车型,显示车型信息
    if selected_car != "全部" and car_data:
        info_col1, info_col2 = st.columns([1, 2])
        with info_col1:
            # 车型图片
            car_imgs = get_car_images(selected_car, 1)
            if car_imgs:
                st.image(car_imgs[0], use_container_width=True)
        with info_col2:
            st.markdown(f"### 🚗 {selected_car}")
            st.markdown(f"**{car_data.get('类型', '')}** | {car_data.get('价格', '')}")
            st.markdown(f"续航: {car_data.get('续航', '')} | 加速: {car_data.get('加速', '')}")
            
            # 快捷操作
            op_cols = st.columns(2)
            with op_cols[0]:
                if st.button("💬 咨询这台车", use_container_width=True):
                    st.session_state.pending_input = f"我想了解{selected_car}"
                    st.rerun()
            with op_cols[1]:
                if st.button("📅 预约试驾", use_container_width=True):
                    st.session_state.page = "📅 试驾预约"
                    st.rerun()
    
    st.markdown("---")
    
    # 图片展示
    if imgs:
        cols = st.columns(show_count)
        for i, img in enumerate(imgs):
            with cols[i % show_count]:
                try:
                    st.image(get_image_path(img), use_container_width=True)
                    tags = img.content_theme + img.design_language
                    st.caption(f"📌 {img.car_series}")
                except:
                    st.warning(f"图片加载失败")
    else:
        st.info("暂无符合条件的图片")
    
    # 全部车型图片预览
    if selected_car == "全部":
        st.markdown("---")
        st.markdown("### 🚗 车型快速入口")
        
        car_cols = st.columns(3)
        for i, (car, data) in enumerate(CAR_DATA.items()):
            with car_cols[i % 3]:
                car_imgs = get_car_images(car, 1)
                if car_imgs:
                    st.image(car_imgs[0], use_container_width=True)
                st.markdown(f"**{car}**")
                st.caption(f"{data.get('类型', '')} - {data.get('价格', '')}")
                if st.button(f"查看详情", key=f"img_car_{i}"):
                    # 跳转到车型图谱页面
                    st.session_state.selected_car = car
                    st.session_state.page = "🚗 车型图谱"
                    st.rerun()

# ============================================================
# 销售话术库
# ============================================================
elif page == "📝 话术库":
    st.markdown('<div class="main-header">销售话术库</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">场景化话术模板 · 提升销售转化率</div>', unsafe_allow_html=True)
    
    scenes = get_all_scenes()
    scene_names = {
        "接待": "🎯 客户接待",
        "需求挖掘": "🔍 需求挖掘",
        "车型介绍": "🚗 车型介绍",
        "价格谈判": "💰 价格谈判",
        "异议处理": "⚡ 异议处理",
        "促成成交": "✅ 促成成交",
        "售后服务": "🔧 售后服务",
        "流失挽回": "💔 流失挽回"
    }
    
    # 场景选择
    col1, col2 = st.columns([1, 2])
    with col1:
        selected_scene = st.selectbox("选择场景", list(scene_names.values()))
    with col2:
        search_keyword = st.text_input("🔍 搜索话术", placeholder="输入关键词搜索...")
    
    # 找到对应的场景key
    scene_key = None
    for k, v in scene_names.items():
        if v == selected_scene:
            scene_key = k
            break
    
    if scene_key and scene_key in SALES_SCRIPTS:
        scene_data = SALES_SCRIPTS[scene_key]
        
        st.markdown(f"### {scene_names[scene_key]}")
        st.markdown(f"**场景**: {scene_data.get('场景', '')}")
        
        # 显示该场景下所有的话术
        for section_name, section_content in scene_data.items():
            if section_name in ["标题", "场景"]:
                continue
            
            st.markdown(f"**📌 {section_name}**")
            
            if isinstance(section_content, list):
                for i, script in enumerate(section_content):
                    with st.container():
                        col_left, col_right = st.columns([4, 1])
                        with col_left:
                            st.info(script)
                        with col_right:
                            if st.button("📋 复制", key=f"copy_{scene_key}_{i}"):
                                st.session_state.copied_text = script
                                st.success("已复制!")
                        st.divider()
    
    # 车型专项话术
    st.markdown("---")
    st.markdown("### 🚗 车型专项话术")
    
    car_script_tabs = st.tabs(list(CAR_DATA.keys()))
    for i, (car, car_data) in enumerate(CAR_DATA.items()):
        with car_script_tabs[i]:
            if car in SALES_SCRIPTS.get("车型介绍", {}).get(car, {}):
                car_script = SALES_SCRIPTS["车型介绍"][car]
                st.markdown(f"**定位**: {car_script.get('定位', '')}")
                
                st.markdown("**核心卖点**")
                for tag in car_script.get('核心卖点', []):
                    st.markdown(f"- {tag}")
                
                st.markdown("**话术要点**")
                for script in car_script.get('话术', []):
                    st.success(script)
                    st.divider()
                
                st.markdown("**竞品对比话术**")
                st.info(car_script.get('对比竞品', ''))

# ============================================================
# 客户跟进管理
# ============================================================
elif page == "👥 客户跟进":
    st.markdown('<div class="main-header">客户跟进管理</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">CRM客户关系管理 · 跟进记录 · 转化漏斗</div>', unsafe_allow_html=True)
    
    # 获取统计数据
    stats = customer_manager.get_statistics()
    
    # 统计卡片
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("总客户数", stats["total"])
    with col2:
        st.metric("新线索", stats["new_leads"])
    with col3:
        st.metric("跟进中", stats["following"])
    with col4:
        st.metric("已成交", stats["converted"])
    with col5:
        st.metric("A级占比", f"{stats['a_rate']}%")
    
    # 逾期未跟进提醒
    overdue = customer_manager.get_overdue()
    if overdue:
        st.warning(f"⚠️ 您有 {len(overdue)} 位客户逾期未跟进!")
        for c in overdue[:3]:
            st.error(f"  - {c.name} ({c.phone}) - 上次跟进: {c.next_follow}")
    
    st.markdown("---")
    
    # 标签页:客户列表 / 新增客户
    tab1, tab2 = st.tabs(["📋 客户列表", "➕ 新增客户"])
    
    with tab1:
        # 筛选条件
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_status = st.selectbox("按状态筛选", ["全部", "新线索", "跟进中", "已邀约", "已成交", "已流失"])
        with col2:
            filter_level = st.selectbox("按等级筛选", ["全部", "A级", "B级", "C级"])
        with col3:
            sort_by = st.selectbox("排序", ["最新添加", "下次跟进时间", "客户等级"])
        
        # 获取筛选后的客户
        all_customers = customer_manager.get_all()
        
        if filter_status != "全部":
            all_customers = [c for c in all_customers if c.status == filter_status]
        if filter_level != "全部":
            all_customers = [c for c in all_customers if c.level == filter_level]
        
        # 排序
        if sort_by == "最新添加":
            all_customers = sorted(all_customers, key=lambda x: x.created_at, reverse=True)
        
        st.markdown(f"**共 {len(all_customers)} 位客户**")
        
        # 客户列表
        for c in all_customers[:20]:  # 最多显示20个
            with st.expander(f"{'🟢' if c.level == 'A级' else '🟡' if c.level == 'B级' else '🔴'} {c.name} | {c.interest_car or '未指定车型'} | {c.status}", expanded=False):
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown(f"**基本信息**")
                    st.write(f"- 手机尾号: {c.phone}")
                    st.write(f"- 来源: {c.source}")
                    st.write(f"- 等级: {c.level}")
                    st.write(f"- 预算: {c.budget or '未填写'}")
                    st.write(f"- 感兴趣: {c.interest_car or '未指定'}")
                with col2:
                    st.markdown(f"**跟进信息**")
                    st.write(f"- 状态: {c.status}")
                    st.write(f"- 创建时间: {c.created_at}")
                    st.write(f"- 下次跟进: {c.next_follow or '未设置'}")
                    
                    # 快速操作
                    if st.button("📝 添加跟进", key=f"follow_{c.id}"):
                        st.session_state[f"show_follow_{c.id}"] = True
                
                # 跟进记录
                if c.follow_records:
                    st.markdown("**跟进记录**")
                    for rec in c.follow_records[-3:]:
                        st.caption(f"  {rec['time']} [{rec['action']}]: {rec['content']}")
                
                # 跟进表单
                if st.session_state.get(f"show_follow_{c.id}", False):
                    with st.form(f"follow_form_{c.id}", clear_on_submit=True):
                        action = st.selectbox("跟进方式", ["通话", "微信", "短信", "面谈"])
                        content = st.text_area("跟进内容", placeholder="记录跟进情况...")
                        next_date = st.date_input("下次跟进日期")
                        if st.form_submit_button("保存"):
                            c.add_follow(action, content)
                            c.next_follow = str(next_date)
                            c.status = "跟进中"
                            st.success("跟进记录已保存!")
                            st.rerun()
    
    with tab2:
        # 新增客户表单
        with st.form("add_customer_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("客户姓名 *")
                new_phone = st.text_input("手机号 *")
                new_source = st.selectbox("客户来源", ["自然到店", "线上留资", "老客推荐", "展会活动", "电话咨询"])
            with col2:
                new_interest = st.selectbox("感兴趣车型", [""] + list(CAR_DATA.keys()))
                new_budget = st.selectbox("预算范围", ["", "15-20万", "20-25万", "25-30万", "30-40万", "40-50万", "50万以上"])
                new_level = st.selectbox("客户等级", ["A级", "B级", "C级"])
            
            new_intent = st.text_input("购车意图", placeholder="如:家用首选,商务接待...")
            new_remark = st.text_area("备注")
            
            col1, col2 = st.columns(2)
            with col1:
                first_follow = st.date_input("首次跟进日期")
            with col2:
                priority = st.selectbox("优先级", ["高", "中", "低"])
            
            submitted = st.form_submit_button("添加客户", type="primary", use_container_width=True)
            
            if submitted:
                if not new_name or not new_phone:
                    st.error("请填写必填项!")
                else:
                    new_customer = Customer(new_name, new_phone, new_source)
                    new_customer.level = new_level
                    new_customer.interest_car = new_interest
                    new_customer.budget = new_budget
                    new_customer.intent = new_intent
                    new_customer.remark = new_remark
                    new_customer.next_follow = str(first_follow)
                    if priority == "高":
                        new_customer.level = "A级"
                    customer_manager.add_customer(new_customer)
                    st.success(f"✅ 客户 {new_name} 已添加!")
                    st.rerun()

# ============================================================
# 客户画像
# ============================================================
elif page == "👥 客户画像":
    st.markdown('<div class="main-header">客户画像分析</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">精准识别客户需求,匹配最适合的车型</div>', unsafe_allow_html=True)
    
    # 选择要查看的客户画像
    profile_names = list(CUSTOMER_PROFILES.keys())
    selected_profile = st.selectbox("选择客户类型", profile_names)
    
    profile = CUSTOMER_PROFILES[selected_profile]
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        # 客户画像卡片
        st.markdown(f"### 👤 {selected_profile}")
        
        # 特征标签
        st.markdown("**🎯 客户特征**")
        features = profile.get('特征', [])
        st.markdown(" ".join([f'<span class="feature-tag">{f}</span>' for f in features]), unsafe_allow_html=True)
        
        st.markdown("**💬 话术重点**")
        tips = profile.get('话术重点', [])
        for t in tips:
            st.markdown(f"- {t}")
        
        # 销售建议
        st.markdown("**📋 销售建议**")
        sales_tips = {
            "科技极客": "强调参数对比,技术领先,OTA升级潜力",
            "家庭用户": "突出安全配置,空间宽敞,续航可靠",
            "商务精英": "展示豪华质感,品牌调性,乘坐舒适",
            "年轻首购": "强调性价比,用车成本低,颜值出众",
            "女性车主": "突出好停车,内饰精致,主动安全",
            "性能玩家": "展示加速成绩,赛道表现,操控乐趣",
        }
        st.info(sales_tips.get(selected_profile, "根据客户需求灵活应对"))
    
    with col2:
        st.markdown("**🚗 推荐车型**")
        recommended_cars = profile.get('推荐车型', [])
        
        for c in recommended_cars:
            car_data = CAR_DATA.get(c, {})
            if car_data:
                # 车型卡片
                car_imgs = get_car_images(c, 1)
                if car_imgs:
                    st.image(car_imgs[0], use_container_width=True, caption=c)
                
                st.markdown(f"**{c}** | {car_data.get('价格', '')}")
                
                # 配置列表
                configs = car_data.get('配置列表', [])
                if configs:
                    with st.expander("📋 配置选择"):
                        for cfg in configs[:3]:
                            st.markdown(f"- **{cfg['名称']}**: {cfg['价格']}万 - {cfg['特点']}")
                
                # 快捷操作
                op_cols = st.columns(2)
                with op_cols[0]:
                    if st.button(f"💬 咨询", key=f"ask_{c}"):
                        st.session_state.pending_input = f"我想了解{c}"
                        st.rerun()
                with op_cols[1]:
                    if st.button(f"📅 试驾", key=f"drive_{c}"):
                        st.session_state.pending_input = f"预约{c}试驾"
                        st.rerun()
                st.divider()
    
    st.markdown("---")
    
    # 全部客户画像概览 - 网格视图
    st.markdown("### 📊 全部客户画像")
    
    cols = st.columns(3)
    for i, (name, p) in enumerate(CUSTOMER_PROFILES.items()):
        with cols[i % 3]:
            # 使用颜色区分
            colors = {
                "科技极客": "#00d4ff",
                "家庭用户": "#00ff88",
                "商务精英": "#ffd700",
                "年轻首购": "#ff69b4",
                "女性车主": "#ff6b6b",
                "性能玩家": "#9b59b6",
            }
            color = colors.get(name, "#00d4ff")
            
            with st.container():
                st.markdown(f"""
                <div style="background: linear-gradient(145deg, #1e2328, #2a2f36); 
                            border-radius: 12px; padding: 1rem; 
                            border-left: 4px solid {color};">
                    <strong style="color: {color};">👤 {name}</strong>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"**特征**: {', '.join(p.get('特征', [])[:2])}")
                st.markdown(f"**推荐**: {', '.join(p.get('推荐车型', []))}")
                
                if st.button(f"查看详情", key=f"view_{name}"):
                    st.session_state.profile_selected = name

# ============================================================
# 试驾预约
# ============================================================
elif page == "📅 试驾预约":
    st.markdown('<div class="main-header">试驾预约</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">填写信息,预约最近的极氪中心试驾体验</div>', unsafe_allow_html=True)
    
    # 初始化预约数据
    if "appointments" not in st.session_state:
        st.session_state.appointments = []
    
    # 显示已预约列表
    if st.session_state.appointments:
        st.markdown("### 📋 已预约记录")
        for appt in st.session_state.appointments[-5:]:  # 只显示最近5条
            st.success(f"✅ {appt['name']} | {appt['car']} | {appt['date']} {appt['time']}")
    
    st.markdown("---")
    
    # 预约表单
    with st.form("test_drive_form", clear_on_submit=True):
        st.markdown("### 📝 预约信息")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("姓名", placeholder="请输入您的姓名")
            phone = st.text_input("手机号", placeholder="请输入手机号")
        with col2:
            car_model = st.selectbox("试驾车型", list(CAR_DATA.keys()))
            city = st.selectbox("所在城市", ["北京", "上海", "广州", "深圳", "杭州", "成都", "南京", "武汉", "西安", "重庆"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            test_date = st.date_input("试驾日期", min_value=datetime.now().date())
        with col2:
            time_options = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"]
            test_time = st.selectbox("试驾时间", time_options)
        with col3:
            experience_type = st.selectbox("体验类型", ["普通试驾", "深度试驾(2小时)", "对比试驾"])
        
        # 额外需求
        st.markdown("**额外需求(可选)**")
        col1, col2 = st.columns(2)
        with col1:
            has_license = st.checkbox("已取得驾照")
            need_pickup = st.checkbox("需要接送服务")
        with col2:
            prefer_female = st.checkbox("希望女性销售接待")
            bring_family = st.checkbox("计划带家人一起")
        
        remark = st.text_area("备注(可选)", placeholder="如有特殊需求请在此说明...")
        
        submitted = st.form_submit_button("提交预约", type="primary", use_container_width=True)
        
        if submitted:
            if not name or not phone:
                st.error("请填写姓名和手机号!")
            else:
                appointment = {
                    "name": name,
                    "phone": phone[-4:],  # 只保存后4位
                    "car": car_model,
                    "city": city,
                    "date": str(test_date),
                    "time": test_time,
                    "type": experience_type,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.appointments.append(appointment)
                
                st.success("🎉 预约成功!")
                st.info(f"""
                **预约确认**
                - 姓名: {name}
                - 车型: {car_model}
                - 城市: {city}
                - 日期: {test_date} {test_time}
                
                我们的销售顾问将在24小时内联系您确认详情!
                """)
                
                # 显示推荐车型图片
                car_imgs = get_car_images(car_model, 2)
                if car_imgs:
                    st.image(car_imgs[0], caption=f"{car_model} - 期待您的试驾体验!", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📍 极氪中心分布")
    
    # 显示门店信息
    stores = {
        "北京": ["极氪中心·北京东方广场", "极氪空间·北京朝阳大悦城"],
        "上海": ["极氪中心·上海中心大厦", "极氪空间·上海环球港"],
        "广州": ["极氪中心·广州太古汇", "极氪空间·广州天河城"],
        "深圳": ["极氪中心·深圳万象城", "极氪空间·深圳海岸城"],
        "杭州": ["极氪中心·杭州大厦", "极氪空间·杭州龙湖天街"],
    }
    
    cols = st.columns(3)
    for i, (city_name, store_list) in enumerate(stores.items()):
        with cols[i % 3]:
            with st.expander(f"📍 {city_name}", expanded=False):
                for store in store_list:
                    st.write(f"- {store}")

# ============================================================
# 数据看板
# ============================================================
elif page == "📈 数据看板":
    st.markdown('<div class="main-header">销售数据分析看板</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">实时分析客户咨询数据,优化销售策略</div>', unsafe_allow_html=True)
    
    # 从真实CRM数据源获取统计
    # 1. 统计客户数据
    all_customers = customer_manager.get_all_customers()
    total_customers = len(all_customers)
    
    # 2. 按意向车型统计热度
    car_interest_count = {}
    intent_stats = {"家用": 0, "商务": 0, "科技": 0, "性能": 0, "女性": 0}
    age_stats = {"25-30岁": 0, "30-35岁": 0, "35-40岁": 0, "40岁以上": 0}
    
    for c in all_customers:
        # 车型统计
        car = c.purchase_interest.get("target_car", "")
        if car:
            car_interest_count[car] = car_interest_count.get(car, 0) + 1
        
        # 意向统计
        intent = c.purchase_interest.get("primary_need", "")
        for key in intent_stats:
            if key in intent:
                intent_stats[key] += 1
        
        # 年龄统计
        age = c.purchase_interest.get("age_group", "")
        if age in age_stats:
            age_stats[age] += 1
    
    # 确保所有车型都在统计中
    for car in CAR_DATA.keys():
        if car not in car_interest_count:
            car_interest_count[car] = 0
    
    # 3. 统计聊天记录中的咨询热度
    chat_car_mentions = {}
    if "chat_history" in st.session_state:
        for msg in st.session_state.chat_history:
            content = msg.get("content", "")
            for car in CAR_DATA.keys():
                if car in content:
                    chat_car_mentions[car] = chat_car_mentions.get(car, 0) + 1
    
    # 合并车型热度（购买意向 + 聊天咨询）
    combined_car_interest = {}
    for car in CAR_DATA.keys():
        purchase_count = car_interest_count.get(car, 0)
        chat_count = chat_car_mentions.get(car, 0)
        combined_car_interest[car] = purchase_count * 5 + chat_count  # 购买意向权重更高
    
    # 4. 统计预约试驾
    test_drives = [c for c in all_customers if c.purchase_interest.get("test_drive")]
    test_drive_count = len(test_drives)
    
    # 真实数据看板
    data = {
        "total_customers": total_customers,
        "total_test_drives": test_drive_count,
        "chat_sessions": len(st.session_state.get("chat_history", [])) // 2 if "chat_history" in st.session_state else 0,
        "top_cars": combined_car_interest,
        "intent_distribution": intent_stats,
        "age_distribution": age_stats,
    }
    
    # 核心指标
    st.markdown("### 📊 核心指标")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("潜客总数", f"{data['total_customers']}", f"+{total_customers}人")
    with col2:
        st.metric("预约试驾", f"{data['total_test_drives']}", f"+{test_drive_count}人")
    with col3:
        st.metric("咨询会话", f"{data['chat_sessions']}", "本次")
    with col4:
        st.metric("在售车型", f"{len(CAR_DATA)}", "款")
    
    st.markdown("---")
    
    # 车型热度
    st.markdown("### 🚗 车型热度分析")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**购买意向排名**")
        top_cars = data["top_cars"]
        total_interest = sum(top_cars.values())
        if total_interest > 0:
            sorted_cars = sorted(top_cars.items(), key=lambda x: x[1], reverse=True)
            for i, (car, count) in enumerate(sorted_cars, 1):
                percentage = count / total_interest * 100 if total_interest > 0 else 0
                st.progress(percentage / 100, text=f"{i}. {car}: {count}分")
        else:
            st.info("暂无购买意向数据，请先在CRM中添加客户")
    
    with col2:
        st.markdown("**客户意向分布**")
        intent_data = data["intent_distribution"]
        total_intent = sum(intent_data.values())
        if total_intent > 0:
            intent_df = pd.DataFrame([
                {"意向": k, "数量": v} for k, v in intent_data.items()
            ])
            st.bar_chart(intent_df.set_index("意向"))
        else:
            st.info("暂无意向数据，请在CRM中添加客户")
    
    st.markdown("---")
    
    # 客户画像分布
    st.markdown("### 👥 客户画像分布")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**年龄分布**")
        age_data = data["age_distribution"]
        total_age = sum(age_data.values())
        if total_age > 0:
            age_df = pd.DataFrame([
                {"年龄段": k, "数量": v} for k, v in age_data.items()
            ])
            st.bar_chart(age_df.set_index("年龄段"))
        else:
            st.info("暂无年龄数据")
    
    with col2:
        st.markdown("**车型咨询热度**")
        # 基于真实聊天记录统计
        if chat_car_mentions and sum(chat_car_mentions.values()) > 0:
            chat_df = pd.DataFrame([
                {"车型": k, "咨询次数": v} for k, v in chat_car_mentions.items()
            ])
            st.bar_chart(chat_df.set_index("车型"))
        else:
            st.info("暂无咨询数据，多使用卖车助手增加统计")
    
    st.markdown("---")
    
    # 销售机会
    st.markdown("### 🎯 销售机会与建议")
    
    # 根据真实数据生成推荐
    total_interest = sum(top_cars.values())
    hot_car = max(top_cars.items(), key=lambda x: x[1])[0] if top_cars else "暂无"
    hot_need = max(intent_stats.items(), key=lambda x: x[1])[0] if intent_stats else "暂无"
    
    col1, col2 = st.columns(2)
    with col1:
        if total_interest > 0:
            st.success(f"""
            **最热车型**: {hot_car}
            热度积分 {top_cars.get(hot_car, 0)}分
            
            **建议**: 加大库存备货
            """)
        else:
            st.info("暂无车型热度数据，请在CRM中添加客户购买意向")
    
    with col2:
        if sum(intent_stats.values()) > 0:
            st.info(f"""
            **最高需求**: {hot_need}
            客户数量 {intent_stats.get(hot_need, 0)}人
            
            **建议**: 优化对应话术
            """)
        else:
            st.info("暂无需求数据，请在CRM中添加客户需求")
    
    st.markdown("---")
    
    # 销售机会 - 补充建议
    st.markdown("### 📋 运营建议")
    
    suggestions = [
        ("🌅 早间提醒", "建议10点前发送问候信息,客户回复率更高"),
        ("📱 周末跟进", "周末客户决策更放松,是跟进的好时机"),
        ("🎁 限时优惠", "设置7天有效期优惠,促单利器"),
        ("👥 老带新", "已购车客户推荐新客户,可给予积分奖励"),
    ]
    
    cols = st.columns(4)
    for i, (title, desc) in enumerate(suggestions):
        with cols[i]:
            with st.container():
                st.markdown(f"**{title}**")
                st.caption(desc)
    
    with col3:
        conv_rate = data['conversion_rate']
        st.warning(f"""
        **转化率**: {conv_rate}%
        较上周 +2.1%
        
        **建议**: 跟进未成交客户
        """)
    
    # 导出数据
    st.markdown("---")
    st.markdown("### 数据操作")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("导出分析报告", use_container_width=True):
            report_data = {
                "导出时间": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "核心指标": data,
                "车型热度": data["top_cars"],
                "意图分布": data["intent_distribution"],
            }
            st.json(report_data)
            st.success("报告已生成!")
    
    with col2:
        if st.button("重置模拟数据", use_container_width=True):
            st.session_state.analytics_data = {
                "total_queries": 1256,
                "total_recommendations": 892,
                "avg_session_length": 4.5,
                "top_cars": {"ZEEKR 7X": 35, "ZEEKR 007": 28, "ZEEKR 009": 18, "ZEEKR 001": 12, "ZEEKR X": 5, "ZEEKR 001 FR": 2},
                "intent_distribution": {"家用推荐": 30, "商务推荐": 20, "科技推荐": 25, "性能推荐": 10, "女性推荐": 15},
                "age_distribution": {"25-30岁": 35, "30-35岁": 40, "35-40岁": 15, "40岁以上": 10},
                "conversion_rate": 23.5,
                "weekly_trend": [45, 52, 48, 61, 58, 67, 72],
            }
            st.rerun()

# ============================================================
# 购车指南
# ============================================================
elif page == "📖 购车指南":
    st.markdown('<div class="main-header">购车指南</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">新能源购车全攻略 · 常见问题解答</div>', unsafe_allow_html=True)
    
    # 标签页
    tab1, tab2, tab3, tab4 = st.tabs(["🚗 购车流程", "⚡ 用车知识", "💰 费用说明", "❓ 常见问题"])
    
    with tab1:
        st.markdown("### 📋 极氪购车流程")
        
        steps = [
            ("1️⃣ 预约试驾", "联系销售顾问预约到店试驾,体验车型操控和功能", "建议试驾时长30-60分钟,带好身份证和驾照"),
            ("2️⃣ 确定配置", "根据预算和使用需求,选择合适的车型和配置", "可以多次试驾对比不同配置"),
            ("3️⃣ 下定锁单", "在极氪App或官网下定,支付定金锁单", "定金通常为5000-10000元"),
            ("4️⃣ 等待交付", "根据车型和配置,等待工厂排产和运输", "热门车型可能需要等待1-3个月"),
            ("5️⃣ 验车提车", "到店验车,检查外观内饰功能,支付尾款", "建议带上老司机帮忙验车"),
            ("6️⃣ 安装充电桩", "预约安装家用充电桩,享受便捷充电", "极氪赠送充电桩和安装服务"),
        ]
        
        for step_name, desc, tip in steps:
            with st.expander(step_name, expanded=True):
                st.markdown(f"**{desc}**")
                st.info(f"💡 小贴士: {tip}")
        
        st.markdown("---")
        st.markdown("### ⏱️ 预计时间线")
        
        timeline_data = {
            "阶段": ["试驾到下定", "下定到交付", "安装充电桩", "总计"],
            "最快": ["1天", "2周", "1周", "约3周"],
            "常规": ["3天", "1个月", "2周", "约1.5个月"],
            "热门车型": ["1周", "2-3个月", "2周", "约3-4个月"],
        }
        st.dataframe(pd.DataFrame(timeline_data), use_container_width=True, hide_index=True)
    
    with tab2:
        st.markdown("### ⚡ 新能源用车知识")
        
        faq_sections = {
            "充电相关": [
                ("家用慢充", "随车赠送7kW家用充电桩,约8-12小时充满,适合夜间预约充电"),
                ("直流快充", "极氪自建超充站,最高功率360kW,15-30分钟可充至80%"),
                ("公共充电", "支持国家电网,特来电等公共充电桩,充电速度取决于桩的功率"),
                ("充电费用", "家用约0.5元/度,百公里费用约10元；公共约1-1.5元/度"),
            ],
            "续航相关": [
                ("CLTC续航", "中国轻型汽车行驶工况测试标准,比NEDC更接近实际续航"),
                ("影响续航因素", "高速行驶,空调使用,低温环境都会降低实际续航"),
                ("里程焦虑", "提前规划行程,使用导航规划充电站,长途出行无忧"),
                ("电池衰减", "极氪提供首任车主终身质保,电池衰减至80%以下可免费更换"),
            ],
            "智能功能": [
                ("OTA升级", "极氪支持整车OTA远程升级,功能持续迭代,常用常新"),
                ("浩瀚智驾", "L2+级辅助驾驶,支持自动泊车,车道保持,自动变道"),
                ("远程控制", "通过极氪App远程解锁,空调预热,查看车辆状态"),
                ("车机系统", "基于Android定制,操作流畅,应用生态丰富"),
            ],
        }
        
        for section, items in faq_sections.items():
            st.markdown(f"#### {section}")
            for q, a in items:
                with st.expander(f"❓ {q}"):
                    st.markdown(a)
    
    with tab3:
        st.markdown("### 💰 购车费用说明")
        
        # 必选费用
        st.markdown("#### 📌 必选费用")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**指导价**")
            st.markdown("- 车型官方指导价")
            st.markdown("- 部分车型有置换补贴")
            st.markdown("- 旧车报废有补贴")
        with col2:
            st.markdown("**保险费用**")
            st.markdown("- 交强险: 950元")
            st.markdown("- 商业险: 约6000-12000元")
            st.markdown("- 按车型价格浮动")
        
        st.markdown("#### 省钱项目")
        st.success("""
        **新能源专属优惠**
        - 免购置税(节省1-7万元)
        - 免车船税(每年节省数百元)
        - 免费安装充电桩(价值2000-5000元)
        - 部分城市免限行(上海,北京等)
        - 免停车费(部分城市政策)
        """)
        
        st.markdown("#### 📊 用车成本对比")
        compare_cost = {
            "项目": ["百公里电耗/油耗", "百公里费用", "年保养费用", "保险费用"],
            "极氪电动车": ["15kWh", "约7.5元", "约500元", "约6000元"],
            "同价位燃油车": ["8L", "约64元", "约3000元", "约4000元"],
        }
        st.dataframe(pd.DataFrame(compare_cost), use_container_width=True, hide_index=True)
        
        st.info("💡 按年行驶2万公里计算,极氪每年可节省约**1.5-2万元**用车费用!")
    
    with tab4:
        st.markdown("### ❓ 常见问题")
        
        qa_list = [
            ("极氪是哪个品牌的?", "极氪是吉利集团旗下的高端纯电品牌,成立于2021年.极氪品牌定位高端智能化,主打30万级以上纯电市场."),
            ("极氪的售后服务怎么样?", "极氪提供终身质保,终身道路救援,专属客服等服务.门店覆盖全国主要城市,售后服务有保障."),
            ("新能源车上牌需要什么条件?", "大部分城市只需有购车资格(社保/居住证)即可上牌.部分限购城市需要参与摇号或竞价获取牌照指标."),
            ("充电桩安装麻烦吗?", "极氪提供一站式安装服务,预约后会有专业人员上门安装.需要有固定停车位(产权或长租车位)并获得物业同意."),
            ("极氪能跑长途吗?", "极氪车型续航普遍超过600km,配合自建超充站和公共充电网络,长途出行完全可行.提前规划好充电路线即可."),
            ("选购哪个配置最划算?", "入门版配置已经非常丰富(8155芯片,辅助驾驶等),如果不是特别追求续航或性能,入门版性价比最高."),
            ("旧车置换有补贴吗?", "极氪提供旧车置换补贴,根据旧车类型和品牌不同,补贴金额在3000-10000元不等.部分城市还有额外补贴."),
            ("订车后能退吗?", "下定锁单后,定金通常不可退.建议在下定前充分试驾确认,有疑问可与销售顾问沟通特殊情况."),
        ]
        
        for q, a in qa_list:
            with st.expander(f"❓ {q}"):
                st.markdown(a)
        
        st.markdown("---")
        st.markdown("### 📞 联系我们")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.success("📞 客服热线\n400-888-8888\n工作日 9:00-21:00")
        with col2:
            st.info("💬 在线客服\n极氪App内\n实时咨询")
        with col3:
            st.warning("📍 门店查询\n极氪App内\n附近门店导航")
