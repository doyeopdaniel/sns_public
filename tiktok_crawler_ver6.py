from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import keyboard
import os
import random
import csv
import pandas as pd

# 파일 경로 및 파일명 설정
BASE_PATH = 'C:\\Users\\user\\Desktop\\sns_crawler'
SOURCE_FILE = 'hashtag_challenge.csv'
RESULT_FILE = 'tiktok_data_challenge.csv'
NULL_RESULT_FILE = 'null_hashtag_challenge.csv'
COLLECTION_STATS_FILE = 'collection_stats_challenge.csv'

# 전체 파일 경로 생성
source_path = os.path.join(BASE_PATH, SOURCE_FILE)
result_path = os.path.join(BASE_PATH, RESULT_FILE)
null_result_path = os.path.join(BASE_PATH, NULL_RESULT_FILE)
stats_path = os.path.join(BASE_PATH, COLLECTION_STATS_FILE)

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
driver = webdriver.Chrome(service=service)

# 소스 CSV 파일 읽기
df = pd.read_csv(source_path, names=['id', 'type', 'hashtag'])
hashtags = df['hashtag'].tolist()

driver.get("https://www.tiktok.com")
time.sleep(2)

for hashtag_idx, hashtag in enumerate(hashtags):
    print(f"현재 처리 중인 해시태그: {hashtag}")
    collected_names = []
    
    try:
        # 검색창 찾기 및 클릭
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#app > div.css-1yczxwx-DivBodyContainer.e1irlpdw0 > div.css-flkb7b-DivSideNavPlaceholderContainer.e1u58fka0 > div > div.css-m8ow1x-DivFixedContentContainer.e1u58fka2 > div.css-1icvwlp-DivSearchWrapper.e1u58fka4 > button"))
        )
        element.click()
        time.sleep(10)
        
        # 검색어 입력
        input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#app > div.css-1yczxwx-DivBodyContainer.e1irlpdw0 > div.css-flkb7b-DivSideNavPlaceholderContainer.e1u58fka0 > div > div.css-6dsq89-DivDrawerContainer.e1lvfea00.drawer-enter-done > div.css-kdngec-DivSearchContainer.e1lvfea05 > div.css-1asq5wp-DivSearchFormContainer.e1hi1cmj0 > form > input"))
        )
        input_element.send_keys(Keys.CONTROL + 'a')
        input_element.send_keys(Keys.BACKSPACE)
        input_element.send_keys(hashtag)
        time.sleep(10)
        input_element.send_keys(Keys.RETURN)

    except:
        # 두 번째 검색 방법 시도
        try:
            input_element = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#app-header > div > div.css-3z2zs6-DivHeaderCenterContainer.etz70ds0 > div > form > input"))
            )
            input_element.send_keys(Keys.CONTROL + 'a')
            input_element.send_keys(Keys.BACKSPACE)
            time.sleep(10)
            input_element.send_keys(hashtag)

            element = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#app-header > div > div.css-3z2zs6-DivHeaderCenterContainer.etz70ds0 > div > form > button"))
            )
            element.click()
            time.sleep(10)
        except Exception as e:
            print(f"검색창 찾기 실패: {e}")
            # 실패한 해시태그 정보 즉시 저장
            with open(null_result_path, mode='a', newline='', encoding='utf-8') as null_file:
                writer = csv.DictWriter(null_file, fieldnames=['source_file', 'hashtag', 'index'])
                writer.writerow({
                    'source_file': SOURCE_FILE,
                    'hashtag': hashtag,
                    'index': hashtag_idx
                })
            continue

    try:
        # 데이터 수집 및 실시간 저장
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
                
                # 결과 실시간 저장
                with open(result_path, mode='a', newline='', encoding='utf-8') as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=['name', 'video'])
                    writer.writerow({'name': text})
                
                collected_names.append(text)
                collected_count += 1
                current_index += 1
            except:
                print(f"요소 {current_index}를 찾을 수 없음")
                not_found_count += 1
                current_index += 1

        # 해시태그별 수집 결과 실시간 저장
        print(f"해시태그 '{hashtag}'에서 수집된 총 name 개수: {len(collected_names)}")
        with open(stats_path, mode='a', newline='', encoding='utf-8') as stats_file:
            writer = csv.DictWriter(stats_file, fieldnames=['hashtag', 'names', 'count'])
            writer.writerow({
                'hashtag': hashtag,
                'names': ','.join(collected_names),
                'count': len(collected_names)
            })

        # 수집된 이름이 5개 미만인 경우 즉시 null_hashtags에 저장
        if len(collected_names) < 5:
            with open(null_result_path, mode='a', newline='', encoding='utf-8') as null_file:
                writer = csv.DictWriter(null_file, fieldnames=['source_file', 'hashtag', 'index'])
                writer.writerow({
                    'source_file': SOURCE_FILE,
                    'hashtag': hashtag,
                    'index': hashtag_idx
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