import pandas as pd

try:
    # 두 파일 읽기
    source_df = pd.read_csv('C:/Users/user/Desktop/sns_crawler/hashtag_meme.csv')
    result_df = pd.read_csv('C:/Users/user/Desktop/sns_crawler/tiktok_data_meme.csv')
    
    print("\n해시태그별 크롤링 결과 분석:")
    
    # 각 해시태그별 수집된 데이터 수와 중복 확인
    for idx, row in source_df.iterrows():
        hashtag = row['hashtag']
        # 해당 해시태그의 데이터만 필터링
        hashtag_data = result_df[result_df['hashtag'] == hashtag]
        total_count = len(hashtag_data)
        unique_count = len(hashtag_data['name'].unique())
        
        # 데이터가 없거나 (0개), 너무 적거나 (5개 미만), 중복이 많은 경우 (고유값이 전체의 50% 미만)
        if total_count == 0:
            print(f"인덱스 {idx}: {hashtag} - 데이터 없음")
        elif total_count < 5:
            print(f"인덱스 {idx}: {hashtag} - 데이터 부족 (총 {total_count}개)")
        elif unique_count < total_count * 0.5:  # 중복이 50% 이상인 경우
            print(f"인덱스 {idx}: {hashtag} - 중복 많음 (전체: {total_count}개, 고유: {unique_count}개)")
    
    print("\n요약:")
    no_data = sum(1 for idx, row in source_df.iterrows() 
                 if len(result_df[result_df['hashtag'] == row['hashtag']]) == 0)
    print(f"데이터가 없는 해시태그: {no_data}개")
    
    few_data = sum(1 for idx, row in source_df.iterrows() 
                  if 0 < len(result_df[result_df['hashtag'] == row['hashtag']]) < 5)
    print(f"데이터가 5개 미만인 해시태그: {few_data}개")

except FileNotFoundError:
    print("CSV 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"오류 발생: {e}")