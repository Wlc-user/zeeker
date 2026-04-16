"""
用户认证模块
包含：注册、登录、忘记密码、邮箱验证
使用Streamlit Session State存储用户数据
"""
import streamlit as st
import hashlib
import time
import random
import re
from datetime import datetime, timedelta

# ============================================================
# 用户数据存储 (使用Session State模拟数据库)
# ============================================================

def init_auth_data():
    """初始化认证数据"""
    if "users" not in st.session_state:
        st.session_state.users = {
            # 默认管理员账户 (密码: admin123)
            "admin@zeeker.com": {
                "password": hashlib.sha256("admin123".encode()).hexdigest(),
                "name": "管理员",
                "email": "admin@zeeker.com",
                "verified": True,
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "role": "admin"
            }
        }
    
    if "verification_codes" not in st.session_state:
        st.session_state.verification_codes = {}  # {"email": {"code": "123456", "expires": timestamp}}
    
    if "reset_tokens" not in st.session_state:
        st.session_state.reset_tokens = {}  # {"token": {"email": "...", "expires": timestamp}}

def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_verification_code() -> str:
    """生成6位验证码"""
    return str(random.randint(100000, 999999))

def generate_reset_token(email: str) -> str:
    """生成密码重置令牌"""
    token = hashlib.md5(f"{email}{time.time()}".encode()).hexdigest()[:32]
    st.session_state.reset_tokens[token] = {
        "email": email,
        "expires": time.time() + 1800  # 30分钟有效期
    }
    return token

def is_valid_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_code_expired(email: str) -> bool:
    """检查验证码是否过期"""
    if email not in st.session_state.verification_codes:
        return True
    record = st.session_state.verification_codes[email]
    return time.time() > record["expires"]

# ============================================================
# 认证函数
# ============================================================

def register(name: str, email: str, password: str, confirm_password: str) -> tuple:
    """
    用户注册
    返回: (success: bool, message: str)
    """
    # 验证输入
    if not name or len(name.strip()) < 2:
        return False, "姓名至少2个字符"
    
    if not is_valid_email(email):
        return False, "请输入有效的邮箱地址"
    
    if email in st.session_state.users:
        return False, "该邮箱已注册，请直接登录"
    
    if len(password) < 6:
        return False, "密码至少6个字符"
    
    if password != confirm_password:
        return False, "两次输入的密码不一致"
    
    # 创建用户
    st.session_state.users[email] = {
        "password": hash_password(password),
        "name": name.strip(),
        "email": email,
        "verified": False,  # 需要邮箱验证
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "role": "user"
    }
    
    # 生成验证码
    code = generate_verification_code()
    st.session_state.verification_codes[email] = {
        "code": code,
        "expires": time.time() + 300  # 5分钟有效期
    }
    
    # 发送验证码（模拟，实际应发送邮件）
    send_verification_email(email, code)
    
    return True, f"注册成功！验证码已发送至 {email}，请查收。"

def send_verification_email(email: str, code: str):
    """
    发送验证邮件（模拟）
    实际项目中应集成真实的邮件服务（如SendGrid、QQ邮箱SMTP等）
    """
    # 在控制台输出模拟邮件内容
    print(f"\n{'='*50}")
    print(f"📧 模拟邮件 - 验证邮箱")
    print(f"收件人: {email}")
    print(f"验证码: {code}")
    print(f"有效期: 5分钟")
    print(f"{'='*50}\n")
    
    # 显示在界面上（开发模式）
    st.info(f"📧 验证码已发送至 **{email}**\n\n开发模式显示验证码: **{code}**")

def verify_email(email: str, code: str) -> tuple:
    """
    验证邮箱
    返回: (success: bool, message: str)
    """
    if email not in st.session_state.users:
        return False, "用户不存在"
    
    if st.session_state.users[email].get("verified", False):
        return True, "邮箱已验证"
    
    if is_code_expired(email):
        return False, "验证码已过期，请重新获取"
    
    record = st.session_state.verification_codes.get(email, {})
    if record.get("code") != code:
        return False, "验证码错误"
    
    # 验证成功
    st.session_state.users[email]["verified"] = True
    del st.session_state.verification_codes[email]
    
    return True, "邮箱验证成功！"

