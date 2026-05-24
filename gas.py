import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# --- 1. 페이지 및 환경 설정 ---
st.set_page_config(page_title="고급 기체 운동론 분석기", layout="wide")

R = 8.314          
k_B = 1.380649e-23 
N_A = 6.02214e23   

def calc_v_rms(T, M_g_mol): return np.sqrt(3 * R * T / (M_g_mol / 1000))
def calc_v_avg(T, M_g_mol): return np.sqrt(8 * R * T / (np.pi * (M_g_mol / 1000)))
def calc_mean_free_path(T, P, d_m): return (k_B * T) / (np.sqrt(2) * np.pi * (d_m**2) * P)

# 기체 데이터베이스 대폭 확장 (12종)
gas_db = {
    "H2 (수소)": {"M": 2.02, "d": 2.89e-10, "color": "#FFC0CB", "type": "di"},
    "He (헬륨)": {"M": 4.00, "d": 2.60e-10, "color": "#00FFFF", "type": "mono"},
    "CH4 (메테인)": {"M": 16.04, "d": 3.80e-10, "color": "#20B2AA", "type": "poly"},
    "NH3 (암모니아)": {"M": 17.03, "d": 3.26e-10, "color": "#9370DB", "type": "poly"},
    "H2O (수증기)": {"M": 18.02, "d": 2.65e-10, "color": "#1E90FF", "type": "poly"},
    "Ne (네온)": {"M": 20.18, "d": 2.75e-10, "color": "#32CD32", "type": "mono"},
    "N2 (질소)": {"M": 28.02, "d": 3.64e-10, "color": "#4169E1", "type": "di"},
    "O2 (산소)": {"M": 32.00, "d": 3.46e-10, "color": "#FF4500", "type": "di"},
    "Ar (아르곤)": {"M": 39.95, "d": 3.40e-10, "color": "#8A2BE2", "type": "mono"},
    "CO2 (이산화탄소)": {"M": 44.01, "d": 3.30e-10, "color": "#A9A9A9", "type": "poly"},
    "Kr (크립톤)": {"M": 83.79, "d": 3.60e-10, "color": "#DAA520", "type": "mono"},
    "SF6 (육불화황)": {"M": 146.06, "d": 5.12e-10, "color": "#FFD700", "type": "poly"}
}

# --- 2. 최상단 대시보드 컨트롤러 ---
st.title("🔬 미시적 기체 분자 운동 및 거동 시뮬레이터")
st.markdown("하나의 화면에서 기체의 구조, 속력 분포, 그리고 충돌 궤적까지 순차적으로 분석할 수 있습니다. 아래에서 실험 조건을 설정하세요.")

with st.container():
    st.markdown("### ⚙️ 실험 조건 설정")
    c1, c2, c3 = st.columns(3)
    selected_gas = c1.selectbox("분석할 기체 선택", list(gas_db.keys()))
    T = c2.slider("절대 온도 (K)", 100, 1000, 300, 10)
    P_atm = c3.number_input("압력 (atm)", 0.1, 10.0, 1.0, 0.1)
    
    P_pa = P_atm * 101325
    M = gas_db[selected_gas]["M"]
    d = gas_db[selected_gas]["d"]
    color = gas_db[selected_gas]["color"]
    m_type = gas_db[selected_gas]["type"]

st.divider()

# --- 3. 기체 구조 및 핵심 지표 시각화 ---
st.markdown("### 1️⃣ 기체 분자의 입체 구조 및 핵심 지표")
v_rms = calc_v_rms(T, M)
v_avg = calc_v_avg(T, M)
mfp = calc_mean_free_path(T, P_pa, d)

col_model, col_metrics = st.columns([1, 2])

with col_model:
    fig_mol = go.Figure()
    if m_type == "mono":
        fig_mol.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', marker=dict(size=50, color=color)))
    elif m_type == "di":
        fig_mol.add_trace(go.Scatter3d(x=[-1, 1], y=[0, 0], z=[0, 0], mode='markers+lines', line=dict(width=15, color='white'), marker=dict(size=40, color=color)))
    elif m_type == "poly":
        fig_mol.add_trace(go.Scatter3d(x=[-1.5, 0, 1.5], y=[0, 0, 0], z=[0, 0, 0], mode='markers+lines', line=dict(width=15, color='white'), marker=dict(size=[30, 40, 30], color=[color, 'black', color])))
    
    fig_mol.update_layout(title="단일 분자 3D 구조 (드래그하여 회전)", scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False), margin=dict(l=0, r=0, b=0, t=30), height=300)
    st.plotly_chart(fig_mol, use_container_width=True)

with col_metrics:
    st.markdown("<br>", unsafe_allow_html=True)
    mc1, mc2 = st.columns(2)
    mc1.metric("근평균제곱속도 ($v_{rms}$)", f"{v_rms:.0f} m/s")
    mc2.metric("평균 속력 ($v_{avg}$)", f"{v_avg:.0f} m/s")
    
    with st.expander("📚 속력 관련 공식 보기 (클릭하여 펼치기)"):
        st.latex(r"v_{rms} = \sqrt{\frac{3RT}{M}}, \quad v_{avg} = \sqrt{\frac{8RT}{\pi M}}")

st.divider()

# --- 4. 맥스웰-볼츠만 속력 분포 ---
st.markdown("### 2️⃣ 기체 집단의 거동: 맥스웰-볼츠만 분포")
col_dist, col_box = st.columns([2, 1])

