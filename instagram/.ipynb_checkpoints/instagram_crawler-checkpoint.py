from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import keyboard
import os
import random
import csv
import pandas as pd
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains

# 파일 경로 및 파일명 설정
BASE_PATH = os.path.join(os.getcwd(), 'instagram_result')  # 현재 작업 디렉토리 아래에 결과 폴더 생성
SOURCE_FILE = 'hashtag_challenge.csv'
RESULT_FILE = 'instagram_data_challenge.csv'
NULL_RESULT_FILE = 'null_hashtag_challenge.csv'
COLLECTION_STATS_FILE = 'collection_stats_challenge.csv'

# 크롤링 시작 인덱스 설정
START_INDEX = 1  # 여기서 시작 인덱스를 설정하세요

# 전체 파일 경로 생성
source_path = os.path.join(BASE_PATH, SOURCE_FILE)
result_path = os.path.join(BASE_PATH, RESULT_FILE)
null_result_path = os.path.join(BASE_PATH, NULL_RESULT_FILE)
stats_path = os.path.join(BASE_PATH, COLLECTION_STATS_FILE)

# BASE_PATH 디렉토리가 없으면 생성
if not os.path.exists(BASE_PATH):
    os.makedirs(BASE_PATH)
    print(f"결과 저장을 위한 디렉토리를 생성했습니다: {BASE_PATH}")