def resend_verification_code(email: str) -> tuple:
    """重新发送验证码"""
    if email not in st.session_state.users:
        return False, "用户不存在"
    
    if st.session_state.users[email].get("verified", False):
        return True, "邮箱已验证，无需重复验证"
    
    # 生成新验证码
    code = generate_verification_code()
    st.session_state.verification_codes[email] = {
        "code": code,
        "expires": time.time() + 300
    }
    
    send_verification_email(email, code)
    return True, "验证码已重新发送"

def login(email: str, password: str) -> tuple:
    """
    用户登录
    返回: (success: bool, message: str)
    """
    if not is_valid_email(email):
        return False, "请输入有效的邮箱地址"
    
    if email not in st.session_state.users:
        return False, "账号不存在，请先注册"
    
    user = st.session_state.users[email]
    
    if user["password"] != hash_password(password):
        return False, "密码错误"
    
    # 检查是否验证
    if not user.get("verified", False):
        # 自动发送验证码
        code = generate_verification_code()
        st.session_state.verification_codes[email] = {
            "code": code,
            "expires": time.time() + 300
        }
        send_verification_email(email, code)
        return False, f"请先验证邮箱，验证码已发送至 {email}"
    
    # 更新登录时间
    st.session_state.users[email]["last_login"] = datetime.now().isoformat()
    
    # 设置登录状态
    st.session_state.authenticated = True
    st.session_state.current_user = {
        "email": email,
        "name": user["name"],
        "role": user.get("role", "user")
    }
    
    return True, f"欢迎回来，{user['name']}！"

def logout():
    """用户登出"""
    st.session_state.authenticated = False
    st.session_state.current_user = None

def forgot_password(email: str) -> tuple:
    """
    忘记密码 - 发送重置链接
    返回: (success: bool, message: str)
    """
    if not is_valid_email(email):
        return False, "请输入有效的邮箱地址"
    
    if email not in st.session_state.users:
        # 为了安全，不提示用户是否存在
        return True, "如果该邮箱已注册，重置链接已发送至您的邮箱"
    
    # 生成重置令牌
    token = generate_reset_token(email)
    
    # 模拟发送重置邮件
    reset_link = f"https://zeeker-app.com/reset-password?token={token}"
    print(f"\n{'='*50}")
    print(f"📧 模拟邮件 - 重置密码")
    print(f"收件人: {email}")
    print(f"重置链接: {reset_link}")
    print(f"有效期: 30分钟")
    print(f"{'='*50}\n")
    
    st.info(f"🔗 密码重置链接已发送至 **{email}**\n\n开发模式显示链接: `{reset_link}`")
    
    return True, "如果该邮箱已注册，重置链接已发送至您的邮箱"

def reset_password(token: str, new_password: str, confirm_password: str) -> tuple:
    """
    重置密码
    返回: (success: bool, message: str)
    """
    if token not in st.session_state.reset_tokens:
        return False, "重置链接无效或已过期"
    
    record = st.session_state.reset_tokens[token]
    
    if time.time() > record["expires"]:
        del st.session_state.reset_tokens[token]
        return False, "重置链接已过期，请重新申请"
    
    email = record["email"]
    
    if len(new_password) < 6:
        return False, "密码至少6个字符"
    
    if new_password != confirm_password:
        return False, "两次输入的密码不一致"
    
    # 更新密码
    st.session_state.users[email]["password"] = hash_password(new_password)
    del st.session_state.reset_tokens[token]
    
    return True, "密码重置成功，请使用新密码登录"

def change_password(email: str, old_password: str, new_password: str) -> tuple:
    """
    修改密码（已登录用户）
    """
    if email not in st.session_state.users:
        return False, "用户不存在"
    
    user = st.session_state.users[email]
    
    if user["password"] != hash_password(old_password):
        return False, "原密码错误"
    
    if len(new_password) < 6:
        return False, "新密码至少6个字符"
    
    st.session_state.users[email]["password"] = hash_password(new_password)
    
    return True, "密码修改成功"

def get_current_user():
    """获取当前登录用户"""
    return st.session_state.get("current_user")

def is_authenticated():
    """检查是否已登录"""
    return st.session_state.get("authenticated", False)

def require_auth():
    """要求用户已登录，否则重定向到登录页"""
    if not is_authenticated():
        st.warning("请先登录后访问")
        st.session_state.show_login = True
        st.rerun()
