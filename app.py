import streamlit as st
from openai import OpenAI
import os
import tempfile
import json

# ========== v2.4.0 升级：新增英文输出功能 ==========
VERSION = "2.4.0"

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

# ========== v2.3.1 升级：CSS 变量引用 CONFIG ==========
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

/* ========== iOS 暗黑模式检测 ========== */
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
    
    .stApp {{
        background-color: var(--bg-primary) !important;
    }}
    
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
    
    .stMarkdown {{
        color: var(--text-primary) !important;
    }}
}}

/* ========== iOS 基础修复 ========== */
* {{
    -webkit-tap-highlight-color: transparent;
    -webkit-touch-callout: none;
}}

/* ========== 全局样式应用 ========== */
.stApp {{
    background-color: var(--bg-primary);
    color: var(--text-primary);
    transition: background-color 0.3s ease, color 0.3s ease;
}}

.big-title {{
    font-size: 32px;
    font-weight: bold;
    color: var(--accent-color);
    margin-bottom: 8px;
    transition: color 0.3s ease;
}}

.subtitle {{
    font-size: 16px;
    color: var(--text-secondary);
    margin-bottom: 24px;
    transition: color 0.3s ease;
}}

.stTextInput input, .stTextArea textarea {{
    -webkit-appearance: none !important;
    -webkit-user-select: text !important;
    user-select: text !important;
    font-size: 16px !important;
    touch-action: manipulation;
    -webkit-border-radius: 10px;
    border-radius: 10px;
    background-color: var(--input-bg);
    color: var(--input-text);
    border: 1px solid var(--border-color);
    transition: all 0.3s ease;
}}

.stTextInput input:focus, .stTextArea textarea:focus {{
    outline: none !important;
    border-color: var(--accent-color) !important;
    box-shadow: 0 0 0 3px var(--shadow) !important;
}}

.stButton button {{
    -webkit-appearance: none;
    touch-action: manipulation;
    -webkit-border-radius: 10px;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--accent-color) 0%, var(--accent-hover) 100%) !important;
    color: var(--button-text) !important;
    border: none !important;
    font-weight: 600;
    transition: all 0.2s ease;
}}

.stButton button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 4px 12px var(--shadow);
}}

.stButton button:active {{
    transform: translateY(0);
}}

.stExpander {{
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s ease;
}}

.stAlert {{
    background-color: var(--bg-card) !important;
    border-color: var(--border-color) !important;
    color: var(--text-primary) !important;
}}

.stInfo {{
    background-color: rgba(255, 107, 107, 0.1) !important;
    border-left-color: var(--accent-color) !important;
}}

.stSuccess {{
    background-color: rgba(48, 209, 88, 0.1) !important;
    border-left-color: #30d158 !important;
}}

.stWarning {{
    background-color: rgba(255, 159, 10, 0.1) !important;
    border-left-color: #ff9f0a !important;
}}

.stError {{
    background-color: rgba(255, 69, 58, 0.1) !important;
    border-left-color: #ff453a !important;
}}

.stFileUploader > div > div {{
    background-color: var(--bg-secondary) !important;
    border-color: var(--border-color) !important;
    color: var(--text-primary) !important;
}}

hr {{
    border-color: var(--border-color) !important;
}}

.stDownloadButton button {{
    background-color: var(--bg-card) !important;
    color: var(--accent-color) !important;
    border: 2px solid var(--accent-color) !important;
}}

.stDownloadButton button:hover {{
    background-color: var(--accent-color) !important;
    color: var(--button-text) !important;
}}

.stSelectbox > div > div {{
    background-color: var(--bg-card);
    border-color: var(--border-color) !important;
    color: var(--text-primary);
    border-radius: 10px;
}}

@media (display-mode: standalone) {{
    .main .block-container {{ padding-top: 2rem; }}
    .big-title {{ margin-top: 10px; }}
}}

@media (max-width: 768px) {{
    .big-title {{ font-size: 26px !important; }}
    .subtitle {{ font-size: 14px !important; }}
    .main .block-container {{ padding: 1rem; }}
    .stApp {{ padding-bottom: env(safe-area-inset-bottom); }}
}}

