import streamlit as st
import streamlit.components.v1 as components
import os

# 1. Streamlit 페이지 레이아웃 기본 설정
st.set_page_config(
    page_title="Pixel Strikers - 축구 게임",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 사이드바 안내 창 생성
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

# 3. 메인 타이틀 출력
st.title("⚽ Arcade Football: Pixel Strikers")
st.caption("HTML5 Canvas 기반 2D 아케이드 축구 시뮬레이션 게임")

# 4. htmls/index.html 경로 확인 및 임베딩
html_file_path = os.path.join(os.path.dirname(__file__), "htmls", "index.html")

if os.path.exists(html_file_path):
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # HTML5 캔버스를 렌더링하기 위한 Streamlit 컴포넌트 호출
    components.html(html_content, height=620, scrolling=False)
else:
    st.error(f"❌ HTML 게임 파일을 찾을 수 없습니다: `{html_file_path}`")
    st.warning("`htmls/index.html` 위치에 파일이 올바르게 생성되었는지 확인해 주세요.")
