import pandas as pd
import requests
import time

# ---- 지오코딩 함수 ---- #
def geocode_vworld(address, retries=5, delay=1):
    url = "https://api.vworld.kr/req/address"
    params = {
        "service": "address",
        "request": "getcoord",
        "version": "2.0",
        "crs": "EPSG:4326",
        "address": address,
        "type": "ROAD",
        "key": "185D3124-1C10-3B73-B240-4413FE5F986A"
    }
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data['response']['status'] == 'OK':
                point = data['response']['result']['point']
                return point['y'], point['x']  # (위도, 경도)
            else:
                print(f"API 응답 상태 오류: {data['response']['status']}")
                return None, None
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error on attempt {attempt+1}: {e}")
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error on attempt {attempt+1}: {e}")
        except requests.exceptions.Timeout as e:
            print(f"Timeout error on attempt {attempt+1}: {e}")
        except Exception as e:
            print(f"Unexpected error on attempt {attempt+1}: {e}")

        time.sleep(delay * (attempt + 1))  # 지수 백오프 개선: 1초, 2초, 3초...

    print(f"Failed to geocode address after {retries} attempts: {address}")
    return None, None

# ---- CSV 파일 불러오기 ---- #

df = pd.read_csv("소방청_119안전센터 현황_20240630.csv", encoding='cp949')

# 주소 컬럼 이름이 '주소'라고 가정
df['위도'] = None
df['경도'] = None

# ---- 주소 변환 반복 ---- #
for idx, row in df.iterrows():
    address = row['주소']
    lat, lon = geocode_vworld(address)
    df.at[idx, '위도'] = lat
    df.at[idx, '경도'] = lon
    print(f"[{idx+1}/{len(df)}] {address} → 위도: {lat}, 경도: {lon}")

# ---- 결과 저장 ---- #
df.to_csv("소방청_119안전센터_현황_위경도포함.csv", index=False, encoding='cp949')
print("✅ 변환 완료 및 저장됨: 소방청_119안전센터_현황_위경도포함.csv")