# 결과 파일들이 없을 경우 생성
if not os.path.exists(result_path):
    with open(result_path, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['name', 'video']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
    print(f"새로운 결과 파일이 생성되었습니다: {RESULT_FILE}")

if not os.path.exists(null_result_path):
    with open(null_result_path, mode='w', newline='', encoding='utf-8') as null_file:
        fieldnames = ['source_file', 'hashtag', 'index']
        writer = csv.DictWriter(null_file, fieldnames=fieldnames)
        writer.writeheader()
    print(f"새로운 null 결과 파일이 생성되었습니다: {NULL_RESULT_FILE}")

if not os.path.exists(stats_path):
    with open(stats_path, mode='w', newline='', encoding='utf-8') as stats_file:
        fieldnames = ['hashtag', 'names', 'count']
        writer = csv.DictWriter(stats_file, fieldnames=fieldnames)
        writer.writeheader()
    print(f"새로운 통계 파일이 생성되었습니다: {COLLECTION_STATS_FILE}")

# Chrome 드라이버 서비스 설정
service = Service(ChromeDriverManager().install())

# Chrome 옵션 설정 추가
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')  # SSL 오류 무시
chrome_options.add_argument('--disable-gpu')  # GPU 가속 비활성화
chrome_options.add_argument('--window-size=1920,1080')  # 윈도우 크기 설정

# 드라이버 생성 시 옵션 적용
driver = webdriver.Chrome(service=service, options=chrome_options)

# 소스 CSV 파일 읽기
df = pd.read_csv(source_path, names=['id', 'type', 'hashtag'])
hashtags = df['hashtag'].tolist()[START_INDEX:]  # 시작 인덱스부터 해시태그 리스트 생성

driver.get("https://www.instagram.com")
time.sleep(20)

# 데이터를 저장할 리스트 생성
collected_data = []

for hashtag in hashtags:  # 해시태그 반복문
    # 검색 버튼 클릭
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.x1iyjqo2.xh8yej3 > div:nth-child(2) > span"))
    )
    try:
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)
    time.sleep(2)

    try:
        input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'x1iyjqo2')]//input"))
        )
        # 1. 마우스 움직임 추가
        actions = ActionChains(driver)
        actions.move_to_element_with_offset(input_element, random.randint(-5, 5), random.randint(-5, 5))
        actions.perform()
        time.sleep(random.uniform(0.5, 1.5))
        input_element.clear()
        for char in hashtag:
            input_element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))  # 타이핑 간격
        time.sleep(random.uniform(1, 2))

        # 2. 페이지 로딩 시 가끔 위로 살짝 스크롤
        if random.random() < 0.2:  # 20% 확률로
            driver.execute_script("window.scrollBy(0, -150);")
            time.sleep(random.uniform(0.8, 1.5))
    except TimeoutException:
        print("검색창을 찾을 수 없습니다")
    except Exception as e:
        print(f"입력 중 오류 발생: {str(e)}")

    # 검색 결과 첫 번째 항목 클릭
    try:
        result_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.x6s0dn4 > div > a:first-child"))
        )
        # 스크롤해서 요소를 화면에 보이게 만들기
        driver.execute_script("arguments[0].scrollIntoView(true);", result_element)
        time.sleep(2)
        # JavaScript로 클릭 실행
        driver.execute_script("arguments[0].click();", result_element)
        time.sleep(3)
    except TimeoutException:
        print("검색 결과를 찾을 수 없습니다")
    except Exception as e:
        print(f"검색 결과 클릭 중 오류 발생: {str(e)}")

    # 여기서 기존 그리드 반복문 시작
    for row in range(2, 50):
        for col in range(1, 4):
            # CSS Selector 패턴에서 nth-child 부분만 동적으로 교체
            # 아래 selector 앞부분은 사용자의 환경/HTML 구조에 따라 그대로 복사
            # 뒤쪽 div:nth-child({row})와 div:nth-child({col}) 부분을 포매팅
               # 변수 값 확인

                try:
                    # 먼저 게시물 클릭
                    element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 
                            f"main > div > div > div > div:nth-child({row}) > div:nth-child({col}) div"
                        ))
                    )
                    # 마우스를 요소 주변으로 자연스럽게 이동
                    actions = ActionChains(driver)
                    actions.move_to_element_with_offset(element, random.randint(-5, 5), random.randint(-5, 5))
                    actions.perform()
                    time.sleep(random.uniform(0.5, 1.5))
                    element.click()
                    time.sleep(random.uniform(2, 4))  # 랜덤한 대기 시간

                    # 2. 가끔 페이지 위아래로 살짝 스크롤
                    if random.random() < 0.3:  # 30% 확률로
                        small_scroll = random.randint(-100, 100)
                        driver.execute_script(f"window.scrollBy(0, {small_scroll});")
                        time.sleep(random.uniform(0.5, 1.5))
                        driver.execute_script(f"window.scrollBy(0, {-small_scroll});")  # 원위치
                        time.sleep(random.uniform(0.3, 0.8))

                    # username 가져오기 (더 단순화된 선택자)
                    username_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 
                            "article div._aar0._aar1 div > a"
                        ))
                    )
                    username = username_element.text
                    print(f"Found username: {username}")

                    # 2. 데이터 저장
                    data = {
                        'hashtag': hashtag,
                        'username': username
                    }
                    
                    # 리스트에 데이터 추가
                    collected_data.append(data)
                    
                    # CSV 파일로 저장
                    df = pd.DataFrame([data])
                    df.to_csv('instagram_data.csv', mode='a', header=not os.path.exists('instagram_data.csv'), index=False)

                    # 3. 닫기 버튼 클릭
                    close_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 
                            "body > div > div > div > div > div > div > svg[aria-label='닫기']"
                        ))
                    )
                    close_button.click()
                    time.sleep(random.uniform(1.5, 3))  # 랜덤한 대기 시간

                    # 4. 자연스러운 스크롤
                    if col == 3:  # 한 행의 마지막 열에서
                        # 랜덤한 크기로 스크롤
                        scroll_amount = random.randint(250, 400)
                        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                        time.sleep(random.uniform(0.8, 2))  # 랜덤한 대기 시간

                except TimeoutException:
                    print(f"요소를 찾을 수 없습니다. 다음 해시태그로 넘어갑니다.")
                    break  # 현재 row, col 반복문을 빠져나가고
                    continue  # 다음 해시태그로 진행

                except NoSuchElementException:
                    # 해당 셀렉터에 요소가 없으면 패스
                    pass

    # 최종 수집된 데이터 확인
    print(f"총 {len(collected_data)}개의 요소를 수집했습니다.")

    try:
        # 데이터 수집 및 실시간 저장
        not_found_count = 0
        collected_count = 0
        current_index = 0

        while collected_count < 50:
            if not_found_count >= 20:
                print(f"해시태그 '{hashtag}': 연속 20회 이상 요소를 찾지 못했습니다. 다음 해시태그로 넘어갑니다.")
                # 현재까지의 수집 결과 저장
                with open(stats_path, mode='a', newline='', encoding='utf-8') as stats_file:
                    writer = csv.DictWriter(stats_file, fieldnames=['hashtag', 'names', 'count'])
                    writer.writerow({
                        'hashtag': hashtag,
                        'names': ','.join(collected_data),
                        'count': len(collected_data)
                    })
                
                # 수집된 이름이 5개 미만인 경우 null_hashtags에 저장
                if len(collected_data) < 5:
                    with open(null_result_path, mode='a', newline='', encoding='utf-8') as null_file:
                        writer = csv.DictWriter(null_file, fieldnames=['source_file', 'hashtag', 'index'])
                        writer.writerow({
                            'source_file': SOURCE_FILE,
                            'hashtag': hashtag,
                            
                        })
                break  # while 루프 종료

            scroll_distance = random.randint(100, 1000)
            driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
            time.sleep(2)

            try:
                css_selector = f"#search_top-item-user-link-{current_index} > div > p"
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
                )
                text = element.text
                print(f"찾은 사용자: {text}")
                
                # 결과 실시간 저장
                with open(result_path, mode='a', newline='', encoding='utf-8') as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=['name', 'video'])
                    writer.writerow({'name': text})
                
                collected_data.append(text)
                collected_count += 1
                current_index += 1
                not_found_count = 0  # 요소를 찾았으므로 카운터 초기화
            except:
                print(f"요소 {current_index}를 찾을 수 없음")
                not_found_count += 1
                current_index += 1

        # 50개 수집 완료 후 통계 저장
        if collected_count >= 50:
            with open(stats_path, mode='a', newline='', encoding='utf-8') as stats_file:
                writer = csv.DictWriter(stats_file, fieldnames=['hashtag', 'names', 'count'])
                writer.writerow({
                    'hashtag': hashtag,
                    'names': ','.join(collected_data),
                    'count': len(collected_data)
                })

    except Exception as e:
        print(f"해시태그 '{hashtag}' 처리 중 오류 발생: {e}")
        # 오류 발생 시 통계 즉시 저장
        with open(stats_path, mode='a', newline='', encoding='utf-8') as stats_file:
            writer = csv.DictWriter(stats_file, fieldnames=['hashtag', 'names', 'count'])
            writer.writerow({
                'hashtag': hashtag,
                'names': '',
                'count': 0
            })
        continue

print("크롤링이 완료되었습니다.")
driver.quit()