import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="Advanced Gas Kinetics", layout="wide", initial_sidebar_state="expanded")

# --- 물리 상수 및 핵심 모듈(def) ---
R = 8.314          # 기체 상수 (J/(mol*K))
k_B = 1.380649e-23 # 볼츠만 상수 (J/K)
N_A = 6.02214e23   # 아보가드로 수 (mol^-1)

def calc_v_rms(T, M_g_mol):
    """근평균제곱속도 (m/s)"""
    M_kg = M_g_mol / 1000
    return np.sqrt(3 * R * T / M_kg)

def calc_v_avg(T, M_g_mol):
    """평균 속력 (m/s)"""
    M_kg = M_g_mol / 1000
    return np.sqrt(8 * R * T / (np.pi * M_kg))

def calc_mean_free_path(T, P, d_m):
    """평균 자유 행로 (m)"""
    return (k_B * T) / (np.sqrt(2) * np.pi * (d_m**2) * P)

def calc_collision_freq(v_avg, mfp):
    """분자당 충돌 빈도 (s^-1)"""
    return v_avg / mfp

def maxwell_boltzmann_dist(v, T, M_g_mol):
    """맥스웰-볼츠만 속력 분포 확률 밀도 함수"""
    M_kg = M_g_mol / 1000
    m = M_kg / N_A  # 분자 1개의 질량
    term1 = 4 * np.pi * (m / (2 * np.pi * k_B * T))**1.5
    term2 = (v**2) * np.exp(-(m * v**2) / (2 * k_B * T))
    return term1 * term2

# --- 대표 기체 데이터베이스 (Dictionary 활용) ---
gas_db = {
    "He (헬륨)": {"M": 4.00, "d": 2.6e-10},
    "Ne (네온)": {"M": 20.18, "d": 2.75e-10},
    "N2 (질소)": {"M": 28.02, "d": 3.64e-10},
    "O2 (산소)": {"M": 32.00, "d": 3.46e-10},
    "Ar (아르곤)": {"M": 39.95, "d": 3.40e-10},
    "CO2 (이산화탄소)": {"M": 44.01, "d": 3.30e-10}
}

# --- 사이드바: 입력 파라미터 제어 ---
with st.sidebar:
    st.header("⚙️ 실험 조건 설정")
    selected_gas = st.selectbox("분석할 기체 선택", list(gas_db.keys()))
    
    # 선택된 기체에 따라 기본값 자동 세팅
    default_M = gas_db[selected_gas]["M"]
    default_d = gas_db[selected_gas]["d"] * 1e10  # 옹스트롬 단위로 변환해서 표시
    
    T = st.slider("절대 온도 T (K)", min_value=100, max_value=1000, value=300, step=10)
    P_atm = st.number_input("압력 P (atm)", value=1.0, step=0.1)
    P_pa = P_atm * 101325  # atm to Pa 변환
    
    st.markdown("---")
    st.subheader("🛠 세부 파라미터 미세조정")
    M = st.number_input("몰 질량 (g/mol)", value=default_M)
    d_angstrom = st.number_input("충돌 직경 (Å, 10⁻¹⁰m)", value=default_d)
    d = d_angstrom * 1e-10

# --- 메인 화면 레이아웃 ---
st.title("🔬 기체 분자 운동론 (Kinetic Theory of Gases)")
st.markdown("**미시적 관점에서의 기체 거동 분석 및 시각화 플랫폼**")

# 핵심 지표 (Metrics)를 화면 최상단에 배치
v_rms = calc_v_rms(T, M)
v_avg = calc_v_avg(T, M)
mfp = calc_mean_free_path(T, P_pa, d)
z = calc_collision_freq(v_avg, mfp)

col1, col2, col3, col4 = st.columns(4)
col1.metric("근평균제곱속도 ($v_{rms}$)", f"{v_rms:.0f} m/s")
col2.metric("평균 속력 ($v_{avg}$)", f"{v_avg:.0f} m/s")
col3.metric("평균 자유 행로 ($\lambda$)", f"{mfp*1e9:.2f} nm")
col4.metric("충돌 빈도 ($Z$)", f"{z:.2e} /s")

