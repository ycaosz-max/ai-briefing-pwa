# AI简报小助手 - PWA版 v1.0.0
# 基于语音版v2.1.1 iOS优化版，添加PWA支持

import streamlit as st
from openai import OpenAI
import os
import tempfile

# ========== PWA配置（必须在最前面）==========
st.markdown("""
<!-- PWA Manifest -->
<link rel="manifest" href="manifest.json">

<!-- iOS PWA配置 -->
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="AI简报">
<meta name="theme-color" content="#FF6B6B">

<!-- Emoji图标 -->
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎙️</text></svg>">
<link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎙️</text></svg>">

<!-- Service Worker注册 -->
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('sw.js')
      .then(function(reg) { console.log('SW注册成功:', reg.scope); })
      .catch(function(err) { console.log('SW注册失败:', err); });
  });
}
</script>
""", unsafe_allow_html=True)

# ========== 页面设置 ==========
st.set_page_config(
    page_title="AI语音简报助手", 
    page_icon="🎙️",
    initial_sidebar_state="expanded"
)

# ========== 样式（iOS优化+PWA优化）==========
st.markdown("""
<style>
* {
    -webkit-tap-highlight-color: transparent;
    -webkit-touch-callout: none;
}
.stTextInput input, .stTextArea textarea {
    -webkit-appearance: none !important;
    -webkit-user-select: text !important;
    user-select: text !important;
    font-size: 16px !important;
    touch-action: manipulation;
}
.stButton button {
    -webkit-appearance: none;
    touch-action: manipulation;
}
@media (max-width: 768px) {
    .big-title { font-size: 24px !important; }
    .subtitle { font-size: 14px !important; }
    .main .block-container { padding: 1rem; }
}
/* PWA全屏模式优化 */
@media (display-mode: standalone) {
    .main .block-container { padding-top: 2rem; }
}
.big-title { font-size: 42px; font-weight: bold; color: #FF6B6B; text-align: center; }
.subtitle { font-size: 18px; color: #666; text-align: center; margin-bottom: 30px; }
.voice-box { background-color: #f0f2f6; padding: 20px; border-radius: 15px; border-left: 5px solid #FF6B6B; margin: 10px 0; }
.stButton>button { border-radius: 20px; height: 3em; font-weight: bold; width: 100%; }
</style>
""", unsafe_allow_html=True)

# ========== 标题 ==========
st.markdown('<p class="big-title">🎙️ AI语音简报助手</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">语音直接转文字，自动生成简报</p>', unsafe_allow_html=True)

# ========== API密钥输入（主界面，iOS优化）==========
api_key = st.secrets.get("SILICONFLOW_API_KEY", "")

if not api_key:
    st.warning("⚠️ 首次使用需要输入 API 密钥")
    
    with st.expander("🔑 点击此处输入 API 密钥", expanded=True):
        st.markdown("""
        **获取步骤：**
        1. 访问 [siliconflow.cn](https://siliconflow.cn)
        2. 手机号注册（送14元额度）
        3. 创建 API 密钥
        4. 复制到下方输入框
        """)
        
        api_input = st.text_input(
            "API 密钥",
            value="",
            type="password",
            placeholder="sk-xxxxxxxxxxxxxxxx",
            key="api_key_input"
        )
        
        if st.button("✅ 确认并保存", type="primary", key="save_api_key"):
            if api_input and api_input.startswith("sk-"):
                st.session_state.api_key = api_input
                st.success("✅ API 密钥已保存！")
                st.rerun()
            else:
                st.error("❌ 请输入正确的 API 密钥（以 sk- 开头）")
    
    st.stop()

# ========== 侧边栏 ==========
with st.sidebar:
    st.header("⚙️ 设置")
    st.success("✅ API 已配置")
    
    if st.button("🔄 更换 API 密钥"):
        del st.session_state.api_key
        st.rerun()
    
    st.divider()
    st.caption("💡 语音转文字使用Whisper模型")

