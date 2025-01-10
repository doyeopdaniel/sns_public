from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
import os
import traceback

# 기본 경로 설정
BASE_PATH = r"C:\Users\user\Desktop\sns_crawler"

# 현재 작업 디렉토리를 sns_crawler 폴더로 변경
os.chdir(BASE_PATH)
print(f"작업 디렉토리를 변경했습니다: {os.getcwd()}")

# 사용자 입력 받기
print("\n=== 크롤링 설정 ===")
source_file = input("소스 CSV 파일명을 입력하세요 (예: tiktoker_meme.csv): ")
result_file = input("결과 CSV 파일명을 입력하세요 (예: tiktoker_meme_with_views.csv): ")
start_index = int(input("시작할 인덱스를 입력하세요 (기본값 0): ") or "0")

# 파일 경로 설정
SOURCE_CSV = os.path.join(BASE_PATH, source_file)
RESULT_CSV = os.path.join(BASE_PATH, result_file)
START_INDEX = start_index

print(f"\n소스 파일: {SOURCE_CSV}")
print(f"결과 파일: {RESULT_CSV}")
print(f"시작 인덱스: {START_INDEX}\n")

# 파일 존재 여부 확인
if not os.path.exists(SOURCE_CSV):
    print(f"오류: 소스 파일을 찾을 수 없습니다: {source_file}")
    print(f"파일이 {BASE_PATH} 폴더에 있는지 확인해주세요.")
    exit()

# 결과 CSV 파일 미리 생성
def initialize_result_csv():
    try:
        # 기본 열 구조 생성
        columns = ['username', 'url']  # 기존 데이터 열
        columns.extend([f'view{i}' for i in range(1, 11)])  # view1 ~ view10 열 추가
        
        # 소스 데이터에서 username과 url 가져오기
        initial_data = df[['username', 'url']].copy()
        
        # view1 ~ view10 열을 0으로 초기화
        for i in range(1, 11):
            initial_data[f'view{i}'] = 0
        
        # CSV 파일로 저장
        initial_data.to_csv(RESULT_CSV, index=False)
        print(f"결과 파일 생성 완료: {RESULT_CSV}")
        return initial_data
        
    except Exception as e:
        print(f"결과 파일 생성 중 오류 발생: {e}")
        raise

# 조회수를 숫자로 변환하는 함수
def parse_views(view_str):
    try:
        if not view_str or pd.isna(view_str):
            return 0
        
        view_str = view_str.strip()
        if 'M' in view_str:
            return round(float(view_str.replace('M', '')) * 1000000)
        elif 'K' in view_str:
            return round(float(view_str.replace('K', '')) * 1000)
        else:
            return int(view_str.replace(',', ''))
    except Exception as e:
        print(f"조회수 변환 오류 ({view_str}): {e}")
        return 0

# 조회수를 가져오는 함수
def get_video_views(url, index):
    if not url or pd.isna(url):
        print(f"인덱스 {index}: URL 없음")
        return [0] * 10

    views = []
    try:
        driver.get(url)
        wait_time = 20 if index < START_INDEX + 3 else 10
        time.sleep(wait_time)

        # 최대 10개의 동영상 조회수 가져오기
        for i in range(1, 11):
            try:
                # WebDriverWait 사용하여 요소 대기
                view_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 
                    f'#main-content-others_homepage > div > div.css-833rgq-DivShareLayoutMain.ee7zj8d4 > div.css-1qb12g8-DivThreeColumnContainer.eegew6e2 > div > div:nth-child({i}) > div > div > div > a > div.css-1tda5g5-DivPlayerContainer.e19c29qe14 > div.css-11u47i-DivCardFooter.e148ts220 > strong'))
                )
                view_text = view_element.text
                view_count = parse_views(view_text)
                views.append(view_count)
                print(f"인덱스 {index}, 동영상 {i}: {view_count:,} 조회수")
            except TimeoutException:
                print(f"인덱스 {index}, 동영상 {i}: 시간 초과")
                views.append(0)
            except Exception as e:
                print(f"인덱스 {index}, 동영상 {i} 오류: {e}")
                views.append(0)

        # 10개 미만인 경우 0으로 채우기
        views.extend([0] * (10 - len(views)))
        return views[:10]

    except Exception as e:
        print(f"URL 처리 중 오류 발생 ({url}): {e}")
        return [0] * 10

# 메인 코드 시작
try:
    # 소스 CSV 파일 읽기 (에러 처리 옵션 추가)
    df = pd.read_csv(SOURCE_CSV, 
                     encoding='utf-8',
                     on_bad_lines='skip',  # 문제가 있는 행은 건너뛰기
                     engine='python',       # python 엔진 사용
                     sep=',')              # 구분자 명시
    
    print(f"소스 파일 읽기 성공: {len(df)} 행")
    
    # 필요한 열이 있는지 확인
    required_columns = ['username', 'url']
    if not all(col in df.columns for col in required_columns):
        print(f"오류: 필수 열({required_columns})이 없습니다.")
        print(f"현재 파일의 열: {df.columns.tolist()}")
        exit()
    
    # 결과 파일 초기화
    df_result = initialize_result_csv()
    print("결과 파일 초기화 완료")
    
    # 셀레니움 웹드라이버 설정
    driver = webdriver.Chrome()
    
    # 각 URL에 대해 조회수 가져오기
    for index, row in df.iterrows():
        if index < START_INDEX:
            continue

        print(f"\n처리 중: {index}번째 행")
        url = row.get('url', '')
        views = get_video_views(url, index)

        # 결과 저장
        for i, view in enumerate(views, 1):
            df_result.at[index, f'view{i}'] = view

        # 주기적으로 저장 (5행마다)
        if index % 5 == 0:
            df_result.to_csv(RESULT_CSV, index=False)
            print(f"{index}번째 행까지 저장 완료")
    # 최종 저장
    df_result.to_csv(RESULT_CSV, index=False)
    print("\n크롤링 완료!")

except Exception as e:
    print(f"크롤링 중 오류 발생: {e}")
    traceback.print_exc()

finally:
    driver.quit()
    print("\n브라우저를 종료했습니다.")

# 결과 확인
print("\n크롤링 결과 미리보기:")
try:
    final_df = pd.read_csv(RESULT_CSV)
    print(final_df.head())
    print(f"\n총 처리된 행 수: {len(final_df)}")
except Exception as e:
    print(f"결과 파일 읽기 실패: {e}")
    