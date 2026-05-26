import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

# 페이지 기본 설정
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
    st.latex(f"\\text{{격자 상수 }} (a) = {props[structure]['a']} \\quad | \\quad \\text{{APF}} = {props[structure]['apf'] * 100}\\%")
    st.markdown("---")
    
    R = 1.0 # 기준 원자 반지름
    a = props[structure]['a_val'] * R
    formula = ""
    
    # 화면 2분할 (2D 뷰, 3D 뷰)
    col_2d, col_3d = st.columns(2)
    
    # ----------------------------------------------------
    # [왼쪽] 2D 단면 / 선 배열 시각화 설정 (Matplotlib)
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
    # [오른쪽] 3D 인터랙티브 시각화 설정 (Plotly)
    # ----------------------------------------------------
    fig3d = go.Figure()

    # 1. 큐브 모서리 그리기 (Wireframe)
    edges = [
        ([0, a], [0, 0], [0, 0]), ([0, a], [a, a], [0, 0]), ([0, a], [0, 0], [a, a]), ([0, a], [a, a], [a, a]),
        ([0, 0], [0, a], [0, 0]), ([a, a], [0, a], [0, 0]), ([0, 0], [0, a], [a, a]), ([a, a], [0, a], [a, a]),
        ([0, 0], [0, 0], [0, a]), ([a, a], [0, 0], [0, a]), ([0, 0], [a, a], [0, a]), ([a, a], [a, a], [0, a])
    ]
    for ex, ey, ez in edges:
        fig3d.add_trace(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines', line=dict(color='gray', width=2), hoverinfo='skip'))

    # 2. 3D 원자 배치
    # 꼭짓점 (Corners)
    cx, cy, cz = zip(*[(0,0,0), (a,0,0), (0,a,0), (a,a,0), (0,0,a), (a,0,a), (0,a,a), (a,a,a)])
    fig3d.add_trace(go.Scatter3d(x=cx, y=cy, z=cz, mode='markers', marker=dict(size=12, color='lightgray', line=dict(color='black', width=1)), name='Corner Atoms'))
    
    # 체심/면심 (Body / Face centered)
    if "BCC" in structure:
        fig3d.add_trace(go.Scatter3d(x=[a/2], y=[a/2], z=[a/2], mode='markers', marker=dict(size=15, color='orange', line=dict(color='black', width=1)), name='Body-Centered Atom'))
    elif "FCC" in structure:
        fx, fy, fz = zip(*[(a/2, a/2, 0), (a/2, a/2, a), (a/2, 0, a/2), (a/2, a, a/2), (0, a/2, a/2), (a, a/2, a/2)])
        fig3d.add_trace(go.Scatter3d(x=fx, y=fy, z=fz, mode='markers', marker=dict(size=13, color='gold', line=dict(color='black', width=1)), name='Face-Centered Atoms'))

    # 3. 타겟 평면 또는 선 그리기
    if calc_type == "면밀도 (Planar Density)":
        if target == "(100) 평면":
            px, py, pz = [a, a, a, a], [0, a, a, 0], [0, 0, a, a]
        elif target == "(110) 평면":
            px, py, pz = [a, 0, 0, a], [0, a, a, 0], [0, 0, a, a]
        elif target == "(111) 평면":
            px, py, pz = [a, 0, 0], [0, a, 0], [0, 0, a]
            
        fig3d.add_trace(go.Mesh3d(x=px, y=py, z=pz, color='dodgerblue', opacity=0.4, name=f'{target}', hoverinfo='name'))
    else:
        if target == "[100] 방향":
            lx, ly, lz = [0, a], [0, 0], [0, 0]
        elif target == "[110] 방향":
            lx, ly, lz = [0, a], [0, a], [0, 0]
        elif target == "[111] 방향":
            lx, ly, lz = [0, a], [0, a], [0, a]
            
        fig3d.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='red', width=8), name=f'{target}'))

    # 레이아웃 설정 (축 숨기기 및 여백 최소화)
    fig3d.update_layout(
        title="3D 단위정 (드래그하여 360도 회전)",
        scene=dict(
            xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
            aspectmode='cube'
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        showlegend=True,
        legend=dict(yanchor="top", y=0.9, xanchor="left", x=0.1)
    )

    with col_3d:
        st.plotly_chart(fig3d, use_container_width=True)

    # ----------------------------------------------------
    # 정보 및 계산식 출력
    # ----------------------------------------------------
    st.info("💡 **도출된 밀도 계산 식 (원자 반경 R 기준)**")
    st.latex(formula)
    
    if target == "(111) 평면":
        st.warning("**[주의]** BCC 구조의 (111) 평면은 체심(중심) 원자를 관통하지 않고 비껴갑니다! (3D 투시도를 회전하며 확인해보세요)")
        if "FCC" in structure:
            st.success("**[참고]** FCC의 (111) 평면은 원자가 가장 빈틈없이 배열된 최조밀 충진면(Close-Packed Plane)입니다.")

    st.write("")
    
    # + 알잘딱깔센 추가 기능: 재료공학적 의미 아코디언 탭
    with st.expander("📚 [결과 해석] 이 밀도 값이 의미하는 바는 무엇일까요?"):
        st.markdown(f"""
        **{target}의 밀도 분석이 중요한 이유**
        - **슬립계 (Slip System):** 금속이 외부의 힘을 받아 영구적으로 형태가 변할 때(소성 변형), 원자들은 밀도가 가장 높은 평면(조밀면)을 따라, 밀도가 가장 높은 방향(조밀방향)으로 미끄러집니다(Slip).
        - **{structure}의 특성:**
            - **FCC**는 (111) 평면처럼 매우 빽빽한 조밀면을 가지고 있어 슬립이 쉽게 일어나며, 이는 연성(잘 늘어나는 성질)이 매우 좋음을 의미합니다. (예: 금, 은, 알루미늄)
            - **BCC**는 완벽한 최조밀면이 없어 FCC보다 단단하지만 상온에서 상대적으로 덜 유연한 특징이 있습니다. (예: 철, 텅스텐)
        """)

    st.write("")
    if st.button("🔄 처음부터 다시 계산하기"):
        reset_step()
        st.rerun()
