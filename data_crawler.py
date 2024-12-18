from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os
import traceback  # traceback 모듈 추가

# CSV 파일 읽기
df = pd.read_csv('influencer.csv', sep=',', header=0)  # CSV 파일 읽기

# 셀레니움 웹드라이버 설정
driver = webdriver.Chrome()  # Chrome 드라이버를 사용합니다. 다른 브라우저를 원하면 변경하세요.

# 시작 행 설정
start_index = 3234  # 원하는 시작 행 번호로 설정하세요

# 조회수를 숫자로 변환하는 함수
def parse_views(view_str):
    try:
        view_str = view_str.strip()
        if 'M' in view_str:
            return round(float(view_str.replace('M', '')) * 1000000)
        elif 'K' in view_str:
            return round(float(view_str.replace('K', '')) * 1000)
        elif view_str == "" or view_str is None:  # 빈 문자열 또는 None 처리
            return 0
        else:
            return int(view_str.replace(',', ''))
    except ValueError as e:
        print(f"Error parsing view string: {view_str}, Error: {e}")
        return 0  # 오류 발생 시 0으로 반환

# 조회수를 가져오는 함수
def get_video_views(url, index):
    views = []
    try:
        driver.get(url)
        # 세 번째까지는 20초, 그 이후는 5초 대기
        wait_time = 20 if index < start_index + 3 else 10
        time.sleep(wait_time)

        # 조회수를 가져오는 로직 (주어진 CSS 선택자 사용)
        for i in range(1, 11):  # 1번부터 10번까지 조회수 가져오기
            try:
                view_element = driver.find_element(By.CSS_SELECTOR, f'#main-content-others_homepage > div > div.css-833rgq-DivShareLayoutMain.ee7zj8d4 > div.css-1qb12g8-DivThreeColumnContainer.eegew6e2 > div > div:nth-child({i}) > div > div > div > a > div.css-1tda5g5-DivPlayerContainer.e19c29qe14 > div.css-11u47i-DivCardFooter.e148ts220 > strong')
                view_text = view_element.text.replace(',', '')  # 쉼표 제거
                print (f"view_text: {view_text}")
                view_count = int(parse_views(view_text))  # 조회수 변환
                views.append(view_count)  # 조회수 리스트에 추가
                print(f"Added view count: {view_count}")  # 추가된 조회수 출력
            except Exception as e:
                print(f"Error fetching view for video {i} from {url}: {e}")
                views.append(0)  # 오류 발생 시 0으로 채움

        # 만약 10개가 없으면 0으로 채워서 반환
        while len(views) < 10:
            views.append(0)

        return views[:10]  # 항상 10개를 반환
    except Exception as e:
        print(f"Error fetching views from {url}: {e}")
        return [0] * 10  # 오류 발생 시 0으로 채움

print("i am groot")

# CSV 파일 읽기
try:
    df_existing = pd.read_csv('influencer_with_views.csv', sep=',', header=0)  # 기존 데이터 읽기
except FileNotFoundError:
    df_existing = pd.DataFrame()  # 파일이 없으면 빈 데이터프레임 생성



# 각 URL에 대해 조회수 가져오기
for index, row in df.iterrows():
    if index < start_index:
        continue  # 시작 행 이전의 행은 건너뜀

    url = row['url']  # 두 번째 열에서 URL 가져오기
    if pd.isna(url) or url.strip() == "":  # URL이 비어있거나 NaN인 경우
        print(f"Warning: URL is missing for index {index}. Skipping...")
        continue  # URL이 비어있으면 다음으로 넘어감

    views = get_video_views(url, index)
    print(f"Fetched views for index {index}: {views}")  # 조회수 출력

    # 조회수를 새로운 열에 추가
    for i in range(10):
        df_existing.at[index, f'view{i + 1}'] = views[i]  # 조회수를 새로운 열에 추가

    # CSV 파일에 저장 (루프 안으로 이동)
    try:
        df_existing.to_csv('influencer_with_views.csv', index=False)  # 모든 데이터 저장
        print("Data saved for index:", index)
    except Exception as e:
        print(f"Error saving data for index {index}: {e}")

# 드라이버 종료
driver.quit()

print(df[['username', 'url']])  # username과 url 열 출력

print(df['url'].isna().sum())  # NaN 값의 개수 출력

print("Current working directory:", os.getcwd())

print(df_existing.head())  # 데이터프레임의 첫 몇 행을 출력
