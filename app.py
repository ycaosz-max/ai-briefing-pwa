import streamlit as st
from openai import OpenAI
import os
import tempfile
import json
from datetime import datetime

# ========== v3.7.0：流程精简、减少冗余步骤 ==========
VERSION = "3.7.0"

CONFIG = {
    "version": VERSION,
    "api": {
        "base_url": "https://api.siliconflow.cn/v1",
        "timeout": 60
    },
    "models": {
        "transcribe": "FunAudioLLM/SenseVoiceSmall",
        "generate": "deepseek-ai/DeepSeek-V3"
    },
    "theme": {
        "light": {
            "bg_primary": "#ffffff",
            "bg_secondary": "#f0f2f6",
            "bg_card": "#ffffff",
            "text_primary": "#1f1f1f",
            "text_secondary": "#666666",
            "border_color": "#e0e0e0",
            "accent_color": "#FF6B6B",
            "accent_hover": "#FF5252",
            "shadow": "rgba(255, 107, 107, 0.15)",
            "input_bg": "#ffffff",
            "input_text": "#1f1f1f",
            "button_text": "#ffffff"
        },
        "dark": {
            "bg_primary": "#000000",
            "bg_secondary": "#1c1c1e",
            "bg_card": "#2c2c2e",
            "text_primary": "#ffffff",
            "text_secondary": "#8e8e93",
            "border_color": "#38383a",
            "accent_color": "#FF8585",
            "accent_hover": "#FF6B6B",
            "shadow": "rgba(255, 133, 133, 0.15)",
            "input_bg": "#1c1c1e",
            "input_text": "#ffffff",
            "button_text": "#ffffff"
        }
    }
}

# ========== PWA配置（必须在最前面）==========
st.markdown(f"""
<!-- PWA Manifest -->
<link rel="manifest" href="data:application/json;base64,eyJuYW1lIjogIkFJ6K+F6K665YWs5a+DIiwgInNob3J0X25hbWUiOiAiQUlTVCIsICJzdGFydF91cmwiOiAiLiIsICJkaXNwbGF5IjogInN0YW5kYWxvbmUiLCAiYmFja2dyb3VuZF9jb2xvciI6ICIjRkY2QjZCIiwgInRoZW1lX2NvbG9yIjogIiNGRjZCNkIiLCAiaWNvbnMiOiBbeyJzcmMiOiAiZGF0YTppbWFnZS9zdmcreG1sLCUzQ3N2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHZpZXdCb3g9JzAgMCAxMDAgMTAwJyUzRSUzQ3RleHQgeT0nLjllbScgZm9udC1zaXplPSc5MCclM0Xwn5OeJTNFL3RleHQlM0UlM0Mvc3ZnJTNFIn1dfQ==">

<!-- iOS PWA配置 -->
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="AI简报">

<!-- Emoji图标 -->
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎙️</text></svg>">
<link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎙️</text></svg>">

<!-- 主题色适配 -->
<meta name="theme-color" content="{CONFIG['theme']['light']['accent_color']}" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="{CONFIG['theme']['dark']['bg_secondary']}" media="(prefers-color-scheme: dark)">

<!-- Service Worker注册 -->
<script>
const swCode = `self.addEventListener('install', e => {{ self.skipWaiting(); }}); self.addEventListener('activate', e => {{ self.clients.claim(); }}); self.addEventListener('fetch', e => {{ e.respondWith(fetch(e.request).catch(() => new Response('离线模式：请检查网络连接', {{headers: {{'Content-Type': 'text/html'}}}}))); }});`;
if ('serviceWorker' in navigator) {{
  navigator.serviceWorker.register('data:text/javascript;base64,' + btoa(swCode))
    .then(reg => console.log('SW注册成功'))
    .catch(err => console.log('SW注册失败', err));
}}
</script>
""", unsafe_allow_html=True)

# ========== 页面设置 ==========
st.set_page_config(
    page_title="AI语音简报助手", 
    page_icon="🎙️"
)

