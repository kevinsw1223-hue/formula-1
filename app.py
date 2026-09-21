import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(
    page_title="Pixel Strikers - 축구 게임",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.title("⚽ Pixel Strikers")
    st.markdown("---")
    st.subheader("🎮 조작 안내")
    st.markdown("""
    - **이동**: `W`, `A`, `S`, `D` 또는 `방향키`
    - **강력 슛**: `Space` 또는 `J`
    - **패스**: `K`
    - **대시/태클**: `Left Shift` 또는 `L`
    """)
    st.markdown("---")
    st.info("💡 **Tip**: 경기 시간은 90초입니다. AI 수비를 따돌리고 골을 성공시켜 보세요!")

st.title("⚽ Arcade Football: Pixel Strikers")

html_file_path = os.path.join(os.path.dirname(__file__), "htmls", "index.html")

if os.path.exists(html_file_path):
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # 높이(height)를 540으로 설정하여 Streamlit 레이아웃 내에 딱 맞게 표시
    components.html(html_content, height=540, scrolling=False)
else:
    st.error(f"❌ HTML 게임 파일을 찾을 수 없습니다: `{html_file_path}`")