st.markdown("---")

# 탭을 이용해 학습 자료와 시뮬레이션을 분리
tab1, tab2, tab3 = st.tabs(["📚 핵심 이론 및 수식", "📊 속력 분포 시뮬레이터", "📈 온도/압력에 따른 변화"])

with tab1:
    st.subheader("1. 속력의 종류와 맥스웰-볼츠만 분포")
    st.markdown("""
    기체 분자들은 끊임없이 무질서한 방향으로 운동하며 서로 충돌합니다. 이때 분자들의 속력은 일정한 분포를 가지는데, 이를 **맥스웰-볼츠만 분포(Maxwell-Boltzmann distribution)**라고 합니다.
    """)
    st.latex(r"f(v) = 4\pi \left(\frac{m}{2\pi k_B T}\right)^{3/2} v^2 e^{-\frac{mv^2}{2k_B T}}")
    
    st.markdown("이 분포로부터 기체 분자의 대표적인 속력들을 유도할 수 있습니다.")
    st.latex(r"v_{rms} = \sqrt{\frac{3RT}{M}}, \quad v_{avg} = \sqrt{\frac{8RT}{\pi M}}, \quad v_{mp} = \sqrt{\frac{2RT}{M}}")
    
    st.subheader("2. 평균 자유 행로 (Mean Free Path, $\lambda$)")
    st.markdown("""
    한 분자가 다른 분자와 충돌한 후, 다음 충돌이 일어날 때까지 이동한 평균 거리를 의미합니다. 
    상대 속도를 고려해야 하므로 분모에 $\sqrt{2}$ 보정 계수가 붙는 것이 핵심입니다.
    """)
    st.latex(r"\lambda = \frac{k_B T}{\sqrt{2} \pi d^2 P}")
    st.info("💡 **결론:** 온도가 높을수록(빠르게 퍼질수록), 압력이 낮을수록(분자가 적을수록), 분자 크기가 작을수록 $\lambda$는 길어집니다.")

with tab2:
    st.subheader(f"온도 {T}K 에서의 {selected_gas} 속력 분포")
    
    # 속력 범위 설정 및 분포 계산
    v_range = np.linspace(0, 2500, 1000)
    prob_dist = maxwell_boltzmann_dist(v_range, T, M)
    
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(v_range, prob_dist, color='#ff4b4b', lw=2, label=f'T = {T}K')
    ax1.fill_between(v_range, prob_dist, color='#ff4b4b', alpha=0.2)
    
    # v_rms, v_avg 위치 표시
    ax1.axvline(v_rms, color='blue', linestyle='--', label=f'v_rms ({v_rms:.0f} m/s)')
    ax1.axvline(v_avg, color='green', linestyle=':', label=f'v_avg ({v_avg:.0f} m/s)')
    
    ax1.set_xlabel("Velocity, $v$ (m/s)")
    ax1.set_ylabel("Probability Density, $f(v)$")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    st.pyplot(fig1)

with tab3:
    st.subheader("압력 변화에 따른 평균 자유 행로 ($\lambda$) 변화")
    st.markdown("일정 온도에서 압력이 증가하면 단위 부피당 입자 수가 증가하므로, 충돌할 확률이 높아져 평균 자유 행로는 짧아집니다.")
    
    P_range_atm = np.linspace(0.1, 5.0, 100)
    P_range_pa = P_range_atm * 101325
    mfp_array = [calc_mean_free_path(T, p, d) * 1e9 for p in P_range_pa] # nm 단위로 변환
    
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.plot(P_range_atm, mfp_array, color='#0068c9', lw=2)
    ax2.set_xlabel("Pressure (atm)")
    ax2.set_ylabel("Mean Free Path (nm)")
    ax2.grid(True, alpha=0.3)
    st.pyplot(fig2)