# ========== v2.6.0：CSS 全面优化 ==========
st.markdown(f"""
<style>
/* ========== 基础变量定义 ========== */
:root {{
    --bg-primary: {CONFIG['theme']['light']['bg_primary']};
    --bg-secondary: {CONFIG['theme']['light']['bg_secondary']};
    --bg-card: {CONFIG['theme']['light']['bg_card']};
    --text-primary: {CONFIG['theme']['light']['text_primary']};
    --text-secondary: {CONFIG['theme']['light']['text_secondary']};
    --border-color: {CONFIG['theme']['light']['border_color']};
    --accent-color: {CONFIG['theme']['light']['accent_color']};
    --accent-hover: {CONFIG['theme']['light']['accent_hover']};
    --shadow: {CONFIG['theme']['light']['shadow']};
    --input-bg: {CONFIG['theme']['light']['input_bg']};
    --input-text: {CONFIG['theme']['light']['input_text']};
    --button-text: {CONFIG['theme']['light']['button_text']};
}}

/* ========== iOS 暗黑模式 ========== */
@media (prefers-color-scheme: dark) {{
    :root {{
        --bg-primary: {CONFIG['theme']['dark']['bg_primary']};
        --bg-secondary: {CONFIG['theme']['dark']['bg_secondary']};
        --bg-card: {CONFIG['theme']['dark']['bg_card']};
        --text-primary: {CONFIG['theme']['dark']['text_primary']};
        --text-secondary: {CONFIG['theme']['dark']['text_secondary']};
        --border-color: {CONFIG['theme']['dark']['border_color']};
        --accent-color: {CONFIG['theme']['dark']['accent_color']};
        --accent-hover: {CONFIG['theme']['dark']['accent_hover']};
        --shadow: {CONFIG['theme']['dark']['shadow']};
        --input-bg: {CONFIG['theme']['dark']['input_bg']};
        --input-text: {CONFIG['theme']['dark']['input_text']};
        --button-text: {CONFIG['theme']['dark']['button_text']};
    }}
    .stApp {{ background-color: var(--bg-primary) !important; }}
    .stTextInput input, .stTextArea textarea {{
        background-color: var(--input-bg) !important;
        color: var(--input-text) !important;
        border-color: var(--border-color) !important;
    }}
    .stSelectbox > div > div {{
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }}
    .stExpander {{
        background-color: var(--bg-card) !important;
        border-color: var(--border-color) !important;
    }}
    .stMarkdown {{ color: var(--text-primary) !important; }}
    .section-card {{ background-color: var(--bg-card) !important; }}
}}

/* ========== iOS 基础修复 ========== */
* {{
    -webkit-tap-highlight-color: transparent;
    -webkit-touch-callout: none;
}}

/* ========== 全局 ========== */
.stApp {{
    background-color: var(--bg-primary);
    color: var(--text-primary);
}}

/* ========== 页头（渐变背景） ========== */
.header-area {{
    padding: 20px 16px 14px 16px;
    background: linear-gradient(135deg, rgba(255,107,107,0.07) 0%, transparent 60%);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    margin-bottom: 18px;
}}
.big-title {{
    font-size: 30px;
    font-weight: 700;
    color: var(--accent-color);
    margin-bottom: 4px;
    letter-spacing: -0.5px;
}}
.subtitle {{
    font-size: 14px;
    color: var(--text-secondary);
    margin-bottom: 14px;
}}

/* ========== 三步流程指示条 ========== */
.steps-bar {{
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 4px;
}}
.step-item {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 12px;
    border-radius: 20px;
    background-color: var(--bg-secondary);
    border: 1px solid var(--border-color);
    font-size: 12px;
    font-weight: 500;
    color: var(--text-secondary);
}}
.step-arrow {{
    font-size: 13px;
    color: var(--border-color);
    font-weight: 300;
}}

/* ========== 区块卡片 ========== */
.section-card {{
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
}}
.section-card-title {{
    font-size: 13px;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
}}

/* ========== 统计徽章 ========== */
.stat-badge {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 12px;
    background-color: rgba(255, 107, 107, 0.1);
    color: var(--accent-color);
    font-size: 12px;
    font-weight: 500;
    margin-bottom: 10px;
}}

/* ========== 输入框 ========== */
.stTextInput input, .stTextArea textarea {{
    -webkit-appearance: none !important;
    -webkit-user-select: text !important;
    user-select: text !important;
    font-size: 16px !important;
    touch-action: manipulation;
    border-radius: 10px;
    background-color: var(--input-bg);
    color: var(--input-text);
    border: 1px solid var(--border-color);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    outline: none !important;
    border-color: var(--accent-color) !important;
    box-shadow: 0 0 0 3px var(--shadow) !important;
}}

/* ========== 按钮 ========== */
.stButton button {{
    -webkit-appearance: none;
    touch-action: manipulation;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--accent-color) 0%, var(--accent-hover) 100%) !important;
    color: var(--button-text) !important;
    border: none !important;
    font-weight: 600;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
.stButton button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 4px 14px var(--shadow);
}}
.stButton button:active {{ transform: translateY(0); }}

.stDownloadButton button {{
    background: transparent !important;
    color: var(--accent-color) !important;
    border: 1.5px solid var(--accent-color) !important;
    border-radius: 10px;
    font-weight: 600;
}}
.stDownloadButton button:hover {{
    background: var(--accent-color) !important;
    color: var(--button-text) !important;
}}

/* ========== 其他 Streamlit 组件 ========== */
.stExpander {{
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    overflow: hidden;
}}
.stAlert {{
    background-color: var(--bg-card) !important;
    border-color: var(--border-color) !important;
    color: var(--text-primary) !important;
}}
.stInfo {{ background-color: rgba(255, 107, 107, 0.08) !important; border-left-color: var(--accent-color) !important; }}
.stSuccess {{ background-color: rgba(48, 209, 88, 0.08) !important; border-left-color: #30d158 !important; }}
.stWarning {{ background-color: rgba(255, 159, 10, 0.08) !important; border-left-color: #ff9f0a !important; }}
.stError {{ background-color: rgba(255, 69, 58, 0.08) !important; border-left-color: #ff453a !important; }}
.stFileUploader > div > div {{
    background-color: var(--bg-secondary) !important;
    border-color: var(--border-color) !important;
    color: var(--text-primary) !important;
}}
.stSelectbox > div > div {{
    background-color: var(--bg-card);
    border-color: var(--border-color) !important;
    color: var(--text-primary);
    border-radius: 10px;
}}
hr {{ border-color: var(--border-color) !important; }}

/* ========== 移动端响应式：列堆叠 ========== */
@media (max-width: 768px) {{
    [data-testid="stHorizontalBlock"] {{ flex-wrap: wrap !important; }}
    [data-testid="stColumn"] {{
        width: 100% !important;
        flex: 1 0 100% !important;
        min-width: 100% !important;
    }}
    .big-title {{ font-size: 24px !important; }}
    .subtitle {{ font-size: 13px !important; }}
    .main .block-container {{ padding: 0.8rem !important; }}
    .stApp {{ padding-bottom: env(safe-area-inset-bottom); }}
    .step-item {{ font-size: 11px; padding: 4px 9px; }}
}}

@media (display-mode: standalone) {{
    .main .block-container {{ padding-top: 1.5rem; }}
}}

/* ========== 结果区排版 ========== */
[data-testid="stTabs"] .stMarkdown p {{
    line-height: 1.85;
    margin-bottom: 10px;
    color: var(--text-primary);
}}
[data-testid="stTabs"] .stMarkdown li {{
    line-height: 1.75;
    margin-bottom: 4px;
    color: var(--text-primary);
}}
[data-testid="stTabs"] .stMarkdown h1,
[data-testid="stTabs"] .stMarkdown h2 {{
    font-size: 17px;
    font-weight: 700;
    color: var(--accent-color);
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 6px;
    margin: 18px 0 10px 0;
}}
[data-testid="stTabs"] .stMarkdown h3 {{
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 14px 0 6px 0;
}}
[data-testid="stTabs"] .stMarkdown strong {{
    font-weight: 700;
    color: var(--text-primary);
}}

/* ========== 字数显示 ========== */
.char-count {{
    font-size: 12px;
    color: var(--text-secondary);
    text-align: right;
    margin-top: -4px;
    margin-bottom: 10px;
}}

/* ========== iPhone 提示卡片 ========== */
.tip-card {{
    background-color: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-left: 3px solid var(--accent-color);
    border-radius: 10px;
    padding: 11px 14px;
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.7;
    margin-bottom: 10px;
}}
.tip-card b {{ color: var(--text-primary); }}

/* ========== st.status 容器 ========== */
[data-testid="stStatusWidget"] {{
    border-radius: 12px !important;
    border-color: var(--border-color) !important;
}}

* {{ transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease; }}

/* ========== st.code() → 纯复制按钮（隐藏文本内容）========== */
[data-testid="stCode"] pre {{
    height: 0 !important;
    min-height: 0 !important;
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
}}
[data-testid="stCode"] {{
    position: relative !important;
    min-height: 2.75rem !important;
    background: rgba(255, 107, 107, 0.06) !important;
    border: 1.5px solid var(--accent-color) !important;
    border-radius: 10px !important;
    overflow: visible !important;
}}
[data-testid="stCode"]::before {{
    content: "📋  点击复制全文";
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--accent-color);
    font-size: 14px;
    font-weight: 600;
    pointer-events: none;
}}
[data-testid="stCode"] button {{
    opacity: 1 !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
}}

/* ========== 文件上传：只显示一个按钮 ========== */
[data-testid="stFileUploaderDropzoneInstructions"] {{
    display: none !important;
}}
[data-testid="stFileUploaderDropzone"] {{
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
}}
[data-testid="stFileUploaderDropzone"] button {{
    width: 100% !important;
    min-height: 46px !important;
    background: linear-gradient(135deg, var(--accent-color) 0%, var(--accent-hover) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 16px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}}
[data-testid="stFileUploaderDropzone"] button span {{
    font-size: 0 !important;
}}
[data-testid="stFileUploaderDropzone"] button span::after {{
    content: "📁 上传录音";
    font-size: 15px !important;
}}
</style>
""", unsafe_allow_html=True)

