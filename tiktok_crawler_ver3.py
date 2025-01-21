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

# Chrome 드라이버 서비스 설정
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# hashtag_meme.csv 파일 경로 수정
df = pd.read_csv('hashtag_meme.csv')

# CSV 파일에서 해시태그 읽기
with open('hashtag_meme.csv', mode='r', encoding='utf-8') as hashtag_file:
    reader = csv.reader(hashtag_file)
    next(reader)  # 첫 번째 행(헤더) 건너뛰기
    hashtags = [row[2] for idx, row in enumerate(reader) if idx >= 82]

driver.get("https://www.tiktok.com")
time.sleep(2)

# null_hashtag.csv 파일 생성 준비
null_hashtags = []

for hashtag_idx, hashtag in enumerate(hashtags):
    print(f"현재 처리 중인 해시태그: {hashtag}")
    try:
        # 검색 버튼 클릭 시도
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#app > div.css-1yczxwx-DivBodyContainer.e1irlpdw0 > div.css-flkb7b-DivSideNavPlaceholderContainer.e1u58fka0 > div > div.css-m8ow1x-DivFixedContentContainer.e1u58fka2 > div.css-1icvwlp-DivSearchWrapper.e1u58fka4 > button"))
            )
            element.click()
            time.sleep(5)
            
            input_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#app > div.css-1yczxwx-DivBodyContainer.e1irlpdw0 > div.css-flkb7b-DivSideNavPlaceholderContainer.e1u58fka0 > div > div.css-6dsq89-DivDrawerContainer.e1lvfea00.drawer-enter-done > div.css-kdngec-DivSearchContainer.e1lvfea05 > div.css-1asq5wp-DivSearchFormContainer.e1hi1cmj0 > form > input"))
            )
        except:
            input_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#app-header > div > div.css-3z2zs6-DivHeaderCenterContainer.etz70ds0 > div > form > input"))
            )
            
        # 검색어 입력
        input_element.send_keys(Keys.CONTROL + 'a')
        input_element.send_keys(Keys.BACKSPACE)
        input_element.send_keys(hashtag)
        time.sleep(5)
        input_element.send_keys(Keys.RETURN)
        time.sleep(5)

        # 데이터 수집 및 저장
        with open('tiktok_data_meme.csv', mode='a', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['hashtag', 'name']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            if csv_file.tell() == 0:
                writer.writeheader()

            not_found_count = 0
            collected_count = 0
            max_attempts = 50  # 초기 시도 횟수

            while collected_count < 50 and not_found_count < 45:  # 50개 수집할 때까지 또는 45번 실패할 때까지
                scroll_distance = random.randint(100, 1000)
                driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
                time.sleep(2)

                try:
                    css_selector = f"#search_top-item-user-link-{collected_count} > div > p"
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
                    )
                    text = element.text
                    print(f"찾은 사용자: {text}")
                    writer.writerow({'hashtag': hashtag, 'name': text})
                    collected_count += 1
                except:
                    print(f"요소 {collected_count}를 찾을 수 없음, 다음 요소로 넘어갑니다.")
                    not_found_count += 1
                    max_attempts += 1  # 실패할 때마다 최대 시도 횟수 증가

            # 45회 이상 실패한 경우 null_hashtag.csv에 기록
            if not_found_count >= 45:
                null_hashtags.append({
                    'source_file': 'hashtag_meme.csv',
                    'hashtag': hashtag,
                    'index': hashtag_idx
                })

    except Exception as e:
        print(f"해시태그 '{hashtag}' 처리 중 오류 발생: {e}")
        print("다음 해시태그로 넘어갑니다.")
        continue

# null_hashtag.csv 파일 저장
if null_hashtags:
    with open('null_hashtag.csv', mode='w', newline='', encoding='utf-8') as null_file:
        fieldnames = ['source_file', 'hashtag', 'index']
        writer = csv.DictWriter(null_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(null_hashtags)
    print("null_hashtag.csv 파일이 생성되었습니다.")

print("크롤링이 완료되었습니다.")
driver.quit()