* {{
    transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}}
</style>
""", unsafe_allow_html=True)

# ========== 初始化 session state ==========
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# ========== 标题 ==========
st.markdown('<p class="big-title">🎙️ AI语音简报助手</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">语音直接转文字，自动生成简报</p>', unsafe_allow_html=True)

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

# ========== 主界面 ==========
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🎤 语音输入")
    
    st.markdown("""
    <div style="padding: 15px; border-radius: 12px; margin-bottom: 10px; 
                background-color: var(--bg-secondary); 
                border: 1px solid var(--border-color);">
        <h4 style="margin-top: 0; color: var(--text-primary);">方式一：实时录音</h4>
        <p style="color: var(--text-secondary); font-size: 14px; margin: 0;">
            📱 iPhone 提示：请使用 Safari 浏览器<br>
            点击录音 → 开始说话<br> 
            点击停止 → 自动转写
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        from streamlit_mic_recorder import mic_recorder
        
        audio = mic_recorder(
            start_prompt="🎙️ 点击录音",
            stop_prompt="⏹️ 点击停止",
            just_once=True,
            key="mic_recorder_ios_v2"
        )
        
        if audio and audio.get("bytes"):
            with st.spinner("🤖 AI正在转写..."):
                result = transcribe_audio(audio["bytes"], api_key)
                
                if result["success"]:
                    clean_text = result["text"]
                    if not clean_text or clean_text.strip() == "":
                        st.warning("⚠️ 转写结果为空，请检查录音是否清晰")
                    else:
                        st.session_state.transcribed_text = clean_text
                        st.success(f"✅ 转写完成！共 {len(clean_text)} 字")
                        st.rerun()
                else:
                    # v2.3.1 升级：错误分类显示
                    error_type = result.get("error_type", "unknown")
                    error_title = result.get("error_title", "错误")
                    error_message = result.get("error_message", result["error_raw"])
                    
                    if error_type == "auth":
                        st.error(f"{error_title}：{error_message}")
                        if st.button("🔄 重新输入密钥", key="reauth_mic"):
                            st.session_state.authenticated = False
                            st.session_state.api_key = ""
                            st.rerun()
                    elif error_type == "network":
                        st.warning(f"{error_title}：{error_message}")
                    elif error_type == "format":
                        st.warning(f"{error_title}：{error_message}")
                    elif error_type == "quota":
                        st.error(f"{error_title}：{error_message}")
                    else:
                        st.error(f"{error_title}：{error_message}")
                    
    except ImportError:
        st.error("⚠️ 录音组件加载失败，请使用方式二上传文件")
    except Exception as e:
        st.error(f"⚠️ 录音功能异常：{str(e)}")
        st.info("请尝试使用方式二上传录音文件")
    
    st.divider()
    
    st.subheader("📁 方式二：上传录音")
    
    st.info("""
    💡 **iPhone 用户推荐此方式**：
    1. 用"语音备忘录"录好音
    2. 点击分享 → 存储到"文件"
    3. 在这里选择文件上传
    """)
    
    audio_file = st.file_uploader(
        "选择录音文件", 
        type=['mp3', 'wav', 'm4a', 'webm', 'ogg'],
        help="支持 mp3, wav, m4a, webm, ogg 格式"
    )
    
    if audio_file:
        st.audio(audio_file, format=f'audio/{audio_file.type.split("/")[1]}')
        
        if st.button("🎯 开始转写", type="primary", key="transcribe_upload"):
            with st.spinner("🤖 正在识别..."):
                result = transcribe_audio(audio_file.getvalue(), api_key)
                
                if result["success"]:
                    clean_text = result["text"]
                    if not clean_text or clean_text.strip() == "":
                        st.warning("⚠️ 转写结果为空，请检查音频文件")
                    else:
                        st.session_state.transcribed_text = clean_text
                        st.success(f"✅ 完成！共 {len(clean_text)} 字")
                        st.rerun()
                else:
                    # v2.3.1 升级：错误分类显示
                    error_type = result.get("error_type", "unknown")
                    error_title = result.get("error_title", "错误")
                    error_message = result.get("error_message", result["error_raw"])
                    
                    if error_type == "auth":
                        st.error(f"{error_title}：{error_message}")
                        if st.button("🔄 重新输入密钥", key="reauth_upload"):
                            st.session_state.authenticated = False
                            st.session_state.api_key = ""
                            st.rerun()
                    elif error_type == "network":
                        st.warning(f"{error_title}：{error_message}")
                    elif error_type == "format":
                        st.warning(f"{error_title}：{error_message}")
                    elif error_type == "quota":
                        st.error(f"{error_title}：{error_message}")
                    else:
                        st.error(f"{error_title}：{error_message}")

