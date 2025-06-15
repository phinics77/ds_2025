import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from folium import Choropleth, Marker
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

manual_map = {
    '창원 마산합포': '창원시 마산합포구',
    '창원 마산회원': '창원시 마산회원구',
    '창원 의창': '창원시 의창구',
    '포항 남': '포항시 남구',
    '제주': '제주시',
    '서': '서구',
    '동': '동구',
    '중': '중구',
    '수원 장안': '수원시 장안구',
    '청주 상당': '청주시 상당구',
    '고양 덕양': '고양시 덕양구',
    '천안 동남': '천안시 동남구',
    '전주 완산': '전주시 완산구',
    '남동': '남동구',
    '연수': '연수구',
    '달서': '달서구',
    '사하': '사하구',
    '강서': '강서구',
    '남해': '남해군',
    '영도': '영도구',
    '유성': '유성구',
}

def normalize_sigungu(name):
    if pd.isna(name):
        return name
    if name in manual_map:
        return manual_map[name]
    if ' ' in name:
        parts = name.split()
        if len(parts) == 2:
            return parts[0] + '시 ' + parts[1] + '구'
    if name.endswith(('시', '군', '구')):
        return name
    return name + '군'

st.set_page_config(page_title="산불 시각화", layout="wide")
st.title("🔥 산불 및 119안전센터 시각화")

df_fire = pd.read_csv("산불데이터_시군구완성.csv", encoding="cp949")
df_geo = pd.read_csv("sigungu_codes_only.csv")

gdf_geojson = gpd.read_file("TL_SCCO_SIG.geojson")
df_119 = pd.read_csv("소방청_119안전센터_현황_위경도포함.csv", encoding="cp949")  # 안전센터 데이터

df_fire['시군구_전체명'] = df_fire['시군구_전체명'].apply(normalize_sigungu)
df_merged = pd.merge(
    df_fire,
    df_geo[['시군구', 'SIG_CD']],
    left_on='시군구_전체명',
    right_on='시군구',
    how='left'
)

df_clean = df_merged.dropna(subset=['SIG_CD'])
df_result = df_clean.groupby('SIG_CD', as_index=False)['발생건수'].sum()

tab1, tab2, tab3 = st.tabs(["119안전센터 위치", "산불 패히지역 지도", "온습도 지도"])

with tab1:
    st.subheader("전국 119안전센터 위치")
    m1 = folium.Map(location=[36.5, 127.5], zoom_start=7)
    marker_cluster1 = MarkerCluster().add_to(m1)

    for _, row in df_119.dropna(subset=['위도', '경도']).iterrows():
        folium.Marker(
            location=[row['위도'], row['경도']],
            icon=folium.Icon(color='red', icon='fire', prefix='fa')
        ).add_to(marker_cluster1)

    st_folium(m1, width=900, height=600)

with tab2:
    st.subheader("산불 발생 시군구별 Choropleth 지도")
    m2 = folium.Map(location=[36.5, 127.8], zoom_start=7, tiles="CartoDB positron")

    Choropleth(
        geo_data=gdf_geojson,
        data=df_result,
        columns=['SIG_CD', '발생건수'],
        key_on='feature.properties.SIG_CD',
        legend_name='산불 발생건수',
        fill_color='YlOrRd',

        
    ).add_to(m2)

    st_folium(m2, width=900, height=600)

with tab3:
    st.subheader("습도 및 온도")
    st.dataframe(df_result)
