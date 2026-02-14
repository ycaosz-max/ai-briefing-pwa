import streamlit as st
from openai import OpenAI
import os
import tempfile
import json

# ========== PWA配置（必须在最前面）==========
st.markdown("""
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
<meta name="theme-color" content="#FF6B6B" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#1c1c1e" media="(prefers-color-scheme: dark)">

<!-- Service Worker注册 -->
<script>
const swCode = `self.addEventListener('install', e => { self.skipWaiting(); }); self.addEventListener('activate', e => { self.clients.claim(); }); self.addEventListener('fetch', e => { e.respondWith(fetch(e.request).catch(() => new Response('离线模式：请检查网络连接', {headers: {'Content-Type': 'text/html'}}))); });`;
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('data:text/javascript;base64,' + btoa(swCode))
    .then(reg => console.log('SW注册成功'))
    .catch(err => console.log('SW注册失败', err));
}
</script>
""", unsafe_allow_html=True)

# ========== 页面设置 ==========
st.set_page_config(
    page_title="AI语音简报助手", 
    page_icon="🎙️"
)

# ========== iOS 暗黑/明亮模式自动切换样式 ==========
st.markdown("""
<style>
/* ========== 基础变量定义 ========== */
:root {
    /* 明亮模式默认 */
    --bg-primary: #ffffff;
    --bg-secondary: #f0f2f6;
    --bg-card: #ffffff;
    --text-primary: #1f1f1f;
    --text-secondary: #666666;
    --border-color: #e0e0e0;
    --accent-color: #FF6B6B;
    --accent-hover: #FF5252;
    --shadow: rgba(255, 107, 107, 0.15);
    --input-bg: #ffffff;
    --input-text: #1f1f1f;
    --button-text: #ffffff;
}

/* ========== iOS 暗黑模式检测 ========== */
@media (prefers-color-scheme: dark) {
    :root {
        --bg-primary: #000000;
        --bg-secondary: #1c1c1e;
        --bg-card: #2c2c2e;
        --text-primary: #ffffff;
        --text-secondary: #8e8e93;
        --border-color: #38383a;
        --accent-color: #FF8585;
        --accent-hover: #FF6B6B;
        --shadow: rgba(255, 133, 133, 0.15);
        --input-bg: #1c1c1e;
        --input-text: #ffffff;
        --button-text: #ffffff;
    }
    
    /* Streamlit 暗黑模式覆盖 */
    .stApp {
        background-color: var(--bg-primary) !important;
    }
    
    .stTextInput input, .stTextArea textarea {
        background-color: var(--input-bg) !important;
        color: var(--input-text) !important;
        border-color: var(--border-color) !important;
    }
    
    .stSelectbox > div > div {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }
    
    .stExpander {
        background-color: var(--bg-card) !important;
        border-color: var(--border-color) !important;
    }
    
    .stMarkdown {
        color: var(--text-primary) !important;
    }
}

/* ========== iOS 基础修复 ========== */
* {
    -webkit-tap-highlight-color: transparent;
    -webkit-touch-callout: none;
}

/* ========== 全局样式应用 ========== */
.stApp {
    background-color: var(--bg-primary);
    color: var(--text-primary);
    transition: background-color 0.3s ease, color 0.3s ease;
}

/* 标题样式 */
.big-title {
    font-size: 32px;
    font-weight: bold;
    color: var(--accent-color);
    margin-bottom: 8px;
    transition: color 0.3s ease;
}

.subtitle {
    font-size: 16px;
    color: var(--text-secondary);
    margin-bottom: 24px;
    transition: color 0.3s ease;
}

/* 输入框样式 - 自动适应主题 */
.stTextInput input, .stTextArea textarea {
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
}

/* 输入框焦点样式 */
.stTextInput input:focus, .stTextArea textarea:focus {
    outline: none !important;
    border-color: var(--accent-color) !important;
    box-shadow: 0 0 0 3px var(--shadow) !important;
}

/* 按钮样式 - 高对比度 */
.stButton button {
    -webkit-appearance: none;
    touch-action: manipulation;
    -webkit-border-radius: 10px;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--accent-color) 0%, var(--accent-hover) 100%) !important;
    color: var(--button-text) !important;
    border: none !important;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px var(--shadow);
}

.stButton button:active {
    transform: translateY(0);
}

/* 卡片/容器样式 */
.stExpander {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s ease;
}

/* 信息框样式 - 暗黑模式适配 */
.stAlert {
    background-color: var(--bg-card) !important;
    border-color: var(--border-color) !important;
    color: var(--text-primary) !important;
}

.stInfo {
    background-color: rgba(255, 107, 107, 0.1) !important;
    border-left-color: var(--accent-color) !important;
}

.stSuccess {
    background-color: rgba(48, 209, 88, 0.1) !important;
    border-left-color: #30d158 !important;
}

.stWarning {
    background-color: rgba(255, 159, 10, 0.1) !important;
    border-left-color: #ff9f0a !important;
}

.stError {
    background-color: rgba(255, 69, 58, 0.1) !important;
    border-left-color: #ff453a !important;
}

/* 文件上传区域 */
.stFileUploader > div > div {
    background-color: var(--bg-secondary) !important;
    border-color: var(--border-color) !important;
    color: var(--text-primary) !important;
}

/* 分割线 */
hr {
    border-color: var(--border-color) !important;
}

/* 下载按钮 */
.stDownloadButton button {
    background-color: var(--bg-card) !important;
    color: var(--accent-color) !important;
    border: 2px solid var(--accent-color) !important;
}

.stDownloadButton button:hover {
    background-color: var(--accent-color) !important;
    color: var(--button-text) !important;
}

/* 选择框样式 */
.stSelectbox > div > div {
    background-color: var(--bg-card);
    border-color: var(--border-color) !important;
    color: var(--text-primary);
    border-radius: 10px;
}

/* PWA全屏模式优化 */
@media (display-mode: standalone) {
    .main .block-container { padding-top: 2rem; }
    .big-title { margin-top: 10px; }
}

/* 移动端适配 */
@media (max-width: 768px) {
    .big-title { 
        font-size: 26px !important; 
    }
    .subtitle { 
        font-size: 14px !important; 
    }
    .main .block-container { 
        padding: 1rem; 
    }
    
    /* iOS 安全区域适配 */
    .stApp {
        padding-bottom: env(safe-area-inset-bottom);
    }
}

/* 平滑过渡动画 */
* {
    transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}
</style>
""", unsafe_allow_html=True)

