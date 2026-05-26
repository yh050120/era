import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from typing import Tuple

# ==========================================
# 1. Configuration & Constants
# ==========================================
st.set_page_config(page_title="결정구조 밀도 시뮬레이터", layout="wide", page_icon="⚛️")

CRYSTAL_PROPS = {
    "SC (단순입방)": {"a_expr": "2R", "a_factor": 2.0, "apf": 0.52},
    "BCC (체심입방)": {"a_expr": "\\frac{4R}{\\sqrt{3}}", "a_factor": 4 / np.sqrt(3), "apf": 0.68},
    "FCC (면심입방)": {"a_expr": "2\\sqrt{2}R", "a_factor": 2 * np.sqrt(2), "apf": 0.74}
}

# ==========================================
# 2. State Management
# ==========================================
def init_session_state() -> None:
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'structure' not in st.session_state:
        st.session_state.structure = "SC (단순입방)"
    if 'calc_type' not in st.session_state:
        st.session_state.calc_type = "면밀도 (Planar Density)"
    if 'target' not in st.session_state:
        st.session_state.target = "(100) 평면"

def navigate(step_change: int) -> None:
    st.session_state.step += step_change
    st.rerun()

def reset_app() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ==========================================
# 3. Visualization Engines
# ==========================================
def create_2d_plot(structure: str, calc_type: str, target: str, a: float, R: float) -> Tuple[plt.Figure, str]:
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_aspect('equal')
    ax.axis('off') 
    formula = ""
    
    if calc_type == "면밀도 (Planar Density)":
        if target == "(100) 평면":
            ax.plot([0, a, a, 0, 0], [0, 0, a, a, 0], 'k--', lw=2)
            ax.set_xlim(-R, a + R)
            ax.set_ylim(-R, a + R)
            atoms = [(0, 0), (a, 0), (0, a), (a, a)]
            
            if "SC" in structure: formula = "\\text{PD} = \\frac{1}{a^2} = \\frac{1}{4R^2}"
            elif "BCC" in structure: formula = "\\text{PD} = \\frac{1}{a^2} = \\frac{3}{16R^2}"
            elif "FCC" in structure: 
                atoms.append((a/2, a/2))
                formula = "\\text{PD} = \\frac{2}{a^2} = \\frac{1}{4R^2}"
                
            for x, y in atoms: 
                ax.add_patch(plt.Circle((x, y), R, color='skyblue', ec='black', alpha=0.8, zorder=3))

        elif target == "(110) 평면":
            w, h = a * np.sqrt(2), a
            ax.plot([0, w, w, 0, 0], [0, 0, h, h, 0], 'k--', lw=2)
            ax.set_xlim(-R, w + R)
            ax.set_ylim(-R, h + R)
            atoms = [(0, 0), (w, 0), (0, h), (w, h)]
            
            if "SC" in structure: formula = "\\text{PD} = \\frac{1}{\\sqrt{2}a^2}"
            elif "BCC" in structure:
                atoms.append((w/2, h/2))
                formula = "\\text{PD} = \\frac{2}{\\sqrt{2}a^2} = \\frac{3\\sqrt{2}}{16R^2}"
            elif "FCC" in structure:
                atoms.extend([(w/2, 0), (w/2, h)])
                formula = "\\text{PD} = \\frac{2}{\\sqrt{2}a^2} = \\frac{\\sqrt{2}}{8R^2}"
                
            for x, y in atoms: 
                ax.add_patch(plt.Circle((x, y), R, color='lightgreen', ec='black', alpha=0.8, zorder=3))

        elif target == "(111) 평면":
            L = a * np.sqrt(2)
            h_tri = L * np.sqrt(3) / 2
            ax.plot([0, L, L/2, 0], [0, 0, h_tri, 0], 'k--', lw=2)
            ax.set_xlim(-R, L + R)
            ax.set_ylim(-R, h_tri + R)
            atoms = [(0, 0), (L, 0), (L/2, h_tri)]
            
            if "SC" in structure: formula = "\\text{PD} = \\frac{0.5}{\\frac{\\sqrt{3}}{2}a^2} = \\frac{1}{\\sqrt{3}a^2}"
            elif "BCC" in structure: formula = "\\text{PD} = \\frac{0.5}{\\frac{\\sqrt{3}}{2}a^2} = \\frac{\\sqrt{3}}{16R^2}"
            elif "FCC" in structure:
                atoms.extend([(L/2, 0), (L/4, h_tri/2), (3*L/4, h_tri/2)])
                formula = "\\text{PD} = \\frac{2}{\\frac{\\sqrt{3}}{2}a^2} = \\frac{\\sqrt{3}}{6R^2}"
                
            for x, y in atoms: 
                ax.add_patch(plt.Circle((x, y), R, color='gold', ec='black', alpha=0.8, zorder=3))

    else:
        length = 0
        atoms_1d = []
        if target == "[100] 방향":
            length = a
            atoms_1d = [0, a]
            if "SC" in structure: formula = "\\text{LD} = \\frac{1}{a} = \\frac{1}{2R}"
            elif "BCC" in structure: formula = "\\text{LD} = \\frac{1}{a} = \\frac{\\sqrt{3}}{4R}"
            elif "FCC" in structure: formula = "\\text{LD} = \\frac{1}{a} = \\frac{1}{2\\sqrt{2}R}"
        elif target == "[110] 방향":
            length = a * np.sqrt(2)
            atoms_1d = [0, length]
            if "FCC" in structure:
                atoms_1d.append(length/2)
                formula = "\\text{LD} = \\frac{2}{\\sqrt{2}a} = \\frac{1}{2R}"
            else: formula = "\\text{LD} = \\frac{1}{\\sqrt{2}a}"
        elif target == "[111] 방향":
            length = a * np.sqrt(3)
            atoms_1d = [0, length]
            if "BCC" in structure:
                atoms_1d.append(length/2)
                formula = "\\text{LD} = \\frac{2}{\\sqrt{3}a} = \\frac{1}{2R}"
            else: formula = "\\text{LD} = \\frac{1}{\\sqrt{3}a}"

        ax.plot([0, length], [0, 0], 'k-', lw=3, zorder=1)
        ax.set_xlim(-R, length + R)
        ax.set_ylim(-2*R, 2*R)
        
        for x in atoms_1d: 
            ax.add_patch(plt.Circle((x, 0), R, color='salmon', ec='black', alpha=0.9, zorder=3))

    fig.tight_layout()
    return fig, formula

