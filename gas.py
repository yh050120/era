import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(page_title="기체 분자 운동 분석기", layout="wide")

# --- 물리 상수 및 계산 함수 (모듈화) ---
def get_v_rms(T, M):
    """근평균제곱속도 계산 (v_rms = sqrt(3RT / M))"""
    R = 8.314 # J/(mol*K)
    return np.sqrt(3 * R * T / (M / 1000))

def get_mean_free_path(T, P, d):
    """평균 자유 행로 계산 (lambda = kT / (sqrt(2) * pi * d^2 * P))"""
    k = 1.38e-23 # 볼츠만 상수
    # P는 Pa 단위, d는 m 단위 입력 가정
    return (k * T) / (np.sqrt(2) * np.pi * (d**2) * P)

# --- UI 레이아웃 ---
st.title("🧪 기체 분자 운동 및 평균 자유 행로 분석기")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("입력 파라미터")
    T = st.number_input("온도 (K)", value=300.0)
    P = st.number_input("압력 (Pa)", value=101325.0)
    M = st.number_input("몰 질량 (g/mol)", value=28.0) # 질소 기본값
    d = st.number_input("분자 지름 (10^-10 m 단위)", value=3.7) * 1e-10

with col2:
    st.subheader("분석 결과")
    v_rms = get_v_rms(T, M)
    mfp = get_mean_free_path(T, P, d)
    
    m1, m2 = st.columns(2)
    m1.metric("근평균제곱속도 (v_rms)", f"{v_rms:.2f} m/s")
    m2.metric("평균 자유 행로 (λ)", f"{mfp:.2e} m")
    
    st.info("**분석 공식**")
    st.latex(r"v_{rms} = \sqrt{\frac{3RT}{M}}, \quad \lambda = \frac{k_B T}{\sqrt{2} \pi d^2 P}")

# --- 맥스웰-볼츠만 분포 그래프 (추가 기능) ---
st.markdown("---")
st.subheader("📈 맥스웰-볼츠만 속도 분포")

def maxwell_boltzmann(v, T, M):
    R = 8.314
    m = (M / 1000) / 6.022e23
    k = 1.38e-23
    term1 = 4 * np.pi * (m / (2 * np.pi * k * T))**1.5
    term2 = v**2 * np.exp(-(m * v**2) / (2 * k * T))
    return term1 * term2

v_range = np.linspace(0, 2000, 500)
dist = maxwell_boltzmann(v_range, T, M)

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(v_range, dist, color='#00f2ff', lw=3)
ax.fill_between(v_range, dist, color='#00f2ff', alpha=0.1)
ax.set_xlabel("Velocity (m/s)")
ax.set_ylabel("Probability Density")
ax.grid(True, alpha=0.3)
st.pyplot(fig)
