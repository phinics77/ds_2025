import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from folium import Choropleth, Marker
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
manual_map = {}

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
st.title("산불 대처를 위한 방안")

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

tab1, tab2, tab3, tab4 , tab5 = st.tabs(["119안전센터 위치", "산불 패히지역 지도","임시탭3", "소방자원 분포표", "소방서 출동시간과 피해의 상관관계"])

with tab1:
    st.subheader("전국 119안전센터 및 대응 현황")

    subtab1, subtab2 = st.tabs(["119안전센터 위치 및 골든타임", "지자체별 헬기 보유 현황"])

    with subtab1:
        col1, col2 = st.columns([1, 1.2])

        with col1:
            m1 = folium.Map(location=[36.5, 127.5], zoom_start=7)
            marker_cluster1 = MarkerCluster().add_to(m1)

            for _, row in df_119.dropna(subset=['위도', '경도']).iterrows():
                folium.Marker(
                    location=[row['위도'], row['경도']],
                    icon=folium.Icon(color='red', icon='fire', prefix='fa')
                ).add_to(marker_cluster1)

            st_folium(m1, width=650, height=650)

        with col2:
            df_gold = pd.DataFrame({
                '지역': ['충남', '전북', '충북', '경기', '강원', '대구', '전남', '경북', '경남', '부산', '울산'],
                '골든타임 초과': [72, 41, 21, 43, 37, 4, 22, 25, 19, 8, 0],
                '골든타임 준수': [11, 19, 43, 66, 60, 9, 56, 93, 67, 18, 18]
            })

            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                y=df_gold["지역"],
                x=df_gold["골든타임 초과"],
                name="골든타임 초과",
                orientation="h",
                marker_color="red"
            ))
            fig_bar.add_trace(go.Bar(
                y=df_gold["지역"],
                x=df_gold["골든타임 준수"],
                name="골든타임 준수",
                orientation="h",
                marker_color="skyblue"
            ))

            fig_bar.update_layout(
                title="지자체별 헬기 골든타임(30분) 초과/준수 건수",
                xaxis_title="건수",
                barmode="stack",
                height=400
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            total_over = df_gold["골든타임 초과"].sum()
            total_in = df_gold["골든타임 준수"].sum()

            fig_pie = px.pie(
                names=["골든타임 초과", "골든타임 준수"],
                values=[total_over, total_in],
                title="전체 골든타임 초과/준수 비율 (2022~2024)",
                color_discrete_map={
                    "골든타임 초과": "red",
                    "골든타임 준수": "skyblue"
                },
                hole=0.3
            )
            fig_pie.update_traces(textinfo='label+percent+value')
            st.plotly_chart(fig_pie, use_container_width=True)

    with subtab2:
        st.image("지자체별 헬기보유.png", width=600, caption="지자체별 헬기 보유 현황 (2022~2024)")


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
    st.subheader("test1123234")

with tab4:
    st.subheader("효율적인 소방자원 분포표")

with tab5:
    st.subheader("소방서의 출동시간과 피해의 상관관계")
    col1, col2 = st.columns(2)
    with col1:
        st.image("산불.png", caption="소방출동", width=320)
    with col2:
        st.image("산불2.png", caption="소방출동", width=320)
        st.markdown("""
    그래프를 보면 소방대원이 현장에 빠르게 도착할수록 화재 피해 면적이 눈에 띄게 줄어드는 것을 확인할 수 있습니다. 초기 진압이 지연될수록 피해 면적은 급격히 커지는 경향을 보입니다. 이는 빠른 대응이 재난 피해 최소화에 결정적인 영향을 미친다는 사실을 잘 보여줍니다.
    """)