import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# 페이지 기본 설정 (가로로 넓게 쓰기 위해 wide 모드로 변경)
st.set_page_config(page_title="결정구조 밀도 시뮬레이터", layout="wide")

# ==========================================
# 세션 상태(Session State) 초기화
# ==========================================
if 'step' not in st.session_state:
    st.session_state.step = 1

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1
def reset_step(): st.session_state.step = 1

# ==========================================
# UI 렌더링
# ==========================================
st.title("결정구조 선밀도 및 면밀도 3D 시뮬레이터 ⚛️")
st.markdown("---")

# [1단계] 결정 구조 선택
if st.session_state.step == 1:
    st.subheader("1️⃣ 결정 구조를 선택하세요")
    st.session_state.structure = st.radio(
        "결정 구조", ("SC (단순입방)", "BCC (체심입방)", "FCC (면심입방)"), label_visibility="collapsed"
    )
    st.write("")
    if st.button("다음 단계 ➡️", type="primary"):
        next_step()
        st.rerun()

# [2단계] 밀도 종류 선택
elif st.session_state.step == 2:
    st.subheader("2️⃣ 계산할 밀도를 선택하세요")
    st.session_state.calc_type = st.radio(
        "밀도 종류", ("면밀도 (Planar Density)", "선밀도 (Linear Density)"), label_visibility="collapsed"
    )
    st.write("")
    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("⬅️ 이전"):
            prev_step()
            st.rerun()
    with col2:
        if st.button("다음 단계 ➡️", type="primary"):
            next_step()
            st.rerun()

# [3단계] 평면/방향 선택
elif st.session_state.step == 3:
    if st.session_state.calc_type == "면밀도 (Planar Density)":
        st.subheader("3️⃣ 분석할 평면(Miller Indices)을 선택하세요")
        options = ("(100) 평면", "(110) 평면", "(111) 평면")
    else:
        st.subheader("3️⃣ 분석할 방향(Direction)을 선택하세요")
        options = ("[100] 방향", "[110] 방향", "[111] 방향")
        
    st.session_state.target = st.radio("평면/방향", options, label_visibility="collapsed")
    st.write("")
    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("⬅️ 이전"):
            prev_step()
            st.rerun()
    with col2:
        if st.button("결과 계산하기 🚀", type="primary"):
            next_step()
            st.rerun()

