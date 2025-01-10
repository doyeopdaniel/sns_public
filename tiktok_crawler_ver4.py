// ... 기존 import 및 초기 설정 코드 동일 ...

for hashtag_idx, hashtag in enumerate(hashtags):
    print(f"현재 처리 중인 해시태그: {hashtag}")
    collected_names = []  # 각 해시태그별 수집된 이름을 저장할 리스트
    
    try:
        // ... 검색 버튼 클릭 및 검색어 입력 코드 동일 ...

        # 데이터 수집 및 저장
        with open('tiktok_data_meme.csv', mode='a', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['hashtag', 'name']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            if csv_file.tell() == 0:
                writer.writeheader()

            not_found_count = 0
            collected_count = 0
            current_index = 0  # 현재 시도하는 인덱스

            while collected_count < 50:  # 50개 수집할 때까지
                if not_found_count >= 20:  # 20회 이상 실패하면 다음 인덱스 범위로 이동
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
                    collected_names.append(text)  # 수집된 이름 리스트에 추가
                    collected_count += 1
                    current_index += 1
                except:
                    print(f"요소 {current_index}를 찾을 수 없음, 다음 요소로 넘어갑니다.")
                    not_found_count += 1
                    current_index += 1

        # 수집된 name 개수 출력
        print(f"해시태그 '{hashtag}'에서 수집된 총 name 개수: {len(collected_names)}")

        # 수집된 name이 5개 미만인 경우 null_hashtag.csv에 기록
        if len(collected_names) < 5:
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
    with open('C:\\Users\\user\\Desktop\\sns_crawler\\null_hashtag.csv', mode='w', newline='', encoding='utf-8') as null_file:
        fieldnames = ['source_file', 'hashtag', 'index']
        writer = csv.DictWriter(null_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(null_hashtags)
    print("null_hashtag.csv 파일이 생성되었습니다.")

print("크롤링이 완료되었습니다.")
driver.quit()