def create_3d_plot(structure: str, calc_type: str, target: str, a: float) -> go.Figure:
    fig = go.Figure()

    # 1. 큐브 모서리 와이어프레임
    edges = [
        ([0, a], [0, 0], [0, 0]), ([0, a], [a, a], [0, 0]), ([0, a], [0, 0], [a, a]), ([0, a], [a, a], [a, a]),
        ([0, 0], [0, a], [0, 0]), ([a, a], [0, a], [0, 0]), ([0, 0], [0, a], [a, a]), ([a, a], [0, a], [a, a]),
        ([0, 0], [0, 0], [0, a]), ([a, a], [0, 0], [0, a]), ([0, 0], [a, a], [0, a]), ([a, a], [a, a], [0, a])
    ]
    for ex, ey, ez in edges:
        fig.add_trace(go.Scatter3d(
            x=ex, y=ey, z=ez, mode='lines', 
            line=dict(color='rgba(128, 128, 128, 0.5)', width=3), 
            hoverinfo='skip', showlegend=False
        ))

    # 2. 3D 원자 배치
    cx, cy, cz = zip(*[(0,0,0), (a,0,0), (0,a,0), (a,a,0), (0,0,a), (a,0,a), (0,a,a), (a,a,a)])
    fig.add_trace(go.Scatter3d(
        x=cx, y=cy, z=cz, mode='markers', 
        marker=dict(size=15, color='#d3d3d3', line=dict(color='black', width=1)), 
        name='Corner Atoms (꼭짓점)'
    ))
    
    if "BCC" in structure:
        fig.add_trace(go.Scatter3d(
            x=[a/2], y=[a/2], z=[a/2], mode='markers', 
            marker=dict(size=20, color='#ffa500', line=dict(color='black', width=1)), 
            name='Body-Centered (체심)'
        ))
    elif "FCC" in structure:
        fx, fy, fz = zip(*[(a/2, a/2, 0), (a/2, a/2, a), (a/2, 0, a/2), (a/2, a, a/2), (0, a/2, a/2), (a, a/2, a/2)])
        fig.add_trace(go.Scatter3d(
            x=fx, y=fy, z=fz, mode='markers', 
            marker=dict(size=18, color='#ffd700', line=dict(color='black', width=1)), 
            name='Face-Centered (면심)'
        ))

    # 3. 타겟 평면/방향 시각화 (버그 픽스된 부분 🛠️)
    if calc_type == "면밀도 (Planar Density)":
        if target == "(100) 평면":
            px, py, pz = [a, a, a, a], [0, a, a, 0], [0, 0, a, a]
            # 4개의 꼭짓점을 2개의 삼각형으로 나누어 강제로 평면을 그림
            i, j, k = [0, 0], [1, 2], [2, 3] 
        elif target == "(110) 평면":
            px, py, pz = [a, 0, 0, a], [0, a, a, 0], [0, 0, a, a]
            i, j, k = [0, 0], [1, 2], [2, 3]
        elif target == "(111) 평면":
            px, py, pz = [a, 0, 0], [0, a, 0], [0, 0, a]
            # 3개의 꼭짓점이므로 1개의 삼각형만 생성
            i, j, k = [0], [1], [2] 
            
        fig.add_trace(go.Mesh3d(
            x=px, y=py, z=pz,
            i=i, j=j, k=k, # <--- 렌더링 강제 명령 추가
            color='dodgerblue', opacity=0.5, 
            name=f'{target}', hoverinfo='name'
        ))
    else:
        if target == "[100] 방향":
            lx, ly, lz = [0, a], [0, 0], [0, 0]
        elif target == "[110] 방향":
            lx, ly, lz = [0, a], [0, a], [0, 0]
        elif target == "[111] 방향":
            lx, ly, lz = [0, a], [0, a], [0, a]
            
        fig.add_trace(go.Scatter3d(
            x=lx, y=ly, z=lz, mode='lines', 
            line=dict(color='red', width=10), name=f'{target}'
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
            aspectmode='cube',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.05, bgcolor='rgba(255,255,255,0.7)'),
        hovermode='closest'
    )
    return fig

