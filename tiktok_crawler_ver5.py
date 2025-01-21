# 필요한 라이브러리 import
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import random
import os
import pandas as pd

# 파일 경로 및 파일명 설정
BASE_PATH = 'C:\\Users\\user\\Desktop\\sns_crawler'
SOURCE_FILE = 'hashtag_challenge.csv'
RESULT_FILE = 'tiktok_data_challenge.csv'
NULL_RESULT_FILE = 'null_hashtag.csv'

# 전체 파일 경로 생성
source_path = os.path.join(BASE_PATH, SOURCE_FILE)
result_path = os.path.join(BASE_PATH, RESULT_FILE)
null_result_path = os.path.join(BASE_PATH, NULL_RESULT_FILE)

# CSV 파일에서 해시태그 읽기
df = pd.read_csv(source_path, names=['id', 'type', 'hashtag'])
hashtags = df['hashtag'].tolist()

# 결과 파일 존재 여부 확인 및 생성
if not os.path.exists(result_path):
    with open(result_path, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['hashtag', 'name']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
    print(f"새로운 결과 파일이 생성되었습니다: {RESULT_FILE}")

if not os.path.exists(null_result_path):
    with open(null_result_path, mode='w', newline='', encoding='utf-8') as null_file:
        fieldnames = ['source_file', 'hashtag', 'index']
        writer = csv.DictWriter(null_file, fieldnames=fieldnames)
        writer.writeheader()
    print(f"새로운 null 결과 파일이 생성되었습니다: {NULL_RESULT_FILE}")

# 크롬 드라이버 설정
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.get("https://www.tiktok.com")

# null_hashtags 리스트 초기화
null_hashtags = []

for hashtag_idx, hashtag in enumerate(hashtags):
    print(f"현재 처리 중인 해시태그: {hashtag}")
    collected_names = []
    
    try:
        # 검색창 찾기 및 클릭
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-e2e='search-box']"))
        )
        search_box.click()
        
        # 검색어 입력
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-e2e='search-input']"))
        )
        search_input.clear()
        search_input.send_keys(hashtag)
        search_input.send_keys(Keys.RETURN)
        time.sleep(3)

        # 데이터 수집 및 저장
        with open(result_path, mode='a', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['hashtag', 'name']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            if csv_file.tell() == 0:
                writer.writeheader()

            not_found_count = 0
            collected_count = 0
            current_index = 0

            while collected_count < 50:
                if not_found_count >= 20:
                    current_index += 20
                    not_found_count = 0

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
                    writer.writerow({'hashtag': hashtag, 'name': text})
                    collected_names.append(text)
                    collected_count += 1
                    current_index += 1
                except:
                    print(f"요소 {current_index}를 찾을 수 없음")
                    not_found_count += 1
                    current_index += 1

        print(f"해시태그 '{hashtag}'에서 수집된 총 name 개수: {len(collected_names)}")

        if len(collected_names) < 5:
            null_hashtags.append({
                'source_file': SOURCE_FILE,
                'hashtag': hashtag,
                'index': hashtag_idx
            })

    except Exception as e:
        print(f"해시태그 '{hashtag}' 처리 중 오류 발생: {e}")
        print("다음 해시태그로 넘어갑니다.")
        continue

# null_hashtag.csv 파일 저장
if null_hashtags:
    with open(null_result_path, mode='w', newline='', encoding='utf-8') as null_file:
        fieldnames = ['source_file', 'hashtag', 'index']
        writer = csv.DictWriter(null_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(null_hashtags)
    print(f"{NULL_RESULT_FILE} 파일이 생성되었습니다.")

print("크롤링이 완료되었습니다.")
driver.quit()