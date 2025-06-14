import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster
import pandas as pd

st.title("전국 119안전센터 위치 지도")

# CSV 파일 불러오기
df = pd.read_csv("소방청_119안전센터_현황_위경도포함.csv", encoding='cp949')

# 컬럼 정리
df.rename(columns=lambda x: x.strip(), inplace=True)
df[['lat', 'lon']] = df[['위도', '경도']]

# 데이터 미리보기
st.subheader("📋 119안전센터 데이터")
st.dataframe(df[['시도본부', '119안전센터명', '주소', '전화번호', 'lat', 'lon']], height=300)

# 지도 생성
m = folium.Map(location=[36.5, 127.5], zoom_start=7)
marker_cluster = MarkerCluster().add_to(m)

for _, row in df.dropna(subset=['lat', 'lon']).iterrows():
    popup_text = f"""
    <b>{row['119안전센터명']}</b><br>
    {row['주소']}<br>
    전화: {row['전화번호']}
    """
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=popup_text,
        icon=folium.Icon(color="red", icon="fire")
    ).add_to(marker_cluster)

# 지도 출력
st.subheader("🗺️ 지도에서 119안전센터 확인")
st_folium(m, width=800, height=600)
