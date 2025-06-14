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

tab1, tab2 , tab3 , tab4 = st.tabs(['소방서 위치' , '산불피해지역', '피해면적', ''])

# 소방서 위치 탭

with tab1:
    st.subheader("소방서 위치")
    st.write("전국의 소방서 위치를 지도에서 확인할 수 있습니다.")
    for _, row in df.dropna(subset=['lat', 'lon']).iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            icon=folium.Icon(color="red", icon="fire station", prefix='fa'),
        ).add_to(marker_cluster)

    # 지도 출력
    st.subheader("🗺️ 지도에서 119안전센터 확인")
    st_folium(m, width=800, height=600)

with tab2:
    st.subheader("산불피해지역")
    st.write("산불피해지역을 지도에서 확인할 수 있습니다.")
    # 산불피해지역 데이터 로드
    wildfire_data = pd.read_csv("산불피해지역.csv", encoding='cp949')
    for _, row in wildfire_data.iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            icon=folium.Icon(color="orange", icon="fire", prefix='fa'),
        ).add_to(marker_cluster)

    # 지도 출력
    st_folium(m, width=800, height=600)