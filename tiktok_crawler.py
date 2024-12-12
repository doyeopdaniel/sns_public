from playwright.sync_api import sync_playwright
import pandas as pd
import random
import time
from typing import List, Dict
import logging
import os
import keyboard  # keyboard 라이브러리 추가 필요 (pip install keyboard)

class TikTokCrawler:
    def __init__(self, hashtag_file: str):
        """틱톡 크롤러 초기화
        
        Args:
            hashtag_file (str): 해시태그 CSV 파일 경로
        """
        self.hashtag_df = pd.read_csv(hashtag_file)
        self.results = []
        self.setup_logging()
        self.pause_crawling = False  # 일시정지 상태를 관리할 플래그 추가
        self.setup_keyboard_listener()  # 키보드 리스너 추가

    def setup_keyboard_listener(self):
        """키보드 일시정지/재개 리스너 설정"""
        keyboard.add_hotkey('`', self.toggle_pause)  # 백틱(`) 키로 일시정지/재개 토글
        print("키보드 리스너 설정: 백틱(`) 키로 크롤링 일시정지/재개 가능")

    def toggle_pause(self):
        """크롤링 일시정지/재개 토글"""
        self.pause_crawling = not self.pause_crawling
        
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('tiktok_crawler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 5.0):
        """랜덤 딜레이 추가"""
        time.sleep(random.uniform(min_seconds, max_seconds))
        
    def setup_keyboard_listener(self):
        """키보드 일시정지/재개 리스너 설정"""
        keyboard.add_hotkey('`', self.toggle_pause)  # 백틱(`) 키로 일시정지/재개 토글
        self.logger.info("키보드 리스너 설정: 백틱(`) 키로 크롤링 일시정지/재개 가능")
        
    def toggle_pause(self):
        """크롤링 일시정지/재개 토글"""
        self.pause_crawling = not self.pause_crawling
        status = "일시정지" if self.pause_crawling else "재개"
        print(f"크롤링 {status}")
        self.logger.info(f"크롤링 {status}")
        
    def crawl_hashtag(self, hashtag: str) -> List[Dict]:
        """틱톡 해시태그 크롤링"""
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,  # 디버깅을 위해 False로 유지
                slow_mo=500,  # 작업 사이 지연 추가
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-infobars',
                    '--window-size=1920,1080',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            
            page = context.new_page()
            
            try:
                # TikTok 메인 페이지로 이동
                page.goto("https://www.tiktok.com/", timeout=30000)
                
                # 페이지 완전 로딩 대기
                page.wait_for_load_state('networkidle', timeout=30000)
                
                # 검색 입력란에 해시태그 입력
                search_input_selector = '#app > div.css-1yczxwx-DivBodyContainer.e1irlpdw0 > div.css-flkb7b-DivSideNavPlaceholderContainer.e1u58fka0 > div > div.css-6dsq89-DivDrawerContainer.e1lvfea00.drawer-enter-done > div.css-kdngec-DivSearchContainer.e1lvfea05 > div.css-1asq5wp-DivSearchFormContainer.e1hi1cmj0 > form > input'
                search_input = page.wait_for_selector(search_input_selector, timeout=10000)
                search_input.fill(f"#{hashtag}")
                page.keyboard.press('Enter')
                
                # 검색 결과 대기
                page.wait_for_selector('.video-feed-item', timeout=10000)
                
                # 결과 추출
                results = []
                user_selectors = [
                    '#search_top-item-user-link-0 > div > p',
                    '[data-e2e="search-user-username"]'
                ]
                
                # 사용자 정보 추출
                for i in range(20):  # 최대 20개 사용자 추출
                    try:
                        for selector in user_selectors:
                            user_elements = page.query_selector_all(selector)
                            
                            if user_elements:
                                for element in user_elements:
                                    user_name = element.inner_text().strip()
                                    user_link = element.get_attribute('href') or f"https://www.tiktok.com/@{user_name}"
                                    
                                    result = {
                                        'hashtag': hashtag,
                                        'username': user_name,
                                        'profile_link': user_link
                                    }
                                    results.append(result)
                                break
                    except Exception as e:
                        print(f"사용자 추출 중 오류: {e}")
                
                # 브라우저 닫힘 방지
                input("크롤링 완료. 엔터를 누르면 브라우저가 닫힙니다.")
                
                return results
            
            except Exception as e:
                print(f"크롤링 중 오류 발생: {e}")
                return []
            
            finally:
                browser.close()
        
    def run(self):
        """크롤링 실행"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            # TikTok 메인 페이지로 이동
            page.goto("https://www.tiktok.com")
            time.sleep(3)  # 페이지 로딩 대기

            for index, row in self.hashtag_df.iterrows():
                hashtag = row['hashtags']  # 'hashtags' 열에서 키워드 가져오기
                print(f"크롤링 시작: #{hashtag}")

                # 첫 번째 방법: 검색 버튼 클릭 후 입력란에 문자열 입력
                try:
                    # 검색 버튼이 보일 때까지 대기
                    page.wait_for_selector("#app > div.css-1yczxwx-DivBodyContainer.e1irlpdw0 > div.css-flkb7b-DivSideNavPlaceholderContainer.e1u58fka0 > div > div.css-m8ow1x-DivFixedContentContainer.e1u58fka2 > div.css-1icvwlp-DivSearchWrapper.e1u58fka4 > button", timeout=10000)
                    page.click("#app > div.css-1yczxwx-DivBodyContainer.e1irlpdw0 > div.css-flkb7b-DivSideNavPlaceholderContainer.e1u58fka0 > div > div.css-m8ow1x-DivFixedContentContainer.e1u58fka2 > div.css-1icvwlp-DivSearchWrapper.e1u58fka4 > button")
                    
                    time.sleep(1)  # 클릭 후 대기

                    input_element = page.wait_for_selector("#app > div.css-1yczxwx-DivBodyContainer.e1irlpdw0 > div.css-flkb7b-DivSideNavPlaceholderContainer.e1u58fka0 > div > div.css-6dsq89-DivDrawerContainer.e1lvfea00.drawer-enter-done > div.css-kdngec-DivSearchContainer.e1lvfea05 > div.css-1asq5wp-DivSearchFormContainer.e1hi1cmj0 > form > input", timeout=10000)
                    input_element.fill(f"#{hashtag}")  # 해시태그 입력
                    input_element.press("Enter")  # 엔터 키 누르기
                    print(f"해시태그 #{hashtag} 입력 완료.")

                    time.sleep(3)  # 검색 결과 로딩 대기

                    # 사용자 링크 크롤링
                    user_links = []
                    for i in range(50):  # 0부터 49까지 크롤링
                        user_selector = f"#search_top-item-user-link-{i} > div > p"
                        try:
                            user_element = page.wait_for_selector(user_selector, timeout=10000)
                            user_links.append(user_element.inner_text())
                        except Exception:
                            break  # 더 이상 요소가 없으면 종료

                    print(f"사용자 링크: {user_links}")

                    # 비디오 정보 크롤링
                    video_info = []
                    for i in range(1, 51):  # 1부터 50까지 크롤링
                        video_selector = f"#tabs-0-panel-search_top > div > div > div:nth-child({i}) > div.css-hbrxqe-DivVideoSearchCardDesc.etrd4pu0 > div > div.css-1kw4mmh-DivPlayLine.etrd4pu3 > div > strong"
                        try:
                            video_element = page.wait_for_selector(video_selector, timeout=10000)
                            video_info.append(video_element.inner_text())
                        except Exception:
                            break  # 더 이상 요소가 없으면 종료

                    print(f"비디오 정보: {video_info}")

                    # 스크롤을 천천히 하면서 추가 크롤링
                    for _ in range(5):  # 5번 스크롤
                        page.evaluate("window.scrollBy(0, window.innerHeight)")  # 아래로 스크롤
                        time.sleep(1)  # 스크롤 후 대기

                except Exception as e:
                    print(f"크롤링 중 오류 발생: {e}")

                # 두 번째 방법: 입력란에 문자열 입력 후 검색 버튼 클릭
                try:
                    # 검색 버튼이 보일 때까지 대기 (타임아웃 없음)
                    page.wait_for_selector("#app > div.css-1yczxwx-DivBodyContainer.e1irlpdw0 > div.css-flkb7b-DivSideNavPlaceholderContainer.e1u58fka0 > div > div.css-m8ow1x-DivFixedContentContainer.e1u58fka2 > div.css-1icvwlp-DivSearchWrapper.e1u58fka4 > button", timeout=None)
                    page.click("#app > div.css-1yczxwx-DivBodyContainer.e1irlpdw0 > div.css-flkb7b-DivSideNavPlaceholderContainer.e1u58fka0 > div > div.css-m8ow1x-DivFixedContentContainer.e1u58fka2 > div.css-1icvwlp-DivSearchWrapper.e1u58fka4 > button")
                    
                    time.sleep(1)  # 클릭 후 대기

                    input_element = page.wait_for_selector("#app > div.css-1yczxwx-DivBodyContainer.e1irlpdw0 > div.css-flkb7b-DivSideNavPlaceholderContainer.e1u58fka0 > div > div.css-6dsq89-DivDrawerContainer.e1lvfea00.drawer-enter-done > div.css-kdngec-DivSearchContainer.e1lvfea05 > div.css-1asq5wp-DivSearchFormContainer.e1hi1cmj0 > form > input", timeout=None)
                    input_element.fill(f"#{hashtag}")  # 해시태그 입력
                    input_element.press("Enter")  # 엔터 키 누르기
                    print(f"해시태그 #{hashtag} 입력 완료.")

                    time.sleep(3)  # 검색 결과 로딩 대기

                    # 사용자 링크 크롤링
                    user_links = []
                    for i in range(50):  # 0부터 49까지 크롤링
                        user_selector = f"#search_top-item-user-link-{i} > div > p"
                        try:
                            user_element = page.wait_for_selector(user_selector, timeout=None)
                            user_links.append(user_element.inner_text())
                        except Exception:
                            break  # 더 이상 요소가 없으면 종료

                    print(f"사용자 링크: {user_links}")

                    # 비디오 정보 크롤링
                    video_info = []
                    for i in range(1, 51):  # 1부터 50까지 크롤링
                        video_selector = f"#tabs-0-panel-search_top > div > div > div:nth-child({i}) > div.css-hbrxqe-DivVideoSearchCardDesc.etrd4pu0 > div > div.css-1kw4mmh-DivPlayLine.etrd4pu3 > div > strong"
                        try:
                            video_element = page.wait_for_selector(video_selector, timeout=10000)
                            video_info.append(video_element.inner_text())
                        except Exception:
                            break  # 더 이상 요소가 없으면 종료

                    print(f"비디오 정보: {video_info}")

                    # 스크롤을 천천히 하면서 추가 크롤링
                    for _ in range(5):  # 5번 스크롤
                        page.evaluate("window.scrollBy(0, window.innerHeight)")  # 아래로 스크롤
                        time.sleep(1)  # 스크롤 후 대기

                except Exception as e:
                    print(f"크롤링 중 오류 발생: {e}")

            # 브라우저는 닫지 않음
            print("브라우저를 닫지 않고 계속 진행합니다.")

    def save_results(self):
        """크롤링 결과 저장 - 기존 파일에 추가"""
        if self.results:
            df = pd.DataFrame(self.results)
            try:
                # 기존 파일이 있으면 읽어오기
                existing_df = pd.read_csv('tiktok_results.csv')
                # 새로운 결과를 기존 데이터에 추가
                updated_df = pd.concat([existing_df, df], ignore_index=True)
            except FileNotFoundError:
                # 파일이 없으면 새로 생성
                updated_df = df
            
            try:
                # CSV 파일로 저장
                updated_df.to_csv('tiktok_results.csv', index=False)
                self.logger.info(f"Results appended to tiktok_results.csv - {len(df)} new rows")
            except Exception as e:
                self.logger.error(f"결과 저장 중 오류 발생: {e}")

    def safe_extract_text(self, element, selector):
        """안전하게 텍스트 추출"""
        try:
            count_element = element.query_selector(selector)
            return count_element.inner_text() if count_element else 'N/A'
        except Exception as e:
            self.logger.warning(f"텍스트 추출 중 오류: {e}")
            return 'N/A'

if __name__ == "__main__":
    # 현재 스크립트의 디렉토리를 기준으로 파일 경로 설정
    hashtag_file = os.path.join(os.path.dirname(__file__), "hashtag.csv")
    crawler = TikTokCrawler(hashtag_file)
    crawler.run()
