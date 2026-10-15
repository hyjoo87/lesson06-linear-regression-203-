import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="서울 기온 예측기", page_icon="🌡️", layout="centered"
)

st.title("🌡️ 서울 연평균기온 분석 및 예측기")
st.write(
    "서울 기온 데이터를 바탕으로 연도별 평균기온의 추세를 분석하고, 전체 기간과 최근 20년의 온도 상승 추세를 비교합니다."
)


# 데이터 로드 및 전처리 함수 (캐싱 적용)
@st.cache_data
def load_and_preprocess_data():
  url = "https://raw.githubusercontent.com/greatsong/modudata/bb860932644270ad1199f10d3e7670e30231bce4/data/seoul.csv"
  df = pd.read_csv(url, encoding="utf-8")

  # 날짜 컬럼을 datetime 형식으로 변환
  df["날짜"] = pd.to_datetime(df["날짜"])
  df["연도"] = df["날짜"].dt.year

  # 1. 2025년 이후 데이터 제외
  df = df[df["연도"] <= 2025]

  # 2. 연도별 관측일수 계산 및 300일 미만인 해 제거
  yearly_counts = df.groupby("연도")["평균기온"].count()
  valid_years = yearly_counts[yearly_counts >= 300].index
  df = df[df["연도"].isin(valid_years)]

  # 3. 연도별 평균기온 계산
  annual_avg = df.groupby("연도")["평균기온"].mean().reset_index()
  annual_avg.columns = ["연도", "연평균기온"]

  # 결측치 제거
  annual_avg = annual_avg.dropna()

  return annual_avg


# 데이터 불러오기
try:
  df_annual = load_and_preprocess_data()
except Exception as e:
  st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
  st.stop()

# 회귀 분석 수행 (전체 기간)
X = df_annual["연도"]
y = df_annual["연평균기온"]

slope, intercept = np.polyfit(X, y, 1)
correlation = X.corr(y)

num_years = len(df_annual)
start_year = int(X.min())
end_year = int(X.max())

# 기본 분석 정보 표시
st.info(
    f"📊 **분석 정보 (전체 기간 기준)**\n\n"
    f"- **회귀선을 만든 해의 개수:** {num_years}개\n"
    f"- **시작 연도:** {start_year}년\n"
    f"- **끝 연도:** {end_year}년\n"
    f"- **연도와 연평균기온 간 상관계수 (r):** {correlation:.4f}"
)

st.markdown("---")

# 100년당 기온 상승 폭 비교 (전체 기간 vs 최근 20년)
max_yr = int(df_annual["연도"].max())
recent_df = df_annual[df_annual["연도"] >= max_yr - 19]

slope_all = slope  # 1년당 기울기
slope_recent, _ = np.polyfit(recent_df["연도"], recent_df["연평균기온"], 1)

rise_all = slope_all * 100
rise_recent = slope_recent * 100

st.subheader("📈 100년당 기온 상승 폭 비교")
col1, col2 = st.columns(2)
with col1:
  st.metric(
      label=f"전체 기간 ({start_year}~{end_year}년)",
      value=f"{rise_all:+.2f} ℃ / 100년",
  )
with col2:
  st.metric(
      label=f"최근 20년 ({max_yr - 19}~{max_yr}년)",
      value=f"{rise_recent:+.2f} ℃ / 100년",
  )

st.markdown("---")

# Plotly 그래프 생성
fig = px.scatter(
    df_annual,
    x="연도",
    y="연평균기온",
    title="서울 연도별 평균기온 및 추세선",
    labels={"연도": "연도", "연평균기온": "연평균기온 (°C)"},
    opacity=0.7,
)

# 전체 회귀 직선 추가
df_annual["회귀예측"] = slope_all * X + intercept
fig.add_trace(
    go.Scatter(
        x=df_annual["연도"],
        y=df_annual["회귀예측"],
        mode="lines",
        name=f"전체 회귀 직선 (100년당 {rise_all:+.2f}℃)",
        line=dict(color="red", width=2),
    )
)

fig.update_layout(
    xaxis_title="연도",
    yaxis_title="연평균기온 (°C)",
    hovermode="x unified",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# 슬라이더를 통한 연도별 예상 기온 확인
st.subheader("🔮 연도별 예상 기온 조회")
selected_year = st.slider(
    "조회할 연도를 선택하세요 (1900년 ~ 2100년)",
    min_value=1900,
    max_value=2100,
    value=2026,
    step=1,
)

# 선택된 연도의 예상 기온 계산 (전체 회귀선 기준)
predicted_temp = slope_all * selected_year + intercept

# 결과 강조 표시
st.markdown(
    f"""
    <div style="padding: 20px; border-radius: 10px; background-color: #f0f2f6; text-align: center;">
        <h3 style="margin: 0; color: #31333F;">📅 {selected_year}년 서울 예상 연평균기온</h3>
        <h1 style="margin: 10px 0 0 0; color: #ff4b4b;">{predicted_temp:.2f} °C</h1>
        <p style="margin: 5px 0 0 0; color: #666666; font-size: 14px;">전체 회귀 분석 기준</p>
    </div>
    """,
    unsafe_allow_html=True,
)
