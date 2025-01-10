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
df = pd.read_csv('C:/Users/user/Desktop/sns_crawler/hashtag_meme.csv', encoding='utf-8')

# CSV 파일에서 해시태그 읽기
with open('hashtag_meme.csv', mode='r', encoding='utf-8') as hashtag_file:
    reader = csv.reader(hashtag_file)
    next(reader)  # 첫 번째 행(헤더) 건너뛰기
    hashtags = [row[2] for idx, row in enumerate(reader) if idx >= 21]  # 두 번째 행부터 해시태그를 리스트에 저장

driver.get("https://www.tiktok.com")
time.sleep(2)
for hashtag in hashtags:
    try:
        element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#app > div.css-1yczxwx-DivBodyContainer.e1irlpdw0 > div.css-flkb7b-DivSideNavPlaceholderContainer.e1u58fka0 > div > div.css-m8ow1x-DivFixedContentContainer.e1u58fka2 > div.css-1icvwlp-DivSearchWrapper.e1u58fka4 > button"))
    )

        element.click()
        time.sleep(10)
        
        # ha 문자열 입력
        input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#app > div.css-1yczxwx-DivBodyContainer.e1irlpdw0 > div.css-flkb7b-DivSideNavPlaceholderContainer.e1u58fka0 > div > div.css-6dsq89-DivDrawerContainer.e1lvfea00.drawer-enter-done > div.css-kdngec-DivSearchContainer.e1lvfea05 > div.css-1asq5wp-DivSearchFormContainer.e1hi1cmj0 > form > input"))
        )
        input_element.send_keys(Keys.CONTROL + 'a')  # 모든 내용 선택
        input_element.send_keys(Keys.BACKSPACE)  
        # "tiktoktrend" 문자열 입력
        input_element.send_keys(hashtag)
        time.sleep(10)
        input_element.send_keys(Keys.RETURN)
        # 두 번째 요소 시도 (첫 번째가 실패할 경우)
    except:
        # 두 번째 요소 찾기
        input_element = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#app-header > div > div.css-3z2zs6-DivHeaderCenterContainer.etz70ds0 > div > form > input"))
        )
        input_element.send_keys(Keys.CONTROL + 'a')  # 모든 내용 선택
        input_element.send_keys(Keys.BACKSPACE)  

        time.sleep(10)
        # ha 문자열 입력
        input_element.send_keys(hashtag)

        element = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#app-header > div > div.css-3z2zs6-DivHeaderCenterContainer.etz70ds0 > div > form > button"))
        )

        element.click()
        time.sleep(10)

    try:
        with open('tiktok_data_meme.csv', mode='a', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['name', 'video']  # 열 이름 정의
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            # 파일이 비어있을 경우 헤더 작성
            if csv_file.tell() == 0:
                writer.writeheader()  # 헤더 작성

            # CSV에 데이터 쓰기
            for i in range(1, 51):  # 1부터 50까지 반복
                # 랜덤한 스크롤 거리 생성 (100에서 1000픽셀 사이)
                scroll_distance = random.randint(100, 1000)

                # 스크롤을 페이지의 아래로 이동
                driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
                time.sleep(2)  # 페이지가 로드될 시간을 기다림

                try:
                    # 첫 번째 요소의 CSS 선택자
                    css_selector_1 = f"#search_top-item-user-link-{i-1} > div > p"  # 0부터 시작하는 인덱스

                    
                    # 첫 번째 요소 찾기
                    element_1 = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector_1))
                    )
                    
                    # 첫 번째 요소의 텍스트 가져오기
                    text_1 = element_1.text
                    print(f"Element {i-1} (User Link): {text_1}")

                except Exception as e:
                    print(f"Element {i} not found: {e}")
                # CSV에 데이터 쓰기
                writer.writerow({'name':  text_1})
               
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {e}")

input("브라우저를 닫으려면 Enter 키를 누르세요.")

