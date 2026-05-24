import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="3D 기체 분자 운동론", layout="wide", initial_sidebar_state="expanded")

# --- 물리 상수 및 핵심 함수 ---
R = 8.314          
k_B = 1.380649e-23 
N_A = 6.02214e23   

def calc_v_rms(T, M_g_mol): return np.sqrt(3 * R * T / (M_g_mol / 1000))
def calc_v_avg(T, M_g_mol): return np.sqrt(8 * R * T / (np.pi * (M_g_mol / 1000)))
def calc_mean_free_path(T, P, d_m): return (k_B * T) / (np.sqrt(2) * np.pi * (d_m**2) * P)

gas_db = {
    "He (단원자, 헬륨)": {"M": 4.00, "d": 2.6e-10, "color": "#00FFFF", "type": "mono"},
    "N2 (이원자, 질소)": {"M": 28.02, "d": 3.64e-10, "color": "#4169E1", "type": "di"},
    "O2 (이원자, 산소)": {"M": 32.00, "d": 3.46e-10, "color": "#FF4500", "type": "di"},
    "CO2 (다원자, 이산화탄소)": {"M": 44.01, "d": 3.30e-10, "color": "#A9A9A9", "type": "poly"}
}

# --- 사이드바: 단계별 네비게이션 ---
st.sidebar.title("🧭 분석 단계 선택")
menu = st.sidebar.radio(
    "클릭해서 순차적으로 학습하세요:",
    ("1. 🧪 기체 선택 및 환경 설정", 
     "2. 🧊 3D 기체 분자 모형", 
     "3. 📈 맥스웰-볼츠만 분포", 
     "4. 💥 충돌 및 평균 자유 행로")
)

st.sidebar.markdown("---")
st.sidebar.subheader("기본 환경 변수 (공통 적용)")
# 상태 유지를 위해 세션 스테이트 사용 또는 사이드바에 고정
selected_gas = st.sidebar.selectbox("분석할 기체", list(gas_db.keys()))
T = st.sidebar.slider("온도 (K)", 100, 1000, 300, 10)
P_atm = st.sidebar.number_input("압력 (atm)", 0.1, 10.0, 1.0, 0.1)
P_pa = P_atm * 101325

M = gas_db[selected_gas]["M"]
d = gas_db[selected_gas]["d"]
color = gas_db[selected_gas]["color"]
m_type = gas_db[selected_gas]["type"]

# --- 화면 1: 환경 설정 ---
if menu == "1. 🧪 기체 선택 및 환경 설정":
    st.title("1. 기체 분자 운동론 기초 설정")
    st.markdown("좌측 메뉴에서 분석할 기체와 온도, 압력을 설정했습니다. 현재 설정된 조건은 다음과 같습니다.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("선택된 기체", selected_gas.split(" ")[0])
    col2.metric("절대 온도 (T)", f"{T} K")
    col3.metric("기압 (P)", f"{P_atm:.1f} atm")
    
    st.info("👈 **준비가 완료되었다면, 좌측 메뉴에서 '2. 3D 기체 분자 모형'을 클릭하여 다음 단계로 넘어가세요.**")

# --- 화면 2: 3D 모형 ---
elif menu == "2. 🧊 3D 기체 분자 모형":
    st.title("2. 미시적 관점: 분자의 입체 모형과 거동")
    
    col_model, col_box = st.columns(2)
    
    with col_model:
        st.subheader("단일 분자 3D 구조")
        # 분자 형태에 따른 3D 모델링
        fig_mol = go.Figure()
        if m_type == "mono":
            fig_mol.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', marker=dict(size=50, color=color)))
        elif m_type == "di":
            fig_mol.add_trace(go.Scatter3d(x=[-1, 1], y=[0, 0], z=[0, 0], mode='markers+lines', line=dict(width=15, color='white'), marker=dict(size=40, color=color)))
        elif m_type == "poly":
            fig_mol.add_trace(go.Scatter3d(x=[-1.5, 0, 1.5], y=[0, 0, 0], z=[0, 0, 0], mode='markers+lines', line=dict(width=15, color='white'), marker=dict(size=[30, 40, 30], color=[color, 'black', color])))
        
        fig_mol.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False), margin=dict(l=0, r=0, b=0, t=0), height=300)
        st.plotly_chart(fig_mol, use_container_width=True)

    with col_box:
        st.subheader("상자 내부의 분자 운동 (시뮬레이션)")
        # 100개의 기체 분자가 상자 안에서 운동하는 모습 구현
        np.random.seed(42) # 고정된 난수
        x, y, z = np.random.rand(3, 100) * 10
        speeds = np.random.normal(T, T*0.1, 100) # 온도에 따른 색상 변화용
        
        fig_box = go.Figure(data=[go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers',
            marker=dict(size=M/2, color=speeds, colorscale='Inferno', opacity=0.8)
        )])
        fig_box.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False), margin=dict(l=0, r=0, b=0, t=0), height=300)
        st.plotly_chart(fig_box, use_container_width=True)

    st.caption("마우스로 드래그하여 입체 모형을 360도로 돌려보거나 확대/축소할 수 있습니다.")