# [4단계] 결과 출력 및 시각화
elif st.session_state.step == 4:
    structure = st.session_state.structure
    calc_type = st.session_state.calc_type
    target = st.session_state.target
    
    # 결정구조별 기본 속성
    props = {
        "SC (단순입방)": {"a": "2R", "a_val": 2, "apf": 0.52},
        "BCC (체심입방)": {"a": "\\frac{4R}{\\sqrt{3}}", "a_val": 4/np.sqrt(3), "apf": 0.68},
        "FCC (면심입방)": {"a": "2\\sqrt{2}R", "a_val": 2*np.sqrt(2), "apf": 0.74}
    }
    
    st.markdown(f"### 📌 {structure} - {target}")
    st.latex(f"격자 상수 (a) = {props[structure]['a']} \\quad | \\quad \\text{{APF}} = {props[structure]['apf'] * 100}\\%")
    st.markdown("---")
    
    R = 1.0 # 기준 원자 반지름
    a = props[structure]['a_val'] * R
    formula = ""
    
    # 화면 2분할 (2D 뷰, 3D 뷰)
    col_2d, col_3d = st.columns(2)
    
    # ----------------------------------------------------
    # [왼쪽] 2D 단면 / 선 배열 시각화 설정
    # ----------------------------------------------------
    fig2d, ax2d = plt.subplots(figsize=(5, 5))
    ax2d.set_aspect('equal')
    ax2d.set_title("2D 분석 뷰", fontsize=15, pad=15)
    
    if calc_type == "면밀도 (Planar Density)":
        if target == "(100) 평면":
            ax2d.plot([0, a, a, 0, 0], [0, 0, a, a, 0], 'k--', lw=2)
            ax2d.set_xlim(-R, a + R); ax2d.set_ylim(-R, a + R)
            atoms = [(0,0), (a,0), (0,a), (a,a)]
            if "SC" in structure: formula = "\\text{PD} = \\frac{1}{a^2} = \\frac{1}{4R^2}"
            elif "BCC" in structure: formula = "\\text{PD} = \\frac{1}{a^2} = \\frac{3}{16R^2}"
            elif "FCC" in structure: 
                atoms.append((a/2, a/2))
                formula = "\\text{PD} = \\frac{2}{a^2} = \\frac{1}{4R^2}"
            for x, y in atoms: ax2d.add_patch(plt.Circle((x, y), R, color='skyblue', ec='black', alpha=0.8))

        elif target == "(110) 평면":
            w, h = a * np.sqrt(2), a
            ax2d.plot([0, w, w, 0, 0], [0, 0, h, h, 0], 'k--', lw=2)
            ax2d.set_xlim(-R, w + R); ax2d.set_ylim(-R, h + R)
            atoms = [(0,0), (w,0), (0,h), (w,h)]
            if "SC" in structure: formula = "\\text{PD} = \\frac{1}{\\sqrt{2}a^2}"
            elif "BCC" in structure:
                atoms.append((w/2, h/2))
                formula = "\\text{PD} = \\frac{2}{\\sqrt{2}a^2} = \\frac{3\\sqrt{2}}{16R^2}"
            elif "FCC" in structure:
                atoms.extend([(w/2, 0), (w/2, h)])
                formula = "\\text{PD} = \\frac{2}{\\sqrt{2}a^2} = \\frac{\\sqrt{2}}{8R^2}"
            for x, y in atoms: ax2d.add_patch(plt.Circle((x, y), R, color='lightgreen', ec='black', alpha=0.8))

        elif target == "(111) 평면":
            L = a * np.sqrt(2)
            h_tri = L * np.sqrt(3) / 2
            ax2d.plot([0, L, L/2, 0], [0, 0, h_tri, 0], 'k--', lw=2)
            ax2d.set_xlim(-R, L + R); ax2d.set_ylim(-R, h_tri + R)
            atoms = [(0,0), (L,0), (L/2, h_tri)]
            if "SC" in structure: formula = "\\text{PD} = \\frac{0.5}{\\frac{\\sqrt{3}}{2}a^2} = \\frac{1}{\\sqrt{3}a^2}"
            elif "BCC" in structure: formula = "\\text{PD} = \\frac{0.5}{\\frac{\\sqrt{3}}{2}a^2} = \\frac{\\sqrt{3}}{16R^2}"
            elif "FCC" in structure:
                atoms.extend([(L/2, 0), (L/4, h_tri/2), (3*L/4, h_tri/2)])
                formula = "\\text{PD} = \\frac{2}{\\frac{\\sqrt{3}}{2}a^2} = \\frac{\\sqrt{3}}{6R^2}"
            for x, y in atoms: ax2d.add_patch(plt.Circle((x, y), R, color='gold', ec='black', alpha=0.8))

    else:
        length = 0
        atoms_1d = []
        if target == "[100] 방향":
            length = a; atoms_1d = [0, a]
            if "SC" in structure: formula = "\\text{LD} = \\frac{1}{a} = \\frac{1}{2R}"
            elif "BCC" in structure: formula = "\\text{LD} = \\frac{1}{a} = \\frac{\\sqrt{3}}{4R}"
            elif "FCC" in structure: formula = "\\text{LD} = \\frac{1}{a} = \\frac{1}{2\\sqrt{2}R}"
        elif target == "[110] 방향":
            length = a * np.sqrt(2); atoms_1d = [0, length]
            if "FCC" in structure:
                atoms_1d.append(length/2)
                formula = "\\text{LD} = \\frac{2}{\\sqrt{2}a} = \\frac{1}{2R}"
            else: formula = "\\text{LD} = \\frac{1}{\\sqrt{2}a}"
        elif target == "[111] 방향":
            length = a * np.sqrt(3); atoms_1d = [0, length]
            if "BCC" in structure:
                atoms_1d.append(length/2)
                formula = "\\text{LD} = \\frac{2}{\\sqrt{3}a} = \\frac{1}{2R}"
            else: formula = "\\text{LD} = \\frac{1}{\\sqrt{3}a}"

        ax2d.plot([0, length], [0, 0], 'k-', lw=3)
        ax2d.set_xlim(-R, length + R); ax2d.set_ylim(-2*R, 2*R); ax2d.axis('off')
        for x in atoms_1d: ax2d.add_patch(plt.Circle((x, 0), R, color='salmon', ec='black', alpha=0.8))

    with col_2d:
        st.pyplot(fig2d)

    # ----------------------------------------------------
    # [오른쪽] 3D 투시도 시각화 설정
    # ----------------------------------------------------
    fig3d = plt.figure(figsize=(5, 5))
    ax3d = fig3d.add_subplot(111, projection='3d')
    ax3d.set_box_aspect([1, 1, 1])
    ax3d.set_title("3D 단위정 (Unit Cell) 투시도", fontsize=15, pad=15)
    ax3d.axis('off')

    # 1. 큐브 모서리 그리기 (12개 선)
    edges = [
        [(0,0,0),(a,0,0)], [(0,a,0),(a,a,0)], [(0,0,a),(a,0,a)], [(0,a,a),(a,a,a)],
        [(0,0,0),(0,a,0)], [(a,0,0),(a,a,0)], [(0,0,a),(0,a,a)], [(a,0,a),(a,a,a)],
        [(0,0,0),(0,0,a)], [(a,0,0),(a,0,a)], [(0,a,0),(0,a,a)], [(a,a,0),(a,a,a)]
    ]
    for edge in edges:
        p1, p2 = edge
        ax3d.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color='gray', linestyle=':', alpha=0.6)

    # 2. 3D 원자 배치 (산점도)
    corners = [(0,0,0), (a,0,0), (0,a,0), (a,a,0), (0,0,a), (a,0,a), (0,a,a), (a,a,a)]
    for c in corners: ax3d.scatter(*c, s=150, c='lightgray', edgecolors='k', alpha=0.9)
    
    if "BCC" in structure:
        ax3d.scatter(a/2, a/2, a/2, s=150, c='orange', edgecolors='k', alpha=0.9)
    elif "FCC" in structure:
        faces = [(a/2, a/2, 0), (a/2, a/2, a), (a/2, 0, a/2), (a/2, a, a/2), (0, a/2, a/2), (a, a/2, a/2)]
        for f in faces: ax3d.scatter(*f, s=150, c='gold', edgecolors='k', alpha=0.9)

    # 3. 타겟 평면 또는 선 그리기
    if calc_type == "면밀도 (Planar Density)":
        if target == "(100) 평면":
            verts = [[(a, 0, 0), (a, a, 0), (a, a, a), (a, 0, a)]]
        elif target == "(110) 평면":
            verts = [[(a, 0, 0), (0, a, 0), (0, a, a), (a, 0, a)]]
        elif target == "(111) 평면":
            verts = [[(a, 0, 0), (0, a, 0), (0, 0, a)]]
        poly = Poly3DCollection(verts, alpha=0.4, facecolor='dodgerblue', edgecolor='blue', lw=2)
        ax3d.add_collection3d(poly)
    else:
        if target == "[100] 방향":
            ax3d.plot([0, a], [0, 0], [0, 0], color='red', lw=4)
        elif target == "[110] 방향":
            ax3d.plot([0, a], [0, a], [0, 0], color='red', lw=4)
        elif target == "[111] 방향":
            ax3d.plot([0, a], [0, a], [0, a], color='red', lw=4)

    with col_3d:
        st.pyplot(fig3d)

    # ----------------------------------------------------
    # 정보 및 계산식 출력
    # ----------------------------------------------------
    st.info("💡 **도출된 밀도 계산 식 (원자 반경 R 기준)**")
    st.latex(formula)
    
    if target == "(111) 평면":
        st.warning("**[주의]** BCC 구조의 (111) 평면은 체심(중심) 원자를 관통하지 않고 비껴갑니다! (3D 투시도를 확인해보세요)")
        if "FCC" in structure:
            st.success("**[참고]** FCC의 (111) 평면은 원자가 가장 빈틈없이 배열된 최조밀 충진면(Close-Packed Plane)입니다.")

    st.write("")
    if st.button("🔄 처음부터 다시 계산하기"):
        reset_step()
        st.rerun()
        