# ==========================================
# 4. Main Application UI
# ==========================================
def main():
    init_session_state()
    
    st.title("결정구조 선밀도 및 면밀도 3D 시뮬레이터 ⚛️")
    st.markdown("---")

    if st.session_state.step == 1:
        st.subheader("1️⃣ 결정 구조(Crystal Structure)를 선택하세요")
        st.session_state.structure = st.radio(
            "결정 구조", list(CRYSTAL_PROPS.keys()), label_visibility="collapsed"
        )
        st.write("")
        if st.button("다음 단계 ➡️", type="primary"): navigate(1)

    elif st.session_state.step == 2:
        st.subheader("2️⃣ 계산할 밀도 종류를 선택하세요")
        st.session_state.calc_type = st.radio(
            "밀도 종류", ("면밀도 (Planar Density)", "선밀도 (Linear Density)"), label_visibility="collapsed"
        )
        st.write("")
        col1, col2 = st.columns([1, 8])
        with col1:
            if st.button("⬅️ 이전"): navigate(-1)
        with col2:
            if st.button("다음 단계 ➡️", type="primary"): navigate(1)

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
            if st.button("⬅️ 이전"): navigate(-1)
        with col2:
            if st.button("결과 계산하기 🚀", type="primary"): navigate(1)

    elif st.session_state.step == 4:
        structure = st.session_state.structure
        calc_type = st.session_state.calc_type
        target = st.session_state.target
        
        props = CRYSTAL_PROPS[structure]
        R = 1.0 
        a_val = props['a_factor'] * R
        
        st.markdown(f"### 📌 {structure} - {target}")
        st.latex(f"\\text{{격자 상수 (Lattice Parameter), }} a = {props['a_expr']} \\quad | \\quad \\text{{원자충진율(APF)}} = {props['apf'] * 100}\\%")
        st.markdown("---")
        
        col_2d, col_3d = st.columns(2, gap="large")
        
        fig2d, formula = create_2d_plot(structure, calc_type, target, a_val, R)
        fig3d = create_3d_plot(structure, calc_type, target, a_val)
        
        with col_2d:
            st.markdown("#### 📊 2D 단면 / 선 배열 뷰")
            st.caption("원자의 실제 접촉 면적과 중심축을 확인하세요.")
            st.pyplot(fig2d, use_container_width=True)

        with col_3d:
            st.markdown("#### 🧊 3D 단위정 (Unit Cell) 인터랙티브 뷰")
            st.caption("마우스로 드래그하여 360도 회전 및 줌인/줌아웃이 가능합니다.")
            st.plotly_chart(fig3d, use_container_width=True)

        st.markdown("---")
        st.subheader("💡 도출된 밀도 계산 식 (원자 반경 R 기준)")
        st.latex(formula)
        
        if target == "(111) 평면":
            if "BCC" in structure:
                st.warning("**[주의]** BCC 구조의 (111) 평면은 체심(중심) 원자를 관통하지 않고 비껴갑니다. 3D 뷰어를 회전하여 체심 원자와 평면의 위치를 확인해보세요.")
            elif "FCC" in structure:
                st.success("**[핵심 포인트]** FCC의 (111) 평면은 원자가 가장 빽빽하게 배열된 **최조밀 충진면(Close-Packed Plane)**입니다.")

        with st.expander("📚 [심화 학습] 이 밀도 값이 재료의 물성에 미치는 영향 (Slip System)"):
            st.markdown(f"""
            - **슬립(Slip) 현상:** 금속 재료가 외력을 받아 소성 변형될 때, 원자들은 밀도가 가장 높은 평면(조밀면)을 따라 가장 높은 방향(조밀방향)으로 미끄러집니다.
            - **{structure}의 기계적 특성 해석:**
                - **FCC 구조:** (111) 평면과 같이 완벽한 최조밀면을 다수 포함하고 있어 슬립이 매우 쉽게 발생합니다. 이로 인해 알루미늄, 구리, 금 등은 연성(Ductility)이 매우 뛰어납니다.
                - **BCC 구조:** FCC와 같은 완벽한 최조밀면이 존재하지 않아 상온에서 슬립이 어렵습니다. 따라서 철(Fe), 텅스텐 등은 상대적으로 단단하고 강도가 높습니다.
            """)

        st.write("")
        col1, col2 = st.columns([1, 8])
        with col1:
            if st.button("⬅️ 수정하기"): navigate(-1)
        with col2:
            if st.button("🔄 처음부터 다시", type="secondary"): reset_app()

if __name__ == "__main__":
    main()
