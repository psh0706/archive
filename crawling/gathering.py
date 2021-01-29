import os
import re
import pandas as pd
import csv
import time
import gc


# 여행고수 팀 - 박수현 작성
# 2019.11.03 ver. 리뷰 취합코드 
# info 까지 전부 돌린 국가>지역 파일 필요.
# ** 기능 **
# 1) 중복페이지 중복제거
# 2) 평점 3.5 이하 리뷰 제거
# 3) 지역 컬럼 추가


##전역변수 - stateName/dirname 은 돌릴 때 마다 변경해주세요.
## stateName = 국가 이름
## dirname = 국가 폴더 경로
dirname = str("C:\\tripAdvisor2\\Taiwan")
local_file_list = os.listdir(dirname)
stateName = "Taiwan"

temp_df = pd.DataFrame()
save_df = pd.DataFrame()

#취합 시작
def startGathering():
    temp_df = pd.read_csv('play_review_list.csv')
    temp_df = joinDataFrame(temp_df)
    temp_df = deleteUnder35(temp_df)
    temp_df = addLocalname(temp_df)
    #url을 kr 에서 uk 로 변경
    temp_df = changeUrl(temp_df)
    #저장
    saveToCSV(temp_df)

    return


def changeUrl(temp_df):
    urls=list()
    change_urls=list()
    chUrl = str()
    urls = temp_df['url']

    regex = re.compile('(https://www.tripadvisor.co.kr)(.*.)')


    for url in urls:
        cut_url = regex.search(url)
        chUrl = "https://www.tripadvisor.co.uk/"+cut_url.group(2)
        change_urls.append(chUrl)

    temp_df['url'] = change_urls    

    return temp_df

#지역컬럼 추가
def addLocalname(temp_df):
    locName_path = os.getcwd()
    splitxt = os.path.split(locName_path)
    temp_df["local"] = splitxt[1]
    return temp_df



#평점 필터링 위한 조인과정
def joinDataFrame(temp_df):
    temp_df2 = pd.read_csv('play_scraped_list.csv')
    temp_df = pd.merge(temp_df,temp_df2, left_on='index', right_on='000_index')
    temp_df.drop(['000_index','001_상호명','003_영업시간','004_추천방문시간','005_카테고리','006_전화번호','007_주소','008_위도','009_경도'],1,inplace=True)
    temp_df.rename(columns={'002_평점': 'rating'}, inplace=True)

    return temp_df


#평점 필터링(제거)
def deleteUnder35(temp_df):
    temp_df = temp_df[temp_df['rating'] >= 3.5]
    return temp_df


#중복 필터링(제거)
def deleteOverlap(save_df):
    save_df.drop_duplicates(["url"], keep='last')

    return save_df



#CSV파일로 저장
def saveToCSV(temp_df):
    global save_df
    try: 
        save_df = pd.read_csv("{}\\play_review_list_{}.csv".format(dirname,stateName), sep=",",encoding = 'utf-8')
    except FileNotFoundError: # 파일이 없을 경우(=가장 처음) 파일생성.
        temp_df.to_csv("{}\\play_review_list_{}.csv".format(dirname,stateName), index=False,encoding = 'utf-8')

        temp_df.drop(['index'],1,inplace=True)
        temp_df['index'] = temp_df.index

        print("play_review_list_{}.csv 파일이 존재하지 않으므로 새로 생성하여 저장합니다.".format(stateName))
        del temp_df
        del save_df
        temp_df = pd.DataFrame()
        save_df = pd.DataFrame()
    else: # 파일이 있을 경우
        save_df.drop(['index'],1,inplace=True)
        save_df = pd.concat([save_df,temp_df],ignore_index=True,sort=True)
        save_df = deleteOverlap(save_df)
        save_df['index'] = save_df.index
        save_df.to_csv("{}\\play_review_list_{}.csv".format(dirname,stateName), index=False ,encoding = 'utf-8')
        print("play_review_list_{}.csv의 끝에 저장합니다.".format(stateName))
        del temp_df
        del save_df
        temp_df = pd.DataFrame()
        save_df = pd.DataFrame()

    return






if __name__ == "__main__":
    print(local_file_list)

    for local_file_name in local_file_list:
        full_filename = os.path.join(dirname, local_file_name)
        print(full_filename)
        os.chdir(full_filename)
        startGathering()