# ========== 初始化 session state ==========
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# ========== 页头 + 三步流程 ==========
st.markdown("""
<div class="header-area">
    <p class="big-title">🎙️ AI语音简报助手</p>
    <p class="subtitle">语音直接转文字，自动生成中英双语简报</p>
</div>
""", unsafe_allow_html=True)

with st.expander("💡 使用说明", expanded=False):
    st.markdown(
        "**三步完成简报：**\n"
        "- 🎙️ **第一步**：实时录音 或 上传录音文件（自动转写）\n"
        "- ✏️ **第二步**：确认/编辑转写内容，简报类型自动识别\n"
        "- ✨ **第三步**：点击「生成简报」，获得中英双语版本"
    )

# ========== API 密钥管理 ==========
def check_api_key():
    """检查是否有可用的 API Key"""
    if st.session_state.get('api_key'):
        return st.session_state.api_key
    
    secret_key = st.secrets.get("SILICONFLOW_API_KEY", "")
    if secret_key:
        st.session_state.api_key = secret_key
        st.session_state.authenticated = True
        return secret_key
    
    return ""

api_key = check_api_key()

if st.session_state.authenticated and api_key:
    pass
elif not api_key:
    st.warning("⚠️ 未检测到 API 密钥，请手动输入")
    
    with st.expander("🔑 点击此处输入 API 密钥", expanded=True):
        st.markdown("""
        **获取步骤：**
        1. 访问 [硅基流动](https://cloud.siliconflow.cn/i/nZqCjymq)
        2. 注册完成实名认证
        3. 创建您的API密钥
        4. 复制到下方输入框
        """)
        
        api_input = st.text_input(
            "API 密钥",
            value="",
            type="password",
            placeholder="sk-xxxxxxxxxxxxxxxx",
            key="api_key_input",
            help="密钥以 sk- 开头"
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("✅ 确认并进入", type="primary", key="save_api_key"):
                if api_input and api_input.startswith("sk-"):
                    st.session_state.api_key = api_input
                    st.session_state.authenticated = True
                    st.success("✅ 登录成功！正在进入主页面...")
                    st.rerun()
                else:
                    st.error("❌ 请输入正确的 API 密钥（以 sk- 开头）")
    
    st.stop()

# ========== v2.3.1 升级：OpenAI 客户端初始化函数（无缓存） ==========
def get_openai_client(api_key: str) -> OpenAI:
    """获取 OpenAI 客户端（保守方案：每次创建新实例）"""
    return OpenAI(
        api_key=api_key,
        base_url=CONFIG['api']['base_url'],
        timeout=CONFIG['api']['timeout']
    )

# ========== v2.3.1 升级：错误分类处理 ==========
def classify_error(error: Exception) -> dict:
    """分类错误类型"""
    error_str = str(error).lower()
    
    if any(kw in error_str for kw in ['401', 'unauthorized', 'invalid api key', 'authentication']):
        return {
            "type": "auth",
            "title": "🔐 认证失败",
            "message": "API 密钥无效或已过期，请检查密钥是否正确",
            "action": "更换密钥"
        }
    elif any(kw in error_str for kw in ['connection', 'timeout', 'network', 'dns', '503']):
        return {
            "type": "network",
            "title": "📡 网络错误",
            "message": "无法连接到服务器，请检查网络连接或稍后重试",
            "action": "重试"
        }
    elif any(kw in error_str for kw in ['400', 'bad request', 'invalid', 'format']):
        return {
            "type": "format",
            "title": "⚠️ 请求格式错误",
            "message": "音频格式不支持或文件损坏，请尝试其他文件",
            "action": "更换文件"
        }
    elif any(kw in error_str for kw in ['429', 'quota', 'rate limit', 'insufficient']):
        return {
            "type": "quota",
            "title": "💰 额度不足",
            "message": "API 调用额度已用完或请求过于频繁",
            "action": "检查额度"
        }
    else:
        return {
            "type": "unknown",
            "title": "❌ 未知错误",
            "message": f"发生未知错误：{str(error)}",
            "action": "重试"
        }

# ========== 语音转文字函数（v2.3.1 升级：使用统一客户端 + 错误分类） ==========
def transcribe_audio(audio_bytes: bytes, api_key: str) -> dict:
    tmp_path = None
    try:
        client = get_openai_client(api_key)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        with open(tmp_path, "rb") as audio:
            transcription = client.audio.transcriptions.create(
                model=CONFIG['models']['transcribe'],
                file=audio,
                language="zh"
            )
            
            result_text = ""
            
            if hasattr(transcription, 'text'):
                result_text = transcription.text
            elif isinstance(transcription, str):
                result_text = transcription.strip()
                if result_text.startswith('{') and result_text.endswith('}'):
                    try:
                        json_data = json.loads(result_text)
                        if 'text' in json_data:
                            result_text = json_data['text']
                    except json.JSONDecodeError:
                        pass
                elif result_text.lower().startswith('text='):
                    result_text = result_text[5:]
            else:
                result_text = str(transcription)
            
            result_text = result_text.strip().strip("'\"").strip()
            if result_text.lower() == 'text':
                result_text = ""
        
        return {"success": True, "text": result_text}
        
    except Exception as e:
        error_info = classify_error(e)
        return {
            "success": False, 
            "error_type": error_info["type"],
            "error_title": error_info["title"],
            "error_message": error_info["message"],
            "error_action": error_info["action"],
            "error_raw": str(e)
        }
    
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

# ========== v3.1.0：共用提示词 & 流式辅助函数 ==========

PROMPTS_ZH = {
    "会议纪要": (
        "你是一名专业的会议记录员。请将以下录音文字整理为结构化会议纪要，使用 Markdown 格式，"
        "包含以下部分：\n## 会议主题\n## 主要讨论要点\n## 达成的决议\n## 待办事项与跟进（如有）\n"
        "要求：语言简洁精准，保留所有关键数据、人名和具体细节，不做无关补充。"
    ),
    "客户拜访": (
        "你是一名专业的销售助理。请将以下客户拜访记录整理为结构化拜访报告，使用 Markdown 格式，"
        "包含以下部分：\n## 客户信息与拜访背景\n## 客户需求与痛点\n## 讨论要点与沟通结果\n## 后续行动计划\n"
        "要求：准确记录客户需求、承诺事项和跟进责任人，保留所有具体信息，不遗漏任何行动项。"
    ),
    "工作日报": (
        "你是一名专业的项目助理。请将以下工作汇报整理为结构化工作日报，使用 Markdown 格式，"
        "包含以下部分：\n## 今日完成事项\n## 遇到的问题与解决方案\n## 明日工作计划\n"
        "要求：条目清晰，每项注明完成情况或具体内容，保留所有关键细节。"
    ),
    "其它摘要": (
        "你是一名专业的文档整理员。请将以下内容整理为结构化摘要，使用 Markdown 格式，"
        "根据内容性质合理划分章节，涵盖主要观点、关键细节和行动项（如有）。\n"
        "要求：逻辑清晰，保留所有关键数据和专有名词，语言简洁专业。"
    ),
}

EN_TYPE_MAP = {
    "会议纪要": "meeting minutes",
    "客户拜访": "client visit report",
    "工作日报": "daily work report",
    "其它摘要": "summary",
}

BRIEFING_TYPES = ["会议纪要", "客户拜访", "工作日报", "其它摘要"]

def detect_briefing_type(text: str) -> str:
    """根据转写文本关键词自动识别最可能的简报类型（AI 分类的兜底）。"""
    keywords = {
        "会议纪要": ["会议", "议题", "参会", "决议", "纪要", "与会", "议程", "开会"],
        "客户拜访": ["客户", "拜访", "合同", "洽谈", "报价", "跟进", "签约"],
        "工作日报": ["今天", "今日", "明天", "明日", "完成事项", "工作内容", "工作日报"],
    }
    scores = {t: sum(1 for kw in kws if kw in text) for t, kws in keywords.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "其它摘要"

def classify_briefing_type(text: str, api_key: str) -> str:
    """用 AI 快速分类简报类型（取前 300 字，temperature=0，max_tokens=15）。出错时降级为关键词检测。"""
    sample = text[:300].strip()
    types_str = "、".join(BRIEFING_TYPES)
    try:
        client = OpenAI(api_key=api_key, base_url=CONFIG["api"]["base_url"])
        resp = client.chat.completions.create(
            model=CONFIG["models"]["generate"],
            messages=[
                {"role": "system", "content": (
                    f"你是文档分类器。根据文本内容，从以下类型中选出最合适的一种，"
                    f"只回复类型名称，不要其他内容：\n{types_str}"
                )},
                {"role": "user", "content": sample},
            ],
            temperature=0,
            max_tokens=15,
        )
        result = resp.choices[0].message.content.strip()
        for t in BRIEFING_TYPES:
            if t in result:
                return t
        return detect_briefing_type(text)
    except Exception:
        return detect_briefing_type(text)

def get_translate_prompt(briefing_type: str) -> str:
    en_type = EN_TYPE_MAP.get(briefing_type, "briefing")
    return (
        f"You are an expert professional translator specializing in business documents. "
        f"Translate the following Chinese {en_type} into natural, idiomatic English.\n"
        f"Rules:\n"
        f"- Preserve the exact Markdown structure (all headers, bullet points, numbering)\n"
        f"- Keep all proper nouns, numbers, and specific details intact\n"
        f"- Use professional language appropriate for {en_type}\n"
        f"- Do NOT add commentary, explanations, or extra content\n"
        f"- Translate only; do not summarize or interpret"
    )

def stream_completion(client, messages: list, temperature: float, max_tokens: int):
    """OpenAI 流式响应生成器，供 st.write_stream() 消费。"""
    resp = client.chat.completions.create(
        model=CONFIG['models']['generate'],
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )
    for chunk in resp:
        delta = chunk.choices[0].delta
        if delta.content is not None:
            yield delta.content


# ========== v3.0.0：导出区块（st.code 原生复制 + st.download_button）==========
def show_export_section(content: str, filename: str, label_copy: str, label_dl: str, key: str):
    """
    iOS PWA 安全导出区块：
    - st.code() 右上角原生复制按钮（无 JS，iOS PWA / 桌面均可用）
    - st.download_button 供桌面下载文件
    """
    st.code(content, language=None)
    mime = "text/markdown" if filename.endswith(".md") else "text/plain"
    st.download_button(
        label=f"💾 {label_dl}",
        data=content.encode("utf-8"),
        file_name=filename,
        mime=mime,
        use_container_width=True,
        key=f"dl_{key}"
    )


# ========== 主界面 ==========
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🎤 语音输入")

    st.markdown("**方式一：实时录音**")
    
    try:
        from streamlit_mic_recorder import mic_recorder
        
        audio = mic_recorder(
            start_prompt="🎙️ 开始录音",
            stop_prompt="⏹️ 停止录音",
            just_once=True,
            use_container_width=True,
            key="mic_recorder_ios_v2"
        )
        
        if audio and audio.get("bytes"):
            audio_kb = len(audio["bytes"]) / 1024
            with st.status("🎙️ 转写中…", expanded=True) as ts:
                result = transcribe_audio(audio["bytes"], api_key)
                if result["success"]:
                    clean_text = result["text"]
                    if not clean_text or clean_text.strip() == "":
                        ts.update(label="⚠️ 转写结果为空", state="error", expanded=True)
                        st.warning("录音内容可能过短或不清晰，请重新录制")
                    else:
                        st.write("🤖 正在识别简报类型…")
                        detected = classify_briefing_type(clean_text, api_key)
                        ts.update(label=f"✅ 转写完成，识别为【{detected}】", state="complete", expanded=False)
                        st.session_state.transcribed_text = clean_text
                        st.session_state.briefing_type = detected
                        st.session_state._type_auto_detected = True
                        st.rerun()
                else:
                    error_type = result.get("error_type", "unknown")
                    error_title = result.get("error_title", "错误")
                    error_message = result.get("error_message", result["error_raw"])
                    ts.update(label=f"❌ {error_title}", state="error", expanded=True)
                    st.write(error_message)
                    if error_type == "auth":
                        if st.button("🔄 重新输入密钥", key="reauth_mic"):
                            st.session_state.authenticated = False
                            st.session_state.api_key = ""
                            st.rerun()
                    
    except ImportError:
        st.error("⚠️ 录音组件加载失败，请使用方式二上传文件")
    except Exception as e:
        st.error(f"⚠️ 录音功能异常：{str(e)}")
        st.info("请尝试使用方式二上传录音文件")
    
    st.divider()

    audio_file = st.file_uploader(
        "方式二：上传录音",
        type=['mp3', 'wav', 'm4a', 'webm', 'ogg'],
        help="支持 MP3、WAV、M4A、WEBM、OGG，最大 200MB。\n\n📱 iPhone：「语音备忘录」录音 → 分享 → 存储到「文件」→ 在此上传"
    )

    if audio_file:
        file_id = f"{audio_file.name}_{audio_file.size}"
        if st.session_state.get("_last_upload_id") != file_id:
            st.session_state._last_upload_id = file_id
            file_bytes = audio_file.getvalue()
            file_mb = len(file_bytes) / (1024 * 1024)
            with st.status(f"🎙️ 转写中（{file_mb:.1f} MB）…", expanded=True) as ts:
                result = transcribe_audio(file_bytes, api_key)
                if result["success"]:
                    clean_text = result["text"]
                    if not clean_text or clean_text.strip() == "":
                        ts.update(label="⚠️ 转写结果为空", state="error", expanded=True)
                        st.warning("音频内容可能过短或格式不支持，请换个文件试试")
                    else:
                        st.write("🤖 正在识别简报类型…")
                        detected = classify_briefing_type(clean_text, api_key)
                        ts.update(label=f"✅ 转写完成，识别为【{detected}】", state="complete", expanded=False)
                        st.session_state.transcribed_text = clean_text
                        st.session_state.briefing_type = detected
                        st.session_state._type_auto_detected = True
                        st.rerun()
                else:
                    error_type = result.get("error_type", "unknown")
                    error_title = result.get("error_title", "错误")
                    error_message = result.get("error_message", result["error_raw"])
                    ts.update(label=f"❌ {error_title}", state="error", expanded=True)
                    st.write(error_message)
                    if error_type == "auth":
                        if st.button("🔄 重新输入密钥", key="reauth_upload"):
                            st.session_state.authenticated = False
                            st.session_state.api_key = ""
                            st.rerun()

with col2:
    st.subheader("📝 编辑与生成")

    # 1. 内容编辑区（转写结果自动填入）
    default_text = st.session_state.get("transcribed_text", "")
    content = st.text_area(
        "编辑内容",
        value=default_text,
        height=180,
        placeholder="语音转写内容会出现在这里，您也可以直接输入…",
        label_visibility="collapsed"
    )
    if content != st.session_state.get("transcribed_text", ""):
        st.session_state.transcribed_text = content
    if content:
        st.markdown(f'<p class="char-count">{len(content)} 字</p>', unsafe_allow_html=True)

    # 2. 简报类型（转写后自动预选，可手动更改）
    briefing_type = st.selectbox(
        "简报类型",
        BRIEFING_TYPES,
        key="briefing_type"
    )
    if st.session_state.get("_type_auto_detected"):
        st.caption("🤖 已根据内容自动识别，可手动更改")

    # 3. 特殊要求（折叠，默认隐藏）
    with st.expander("⚙️ 特殊要求（选填）", expanded=False):
        custom_req = st.text_input(
            "特殊要求",
            placeholder="例如：重点突出数据、使用 bullet points",
            label_visibility="collapsed"
        )
    
    col_gen, col_clear = st.columns([3, 1])
    with col_gen:
        if st.button("✨ 生成简报", type="primary", use_container_width=True):
            if not content.strip():
                st.error("❌ 内容不能为空")
            else:
                try:
                    client = get_openai_client(api_key)
                    prompt_zh = PROMPTS_ZH[briefing_type]
                    if custom_req:
                        prompt_zh += f"\n\n额外要求：{custom_req}"
                    with st.status("🤖 生成中文简报…", expanded=True) as s1:
                        zh_result = st.write_stream(stream_completion(
                            client,
                            [{"role": "system", "content": prompt_zh},
                             {"role": "user", "content": content}],
                            temperature=0.7,
                            max_tokens=2000,
                        ))
                        s1.update(
                            label=f"✅ 完成（{len(zh_result)} 字）",
                            state="complete", expanded=False
                        )
                    st.session_state.generated_result_zh = zh_result
                    st.session_state.zh_edit_content = zh_result
                    if "generated_result_en" in st.session_state:
                        del st.session_state["generated_result_en"]
                    st.rerun()
                except Exception as e:
                    error_info = classify_error(e)
                    st.error(f"{error_info['title']}：{error_info['message']}")
                    if error_info['type'] == 'auth':
                        if st.button("🔄 重新输入密钥", key="reauth_gen"):
                            st.session_state.authenticated = False
                            st.session_state.api_key = ""
                            st.rerun()

    with col_clear:
        if st.button("🗑️ 清空", use_container_width=True):
            st.session_state.transcribed_text = ""
            for _k in ["generated_result_zh", "generated_result_en", "generated_result",
                       "_type_auto_detected", "_last_upload_id", "zh_edit_content"]:
                if _k in st.session_state:
                    del st.session_state[_k]
            st.rerun()

    # ========== 结果展示：双 Tab ==========
    if "generated_result_zh" in st.session_state:
        st.divider()
        tab_zh, tab_en = st.tabs(["🇨🇳 中文版", "🇬🇧 English"])

        with tab_zh:
            if "zh_edit_content" not in st.session_state:
                st.session_state.zh_edit_content = st.session_state.get("generated_result_zh", "")
            current_zh = st.session_state.get("zh_edit_content", "")
            if current_zh:
                st.markdown(f'<span class="stat-badge">📝 {len(current_zh)} 字</span>', unsafe_allow_html=True)
            st.text_area("编辑中文简报", key="zh_edit_content", height=260, label_visibility="collapsed")
            show_export_section(
                content=st.session_state.get("zh_edit_content", ""),
                filename=f"简报_{briefing_type}.md",
                label_copy="复制全文",
                label_dl="下载中文版 .md",
                key="zh"
            )

        with tab_en:
            if "generated_result_en" in st.session_state:
                result_en = st.session_state["generated_result_en"]
                st.markdown(
                    f'<span class="stat-badge">📝 ~{len(result_en.split())} words</span>',
                    unsafe_allow_html=True
                )
                st.markdown(result_en)
                show_export_section(
                    content=result_en,
                    filename=f"Briefing_{briefing_type}.md",
                    label_copy="Copy all text",
                    label_dl="Download English .md",
                    key="en"
                )
            else:
                st.caption("中文简报生成后，点击下方按钮获取英文版")
            en_btn_label = "🌐 重新生成英文版" if "generated_result_en" in st.session_state else "🌐 生成英文版"
            if st.button(en_btn_label, use_container_width=True, key="translate_btn"):
                edited_zh = st.session_state.get("zh_edit_content", "")
                if not edited_zh.strip():
                    st.error("中文内容为空")
                else:
                    try:
                        client = get_openai_client(api_key)
                        with st.status("🌐 翻译为英文…", expanded=True) as sr:
                            en_result = st.write_stream(stream_completion(
                                client,
                                [{"role": "system", "content": get_translate_prompt(briefing_type)},
                                 {"role": "user", "content": edited_zh}],
                                temperature=0.3,
                                max_tokens=3000,
                            ))
                            sr.update(
                                label=f"✅ 翻译完成（~{len(en_result.split())} words）",
                                state="complete", expanded=False
                            )
                        st.session_state.generated_result_en = en_result
                        st.rerun()
                    except Exception as e:
                        error_info = classify_error(e)
                        st.error(f"{error_info['title']}：{error_info['message']}")

# ========== 版本号 ==========
st.divider()
st.caption(f"Made with ❤️ | PWA v{CONFIG['version']} · AI语音简报助手")
