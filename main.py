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
  annual_avg = df.groupby("연