with col2:
    st.subheader("📝 编辑与生成")
    
    briefing_type = st.selectbox(
        "简报类型",
        ["会议纪要", "工作日报", "学习笔记", "新闻摘要"],
        key="briefing_type"
    )

    output_lang = st.radio(
        "输出语言 / Output Language",
        ["中文", "English"],
        horizontal=True,
        key="output_lang"
    )
    
    default_text = st.session_state.get("transcribed_text", "")
    
    content = st.text_area(
        "编辑内容",
        value=default_text,
        height=300,
        placeholder="语音转写内容会出现在这里，您也可以直接输入..."
    )
    
    if content != st.session_state.get("transcribed_text", ""):
        st.session_state.transcribed_text = content
    
    custom_req = st.text_input("特殊要求", placeholder="例如：重点突出数据、使用 bullet points")
    
    col_gen, col_clear = st.columns([3, 1])
    with col_gen:
        if st.button("✨ 生成简报", type="primary", use_container_width=True):
            if not content.strip():
                st.error("❌ 内容不能为空")
            else:
                with st.spinner("🤖 生成中..."):
                    try:
                        # v2.3.1 升级：使用统一客户端
                        client = get_openai_client(api_key)
                        
                        prompts_zh = {
                            "会议纪要": "整理成会议纪要：1主题 2讨论 3决议 4待办",
                            "工作日报": "整理成工作日报：1完成 2问题 3计划",
                            "学习笔记": "整理成学习笔记：1概念 2重点 3思考",
                            "新闻摘要": "整理成新闻摘要：1事件 2数据 3影响"
                        }
                        prompts_en = {
                            "会议纪要": "Organize into meeting minutes in English: 1.Topic 2.Discussion Points 3.Decisions 4.Action Items",
                            "工作日报": "Organize into a daily work report in English: 1.Completed Tasks 2.Issues 3.Tomorrow's Plan",
                            "学习笔记": "Organize into study notes in English: 1.Core Concepts 2.Key Points 3.Reflections",
                            "新闻摘要": "Organize into a news summary in English: 1.Core Event 2.Key Data 3.Impact Analysis"
                        }
                        prompts = prompts_en if output_lang == "English" else prompts_zh
                        
                        prompt = prompts[briefing_type]
                        if custom_req:
                            prompt += f"。要求：{custom_req}"
                        
                        response = client.chat.completions.create(
                            model=CONFIG['models']['generate'],
                            messages=[
                                {"role": "system", "content": prompt},
                                {"role": "user", "content": content}
                            ],
                            temperature=0.7,
                            max_tokens=2000
                        )
                        
                        st.session_state.generated_result = response.choices[0].message.content
                        
                    except Exception as e:
                        # v2.3.1 升级：错误分类
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
            if "generated_result" in st.session_state:
                del st.session_state.generated_result
            st.rerun()
    
    if "generated_result" in st.session_state:
        st.divider()
        st.success("✅ 生成完成！")
        st.markdown(st.session_state.generated_result)
        st.download_button(
            "📋 下载 / Download",
            st.session_state.generated_result,
            file_name=f"{'Briefing' if output_lang == 'English' else '简报'}_{briefing_type}.txt",
            mime="text/plain"
        )

# ========== v2.3.1 升级：统一版本号引用 ==========
st.divider()
st.caption(f"Made with ❤️ | PWA版 v{CONFIG['version']} - 像App一样使用")
