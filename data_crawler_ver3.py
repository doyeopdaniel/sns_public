from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
import pandas as pd

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

# 파일 존재 여부 확인
if not os.path.exists(SOURCE_CSV):
    print(f"오류: 소스 파일을 찾을 수 없습니다: {source_file}")
    print(f"파일이 {BASE_PATH} 폴더에 있는지 확인해주세요.")
    exit()

def get_video_views(url, index):
    if not url or pd.isna(url):
        print(f"인덱스 {index}: URL 없음")
        return [0] * 10

    views = []
    retry_count = 0
    max_retries = 3  # 최대 재시도 횟수

    while retry_count < max_retries:
        try:
            driver.get(url)
            # 페이지 완전히 로드될 때까지 대기
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(8)  # 추가 대기 시간
            
            # 최대 10개의 동영상 조회수 가져오기
            for i in range(1, 11):
                try:
                    # 스크롤 조정을 더 부드럽게
                    if i > 3:
                        driver.execute_script(f"window.scrollTo(0, {(i-3)*300});")
                        time.sleep(1.5)

                    # 조회수 요소 찾기 (여러 선택자 시도)
                    selectors = [
                        f".tiktok-yvmafn-DivVideoFeedV2 > div:nth-child({i}) [data-e2e='video-views']",  # 메인 피드의 i번째 비디오
                        f".tiktok-1qb12g8-DivThreeColumnContainer > div:nth-child({i}) [data-e2e='video-views']",  # 프로필 페이지의 i번째 비디오
                        f".tiktok-x6y88p-DivItemContainerV2:nth-child({i}) [data-e2e='video-views']",  # 새로운 형식의 i번째 비디오
                        f"div[data-e2e='user-post-item-list'] > div:nth-child({i}) [data-e2e='video-views']"  # 유저 포스트 리스트의 i번째 비디오
                    ]
                    
                    view_element = None
                    for selector in selectors:
                        try:
                            view_element = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            if view_element:
                                break
                        except:
                            continue

                    if view_element:
                        view_text = view_element.text
                        view_count = parse_views(view_text)
                        views.append(view_count)
                        print(f"인덱스 {index}, 동영상 {i}: {view_count:,} 조회수")
                    else:
                        print(f"인덱스 {index}, 동영상 {i}: 조회수 요소를 찾을 수 없음")
                        views.append(0)

                except Exception as e:
                    print(f"인덱스 {index}, 동영상 {i} 처리 중 오류: {e}")
                    views.append(0)

            break  # 성공적으로 완료되면 루프 종료
        
        except Exception as e:
            retry_count += 1
            print(f"재시도 {retry_count}/{max_retries} - URL 처리 중 오류 발생 ({url}): {e}")
            if retry_count < max_retries:
                time.sleep(5)  # 재시도 전 대기
                # 페이지 새로고침
                try:
                    driver.refresh()
                except:
                    pass
            else:
                print(f"최대 재시도 횟수 초과. URL 건너뜀: {url}")
                return [0] * 10

    # 10개 미만인 경우 0으로 채우기
    views.extend([0] * (10 - len(views)))
    return views[:10]

# Chrome 드라이버 설정
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--start-maximized')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

driver = webdriver.Chrome(service=service, options=options)

try:
    # 소스 CSV 파일 읽기
    df = pd.read_csv(SOURCE_CSV)
    print(f"소스 파일 읽기 성공: {len(df)} 행")
    
    # 결과 데이터프레임 초기화
    df_result = df.copy()
    for i in range(1, 11):
        df_result[f'view{i}'] = 0
    
    # 각 URL에 대해 조회수 가져오기
    for index, row in df.iterrows():
        if index < START_INDEX:
            continue
            
        print(f"\n처리 중: {index}번째 행")
        url = row['url']
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