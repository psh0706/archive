#!/usr/bin/env python
# coding: utf-8

# 필요 라이브러리
from googletrans import Translator
import pandas as pd
import os
import re

# 메인 함수
if __name__ == "__main__":
    default_path = r"C:\temp_workspace\hotel"  # 경로
    translator = Translator()                  # 번역기 시작

    os.chdir(default_path)                     # C:\Workspace\tour_gosu\hotel
    country_list = os.listdir()                # 국가 리스트 추출

    # 순회
    for country in country_list:
        os.chdir(country)                      # C:\Workspace\tour_gosu\tour\country
        city_list = os.listdir()               # 도시 리스트 추출

        for city in city_list:
            os.chdir(city + "\\review")        # C:\Workspace\tour_gosu\tour\country\city\review

            # 저장할 폴더 생성
            try:
                os.makedirs("translated_review")
            except:
                pass

            review_list = os.listdir()   # 리뷰 리스트 추출

            # 필요 없는 리뷰 리스트 제거
            try:
                review_list.remove("translated_review")
            except:
                pass
            try:
                review_list.remove("debug.log")
            except:
                pass

            # 따로 플래그가 없어서 파일 이름의 인덱스를 정규 표현식으로 추출해,
            # hotel_urls에서 레이블명을 매칭하여 가져온다.
            # 번역 도중 오류가 생겨 다시 돌릴 때, 위와 비슷한 과정을 통해
            # 이미 번역된 리뷰를 제외하고 번역되지 않은 파일 부터 다시 번역을 시작한다. (flag 역할)

            file_list = review_list                                           # 번역되지 않은 파일 리스트 추출
            regex = re.compile(r'(hr_)(\d*)(.csv)')
            hotel_urls = pd.read_csv(r'..\hotel_urls.csv', encoding="UTF-8")  # title을 읽어오기 위해 hotel_urls를 불러온다.

            for file in file_list:
                hotel_index = int(regex.search(file).group(2))
                hotel_label = hotel_urls.iloc[hotel_index]['title']

                hotel_label = re.sub('[\/:*?"<>|]', '', str(hotel_label))     # 특수문자 제거 (파일 이름에 특수문자 포함 불가능)

                if os.path.isfile(
                        r'.\translated_review\hotel_review_{}.csv'.format(hotel_label)):  # (Flag 역할)음식점이름.csv가 존재하는 경우
                    print(hotel_index, '. ', hotel_label, ' 을 이미 번역했으므로 Pass 합니다.')
                    review_list.remove(file)

            # 번역 시작.

            for review in review_list:
                src_review = pd.read_csv(review, sep=",", encoding="UTF-8", error_bad_lines=False)
                tar_review = pd.DataFrame(columns=['index', 'title', 'rating', 'content', 'lang'])

                # index-label 매칭
                hotel_urls = pd.read_csv(r'..\hotel_urls.csv', encoding="UTF-8")  # title을 읽어오기 위해 hotel_urls를 불러온다.
                regex = re.compile(r'(hr_)(\d*)(.csv)')  # 정규 표현식
                hotel_index = int(regex.search(review).group(2))  # 파일 이름에서 index 추출.
                temp_hotel_urls = hotel_urls.loc[hotel_index]
                hotel_label = temp_hotel_urls['title']  # index를 통해 title 추출.

                hotel_label = re.sub('[\/:*?"<>|]', '', str(hotel_label))  # 특수문자 제거
                for index in range(0, len(src_review)):
                    temp = src_review.loc[index]  # 리뷰 하나 불러오기

                    if temp['lang'] == 'en':                  # lang=en 리뷰는 번역 없이 그대로 가져온다.
                        tar_review.loc[index] = [temp['index'], temp['title'], temp['rating'], temp['content'],
                                                 temp['lang']]
                    elif len(temp['content']) > 500:          # 리뷰가 너무 길면 번역 불가.
                        pass
                    elif len(temp['content']) < 2:            # 리뷰가 너무 짧으면 번역 불가.
                        pass
                    else:                                     # lang != en 이면 번역.
                        try:
                            result = translator.translate(temp['content'], dest="en")
                            tar_review.loc[index] = [temp['index'], temp['title'], temp['rating'], result.text,
                                                    temp['lang']]
                        except: pass

                    tar_review.to_csv(r'.\translated_review\hotel_review_{}.csv'.format(hotel_label), encoding="UTF=8",
                                      index=False)
                    print(review, '의 ', index, '번 째 번역 완료 !!')
            
            os.chdir("..")
            os.chdir("..")