with col_dist:
    v_range = np.linspace(0, max(2500, v_rms*2.5), 500)
    m_kg = (M / 1000) / N_A
    term1 = 4 * np.pi * (m_kg / (2 * np.pi * k_B * T))**1.5
    prob_dist = term1 * (v_range**2) * np.exp(-(m_kg * v_range**2) / (2 * k_B * T))
    
    fig_dist = go.Figure()
    fig_dist.add_trace(go.Scatter(x=v_range, y=prob_dist, fill='tozeroy', mode='lines', line=dict(color=color, width=3), name='확률 밀도'))
    fig_dist.add_vline(x=v_rms, line_dash="dash", line_color="red", annotation_text=f"v_rms ({v_rms:.0f} m/s)")
    fig_dist.add_vline(x=v_avg, line_dash="dot", line_color="orange", annotation_text=f"v_avg ({v_avg:.0f} m/s)")
    
    fig_dist.update_layout(xaxis_title="속력 (m/s)", yaxis_title="확률 밀도", height=400, template="plotly_dark", margin=dict(l=0, r=0, b=0, t=30))
    st.plotly_chart(fig_dist, use_container_width=True)

with col_box:
    # 3D 상자 내부 기체 분자 무작위 운동
    np.random.seed(42)
    x, y, z = np.random.rand(3, 100) * 10
    speeds = np.random.normal(T, T*0.1, 100) 
    
    fig_box = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=z, mode='markers',
        marker=dict(size=M/3, color=speeds, colorscale='Inferno', opacity=0.8)
    )])
    fig_box.update_layout(title="상자 내부 분자 분포", scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False), margin=dict(l=0, r=0, b=0, t=30), height=400)
    st.plotly_chart(fig_box, use_container_width=True)

st.divider()

# --- 5. 평균 자유 행로 시뮬레이터 (신규) ---
st.markdown("### 3️⃣ 충돌 궤적 및 평균 자유 행로 (Mean Free Path, $\lambda$)")
st.markdown("기체 분자는 직진하다가 다른 분자와 부딪혀 경로를 바꿉니다. **충돌과 충돌 사이의 직선 이동 거리**를 '자유 행로(Free Path)'라 하며, 이들의 평균값이 바로 **평균 자유 행로($\lambda$)**입니다.")

col_mfp_text, col_mfp_sim = st.columns([1, 1.5])

with col_mfp_text:
    st.metric("현재 조건의 평균 자유 행로 ($\lambda$)", f"{mfp*1e9:.2f} nm")
    st.info(f"선택하신 {selected_gas.split(' ')[0]} 분자는 약 **{mfp*1e9:.2f} 나노미터** 이동할 때마다 한 번씩 다른 분자와 충돌합니다.")
    st.latex(r"\lambda = \frac{k_B T}{\sqrt{2} \pi d^2 P}")
    st.markdown("""
    * **$\sqrt{2}$**: 두 분자가 모두 움직이고 있다는 점(상대 속도)을 고려한 보정 상수입니다.
    * **$d^2$**: 분자의 크기(단면적)가 클수록 충돌 확률이 높아져 $\lambda$가 짧아집니다.
    * **$P$**: 압력이 높을수록(분자가 빽빽할수록) 충돌이 잦아져 $\lambda$가 짧아집니다.
    """)

with col_mfp_sim:
    # 2D Random Walk를 활용한 충돌 및 평균 자유 행로 궤적 시각화
    num_collisions = 7
    lambda_nm = mfp * 1e9
    
    np.random.seed(88) # 시각적으로 예쁜 궤적을 위한 시드 고정
    angles = np.random.uniform(0, 2*np.pi, num_collisions)
    # 실제 평균 자유 행로를 평균으로 하는 지수 분포로 각 스텝 생성
    step_sizes = np.random.exponential(scale=lambda_nm, size=num_collisions)
    
    x_path, y_path = [0], [0]
    for i in range(num_collisions):
        x_path.append(x_path[-1] + step_sizes[i] * np.cos(angles[i]))
        y_path.append(y_path[-1] + step_sizes[i] * np.sin(angles[i]))
        
    fig_mfp = go.Figure()
    
    # 충돌 궤적 (선)
    fig_mfp.add_trace(go.Scatter(x=x_path, y=y_path, mode='lines', line=dict(color='white', width=2, dash='dot'), name='이동 궤적'))
    
    # 충돌 지점 (점)
    fig_mfp.add_trace(go.Scatter(x=x_path, y=y_path, mode='markers', marker=dict(size=12, color=color, line=dict(width=2, color='white')), name='충돌 발생 지점'))
    
    # 특정 '자유 행로' 구간 강조 (첫 번째와 두 번째 충돌 사이)
    fig_mfp.add_annotation(
        x=(x_path[1]+x_path[2])/2, y=(y_path[1]+y_path[2])/2,
        text="이 구간이 바로 <b>'자유 행로(Free Path)'</b>",
        showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="yellow",
        font=dict(color="yellow", size=12), ax=40, ay=-40
    )
    
    fig_mfp.update_layout(
        title="단일 분자의 충돌 궤적 추적 시뮬레이터",
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        height=400, template="plotly_dark", showlegend=False, margin=dict(l=0, r=0, b=0, t=40)
    )
    st.plotly_chart(fig_mfp, use_container_width=True)