# --- 화면 3: 속력 분포 ---
elif menu == "3. 📈 맥스웰-볼츠만 분포":
    st.title("3. 기체 분자의 속력 분포 분석")
    st.markdown("모든 분자가 같은 속력으로 움직이지 않습니다. 온도가 주어졌을 때 분자들의 속력 분포를 확인해보세요.")
    
    v_rms = calc_v_rms(T, M)
    v_avg = calc_v_avg(T, M)
    
    # 3D를 썼으니 통일감을 위해 2D 그래프도 Plotly로 그려줍니다.
    v_range = np.linspace(0, 2500, 500)
    m_kg = (M / 1000) / N_A
    term1 = 4 * np.pi * (m_kg / (2 * np.pi * k_B * T))**1.5
    prob_dist = term1 * (v_range**2) * np.exp(-(m_kg * v_range**2) / (2 * k_B * T))
    
    fig_dist = go.Figure()
    fig_dist.add_trace(go.Scatter(x=v_range, y=prob_dist, fill='tozeroy', mode='lines', line=dict(color=color, width=3), name='확률 밀도'))
    fig_dist.add_vline(x=v_rms, line_dash="dash", line_color="red", annotation_text=f"v_rms ({v_rms:.0f} m/s)")
    fig_dist.add_vline(x=v_avg, line_dash="dot", line_color="orange", annotation_text=f"v_avg ({v_avg:.0f} m/s)")
    
    fig_dist.update_layout(xaxis_title="속력 (m/s)", yaxis_title="확률 밀도", height=500, template="plotly_dark")
    st.plotly_chart(fig_dist, use_container_width=True)

# --- 화면 4: 충돌 및 행로 ---
elif menu == "4. 💥 충돌 및 평균 자유 행로":
    st.title("4. 평균 자유 행로 (Mean Free Path)")
    st.markdown("분자가 다른 분자와 충돌하기 전까지 직진하는 평균 거리($\lambda$)를 계산합니다.")
    
    mfp = calc_mean_free_path(T, P_pa, d)
    
    st.latex(r"\lambda = \frac{k_B T}{\sqrt{2} \pi d^2 P}")
    
    col1, col2 = st.columns(2)
    col1.metric("계산된 평균 자유 행로 (λ)", f"{mfp*1e9:.2f} nm")
    col2.info(f"현재 {P_atm} atm 조건에서 {selected_gas.split(' ')[0]} 분자는 충돌 전 평균적으로 **{mfp*1e9:.2f} 나노미터**를 이동합니다.")
    
    st.markdown("---")
    st.subheader("💡 직관적 이해: 압력과 $\lambda$의 관계")
    st.markdown("압력이 높을수록 공간 내에 분자가 빽빽하게 들어차므로, 충돌이 잦아져 평균 이동 거리가 극심하게 짧아집니다.")