# ========== 语音转文字函数 ==========
def transcribe_audio(audio_bytes, api_key):
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.siliconflow.cn/v1")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        with open(tmp_path, "rb") as audio:
            transcription = client.audio.transcriptions.create(
                model="FunAudioLLM/SenseVoiceSmall",
                file=audio,
                response_format="text"
            )
        
        os.unlink(tmp_path)
        return {"success": True, "text": transcription}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ========== 主界面 ==========
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🎤 语音输入")
    
    # 方式一：实时录音
    st.markdown("""
    <div class="voice-box">
        <h4>方式一：实时录音转文字</h4>
        <p style="color: #666; font-size: 14px; margin: 0;">
            📱 iPhone 提示：请使用 Safari 浏览器<br>
            点击录音 → 说话 → 自动转写填入右侧
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        from streamlit_mic_recorder import mic_recorder
        
        audio = mic_recorder(
            start_prompt="🎙️ 点击开始录音",
            stop_prompt="⏹️ 点击停止",
            just_once=True,
            key="mic_recorder_ios"
        )
        
        if audio and audio.get("bytes"):
            with st.spinner("🤖 AI正在转写..."):
                result = transcribe_audio(audio["bytes"], api_key)
                
                if result["success"]:
                    st.session_state.transcribed_text = result["text"]
                    st.success(f"✅ 转写完成！共 {len(result['text'])} 字")
                    st.rerun()
                else:
                    st.error(f"❌ 转写失败：{result['error']}")
                    
    except ImportError:
        st.error("⚠️ 录音组件加载失败")
        st.info("请刷新页面重试")
    
    st.divider()
    
    # 方式二：上传录音
    st.subheader("📁 方式二：上传录音")
    
    st.info("""
    💡 **iPhone 用户推荐此方式**：
    1. 用"语音备忘录"录好音
    2. 点击分享 → 存储到"文件"
    3. 在这里选择文件上传
    """)
    
    audio_file = st.file_uploader(
        "选择录音文件", 
        type=['mp3', 'wav', 'm4a', 'webm'],
        help="支持 mp3, wav, m4a 格式"
    )
    
    if audio_file:
        st.audio(audio_file, format=f'audio/{audio_file.type.split("/")[1]}')
        
        if st.button("🎯 开始转写", key="transcribe_mic"):
            with st.spinner("🤖 AI正在转写..."):
                result = transcribe_audio(audio_file.getvalue(), api_key)
                
                if result["success"]:
                    st.session_state.transcribed_text = result["text"]
                    st.success(f"✅ 转写完成！共 {len(result['text'])} 字")
                    st.rerun()
                else:
                    st.error(f"❌ 转写失败：{result['error']}")

with col2:
    st.subheader("📝 编辑与生成")
    
briefing_type = st.selectbox(
    "简报类型",
    ["工作日报", "会议纪要", "学习笔记", "新闻摘要"],
    index=1,  # 默认选中“会议纪要”
    key="briefing_type"
)
    
    default_text = st.session_state.get("transcribed_text", "")
    
    content = st.text_area(
        "编辑内容",
        value=default_text,
        height=300,
        placeholder="语音转写内容会出现在这里..."
    )
    
    if content != st.session_state.get("transcribed_text", ""):
        st.session_state.transcribed_text = content
    
    custom_req = st.text_input("特殊要求", placeholder="例如：重点突出数据")
    
    col_gen, col_clear = st.columns([3, 1])
    with col_gen:
        if st.button("✨ 生成简报", type="primary", use_container_width=True):
            if not content.strip():
                st.error("❌ 内容不能为空")
            else:
                with st.spinner("🤖 生成中..."):
                    try:
                        client = OpenAI(api_key=api_key, base_url="https://api.siliconflow.cn/v1")
                        
                        prompts = {
                            "工作日报": "整理成工作日报：1完成 2问题 3计划",
                            "会议纪要": "整理成会议纪要：1主题 2讨论 3决议 4待办",
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
            file_name=f"简报_{briefing_type}.txt"
        )

st.divider()

st.caption("Made with ❤️ | PWA版 v1.0.0 - 像App一样使用")