# ========== 标题 ==========
st.markdown('<p class="big-title">🎙️ AI语音简报助手</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">语音直接转文字，自动生成简报</p>', unsafe_allow_html=True)

# ========== API 密钥管理（修复版）==========
# 优先从 secrets 读取，其次从 session_state 读取
api_key = st.secrets.get("SILICONFLOW_API_KEY", "") or st.session_state.get("api_key", "")

if not api_key:
    st.warning("⚠️ 首次使用需要输入 API 密钥")
    
    with st.expander("🔑 点击此处输入 API 密钥", expanded=True):
        st.markdown("""
        **获取步骤：**
        1. 访问 [硅基流动](https://cloud.siliconflow.cn/i/nZqCjymq)
        2. 注册完成实名认证
        3. 创建您的API密钥
        4. 复制到下方输入框
        """)
        
        # 使用 key 参数确保组件状态持久化
        api_input = st.text_input(
            "API 密钥",
            value=st.session_state.get("temp_api_key", ""),
            type="password",
            placeholder="sk-xxxxxxxxxxxxxxxx",
            key="api_key_input_main",
            help="密钥以 sk- 开头"
        )
        
        # 保存临时值到 session_state，避免输入丢失
        if api_input:
            st.session_state.temp_api_key = api_input
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("✅ 确认并保存", type="primary", key="save_api_key_btn"):
                if api_input and api_input.startswith("sk-"):
                    # 保存到 session_state
                    st.session_state.api_key = api_input
                    # 清除临时值
                    if "temp_api_key" in st.session_state:
                        del st.session_state.temp_api_key
                    st.success("✅ API 密钥已保存！")
                    st.rerun()
                else:
                    st.error("❌ 请输入正确的 API 密钥（以 sk- 开头）")
    
    # 关键：使用 st.stop() 阻止继续执行
    st.stop()

# ========== 语音转文字函数 ==========
def transcribe_audio(audio_bytes, api_key):
    tmp_path = None
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.siliconflow.cn/v1"
        )
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        with open(tmp_path, "rb") as audio:
            transcription = client.audio.transcriptions.create(
                model="FunAudioLLM/SenseVoiceSmall",
                file=audio,
                language="zh"
            )
            
            # 处理返回结果
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
        return {"success": False, "error": str(e)}
    
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

# ========== 主界面 ==========
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🎤 语音输入")
    
    # 方式一：实时录音
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
                    st.error(f"❌ 转写失败：{result['error']}")
                    
    except ImportError:
        st.error("⚠️ 录音组件加载失败，请使用方式二上传文件")
    except Exception as e:
        st.error(f"⚠️ 录音功能异常：{str(e)}")
        st.info("请尝试使用方式二上传录音文件")
    
    st.divider()
    
    # 方式二：上传录音（iOS 推荐）
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
                    st.error(f"❌ 失败：{result['error']}")

with col2:
    st.subheader("📝 编辑与生成")
    
    briefing_type = st.selectbox(
        "简报类型",
        ["会议纪要", "工作日报", "学习笔记", "新闻摘要"],
        key="briefing_type"
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
                        client = OpenAI(
                            api_key=api_key, 
                            base_url="https://api.siliconflow.cn/v1"
                        )
                        
                        prompts = {
                            "会议纪要": "整理成会议纪要：1主题 2讨论 3决议 4待办",
                            "工作日报": "整理成工作日报：1完成 2问题 3计划",
                            "学习笔记": "整理成学习笔记：1概念 2重点 3思考",
                            "新闻摘要": "整理成新闻摘要：1事件 2数据 3影响"
                        }
                        
                        prompt = prompts[briefing_type]
                        if custom_req:
                            prompt += f"。要求：{custom_req}"
                        
                        response = client.chat.completions.create(
                            model="deepseek-ai/DeepSeek-V3",
                            messages=[
                                {"role": "system", "content": prompt},
                                {"role": "user", "content": content}
                            ],
                            temperature=0.7,
                            max_tokens=2000
                        )
                        
                        st.session_state.generated_result = response.choices[0].message.content
                        
                    except Exception as e:
                        st.error(f"❌ 生成失败：{str(e)}")
    
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
            "📋 下载",
            st.session_state.generated_result,
            file_name=f"简报_{briefing_type}.txt",
            mime="text/plain"
        )

# 添加退出/更换密钥按钮
st.divider()
col_footer1, col_footer2 = st.columns([6, 1])
with col_footer2:
    if st.button("🚪 退出登录", key="logout_btn"):
        if "api_key" in st.session_state:
            del st.session_state.api_key
        st.rerun()

st.caption("Made with ❤️ | PWA版 v2.3.0 - 像App一样使用")
