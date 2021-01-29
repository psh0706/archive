from flask import Flask
from flask import send_file
from flask import jsonify
from flask_restful import Resource, Api
from flask_restful import reqparse
from flask import request
from flask_cors import CORS, cross_origin, logging
import pymysql
import pickle
import os
import pandas as pd
import numpy as np
import json
import time
import scipy.stats as ss
import re
import pymysql
 
#MySQL Connection 연결
conn = pymysql.connect(host='10.0.1.4', port = 3306 ,user='test', password='0000',
                       db='tourai', charset='utf8')

# # Connection 으로부터 Cursor 생성
curs = conn.cursor()
 
# SQL문 실행
# sql = "select * from tour_info"
# curs.execute(sql)

# 데이타 Fetch
# rows = curs.fetchall()
# print(rows)     # 전체 rows


app = Flask(__name__)
CORS(app, resources={r'*': {'origins': '*'}})
logging.getLogger('flask_cors').level = logging.DEBUG


default_path = os.getcwd()

# kind1 = positive,negative,bigram
# kind2 = restaurant,tour,hotel

### CORS section
@app.after_request
def after_request_func(response):
    origin = request.headers.get('Origin')
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Headers', 'x-csrf-token')
        response.headers.add('Access-Control-Allow-Methods',
                            'GET, POST, OPTIONS, PUT, PATCH, DELETE')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)

    return response
### end CORS section
### cf) https://developer.mozilla.org/ko/docs/Web/HTTP/CORS

@app.route('/sql', methods=['POST'])
def sql():
    jsonData = json.loads(request.get_data(), encoding='utf-8')

    #JSON 데이터를 플랫 테이블로 정규화.
    food = pd.json_normalize(jsonData['food'])
    tour = pd.json_normalize(jsonData['tour'])
    hotel = pd.json_normalize(jsonData['hotel'])
    
    #값 없는 레코드 날리기
    food.dropna(subset=['recomm'], how='all',inplace=True)
    tour.dropna(subset=['recomm'], how='all',inplace=True)
    hotel.dropna(subset=['recomm'], how='all',inplace=True)

    #새로 인덱싱
    food.reset_index(drop = True, inplace = True)
    tour.reset_index(drop = True, inplace = True)
    hotel.reset_index(drop = True, inplace = True)

    food['same'] = ''
    tour['same'] = ''
    hotel['same'] = ''

    
    if jsonData['with'] == "혼자":
        
        food_regex = r'(.*.가격이싼)?(.*.가성비or가치있는)?(.*.현지스러운)?(.*.분위기좋은)?(.*.작고아담한)?'
        food = food.apply(lambda x: recomm_filter(food_regex,x),axis=1)

        tour_regex = r'(.*.힐링하기좋은)?(.*.볼거리많은)?(.*.젊은사람추천)?(.*.재밌는거리)?'
        tour = tour.apply(lambda x: recomm_filter(tour_regex,x),axis=1)

        hotel_regex = r'(.*.위치가좋은)?(.*.청결한)?(.*.가성비좋은)?(.*.조식좋은)?(.*.도심위치)?'
        hotel = hotel.apply(lambda x: recomm_filter(hotel_regex,x),axis=1)

    elif jsonData['with'] == "가족":
        
        food_regex = r'(.*.가성비or가치있는)?(.*.서비스좋은)?(.*.분위기좋은)?(.*.고급스러운/비싼)?(.*.청결한,깨끗한)?(.*.가족식당)?(.*.여럿이먹기좋은)?(.*.편안한식당)?(.*.위치좋은)?'
        food = food.apply(lambda x: recomm_filter(food_regex,x),axis=1)
        
        tour_regex = r'(.*.쇼핑맛집거리)?(.*.바다해변)?(.*.도심여행지)?(.*.짧은시간)?(.*.가족여행좋은)?(.*.볼거리많은)?(.*.놀이공원)?'
        tour = tour.apply(lambda x: recomm_filter(tour_regex,x),axis=1)

        hotel_regex = r'(.*.서비스가좋은)?(.*.위치가좋은)?(.*.청결한)?(.*.수영장좋은)?(.*.조식좋은)?(.*.룸이큰)?(.*.욕실이큰)?'
        hotel = hotel.apply(lambda x: recomm_filter(hotel_regex,x),axis=1)
        
    elif jsonData['with'] == "친구":

        food_regex = r'(.*.가격이싼)?(.*.가성비or가치있는)?(.*.현지스러운)?(.*.분위기좋은)?(.*.고급스러운/비싼)?(.*.여럿이먹기좋은)?(.*.위치좋은)?'
        food = food.apply(lambda x: recomm_filter(food_regex,x),axis=1)

        tour_regex = r'(.*.쇼핑맛집거리)?(.*.걷기좋은)?(.*.뷰가멋진)?(.*.도심여행지)?(.*.멋진사진촬영지)?(.*.볼거리많은)?(.*.젊은사람추천)?(.*.재밌는거리)?'
        tour = tour.apply(lambda x: recomm_filter(tour_regex,x),axis=1)

        hotel_regex = r'(.*.위치가좋은)?(.*.청결한)?(.*.가성비좋은)?(.*.조식좋은)?(.*.뷰가좋은)?'
        hotel = hotel.apply(lambda x: recomm_filter(hotel_regex,x),axis=1)

    else:

        food_regex = r'(.*.가성비or가치있는)?(.*.서비스좋은)?(.*.분위기좋은)?(.*.고급스러운/비싼)?(.*.위치좋은)?'
        food = food.apply(lambda x: recomm_filter(food_regex,x),axis=1)

        tour_regex = r'(.*.쇼핑맛집거리)?(.*.걷기좋은)?(.*.뷰가멋진)?(.*.도심여행지)?(.*.멋진사진촬영지)?(.*.볼거리많은)?(.*.젊은사람추천)?(.*.재밌는거리)?'
        tour = tour.apply(lambda x: recomm_filter(tour_regex,x),axis=1)

        hotel_regex = r'(.*.위치가좋은)?(.*.청결한)?(.*.조식좋은)?(.*.뷰가좋은)?(.*.욕실이큰)?'
        hotel = hotel.apply(lambda x: recomm_filter(hotel_regex,x),axis=1)
    
    food = food[food['same'] > 2]
    hotel = hotel[hotel['same'] > 2]
    tour = tour[tour['same'] > 2]

    food.sort_values(by=['same'],inplace=True,ascending=False)
    hotel.sort_values(by=['same'],inplace=True,ascending=False)
    tour.sort_values(by=['same'],inplace=True,ascending=False)

    merge = {
        "food" : food.to_dict(orient = "records"),
        "tour" : tour.to_dict(orient = "records"),
        "hotel" : hotel.to_dict(orient = "records")
    }
    return merge

@app.route('/sqll', methods=['POST'])
def sqll():
    start = time.time()  # 시작 시간 저장
    jsonData = json.loads(request.get_data(), encoding='utf-8')
    data = pd.json_normalize(jsonData['title_list'])
    data['same'] = 0
    print(data)
    div1 = data[(data['keyword'] == '혼자') | (data['keyword'] == '애인') | (data['keyword'] == '가족') | (data['keyword'] == '친구')]
    div2 = data[(data['keyword'] != '혼자') & (data['keyword'] != '애인') & (data['keyword'] != '가족') & (data['keyword'] != '친구')]

    div1.dropna(subset=['recomm'], how='all',inplace=True)

    div1.reset_index(drop = True, inplace = True)
    div2.reset_index(drop = True, inplace = True)

    if div1['keyword'][0] == "혼자":

        food_regex = r'(.*.가격이싼)?(.*.가성비or가치있는)?(.*.현지스러운)?(.*.분위기좋은)?(.*.작고아담한)?'
        tour_regex = r'(.*.힐링하기좋은)?(.*.볼거리많은)?(.*.젊은사람추천)?(.*.재밌는거리)?'
        hotel_regex = r'(.*.위치가좋은)?(.*.청결한)?(.*.가성비좋은)?(.*.조식좋은)?(.*.도심위치)?'

        div1[div1['type'] == 'food'] = div1[div1['type'] == 'food'].apply(lambda x: recomm_filter(food_regex,x),axis=1) 
        div1[div1['type'] == 'tour'] = div1[div1['type'] == 'tour'].apply(lambda x: recomm_filter(tour_regex,x),axis=1)
        div1[div1['type'] == 'hotel'] = div1[div1['type'] == 'hotel'].apply(lambda x: recomm_filter(hotel_regex,x),axis=1)

    elif div1['keyword'][0] == "가족":

        food_regex = r'(.*.가성비or가치있는)?(.*.서비스좋은)?(.*.분위기좋은)?(.*.고급스러운/비싼)?(.*.청결한,깨끗한)?(.*.가족식당)?(.*.여럿이먹기좋은)?(.*.편안한식당)?(.*.위치좋은)?'
        tour_regex = r'(.*.쇼핑맛집거리)?(.*.바다해변)?(.*.도심여행지)?(.*.짧은시간)?(.*.가족여행좋은)?(.*.볼거리많은)?(.*.놀이공원)?'
        hotel_regex = r'(.*.서비스가좋은)?(.*.위치가좋은)?(.*.청결한)?(.*.수영장좋은)?(.*.조식좋은)?(.*.룸이큰)?(.*.욕실이큰)?'

        div1[div1['type'] == 'food'] = div1[div1['type'] == 'food'].apply(lambda x: recomm_filter(food_regex,x),axis=1) 
        div1[div1['type'] == 'tour'] = div1[div1['type'] == 'tour'].apply(lambda x: recomm_filter(tour_regex,x),axis=1)
        div1[div1['type'] == 'hotel'] = div1[div1['type'] == 'hotel'].apply(lambda x: recomm_filter(hotel_regex,x),axis=1)

    elif div1['keyword'][0] == "친구":

        food_regex = r'(.*.가격이싼)?(.*.가성비or가치있는)?(.*.현지스러운)?(.*.분위기좋은)?(.*.고급스러운/비싼)?(.*.여럿이먹기좋은)?(.*.위치좋은)?'
        tour_regex = r'(.*.쇼핑맛집거리)?(.*.걷기좋은)?(.*.뷰가멋진)?(.*.도심여행지)?(.*.멋진사진촬영지)?(.*.볼거리많은)?(.*.젊은사람추천)?(.*.재밌는거리)?'
        hotel_regex = r'(.*.위치가좋은)?(.*.청결한)?(.*.가성비좋은)?(.*.조식좋은)?(.*.뷰가좋은)?'

        div1[div1['type'] == 'food'] = div1[div1['type'] == 'food'].apply(lambda x: recomm_filter(food_regex,x),axis=1) 
        div1[div1['type'] == 'tour'] = div1[div1['type'] == 'tour'].apply(lambda x: recomm_filter(tour_regex,x),axis=1)
        div1[div1['type'] == 'hotel'] = div1[div1['type'] == 'hotel'].apply(lambda x: recomm_filter(hotel_regex,x),axis=1)

    else:

        food_regex = r'(.*.가성비or가치있는)?(.*.서비스좋은)?(.*.분위기좋은)?(.*.고급스러운/비싼)?(.*.위치좋은)?'
        tour_regex = r'(.*.쇼핑맛집거리)?(.*.걷기좋은)?(.*.뷰가멋진)?(.*.도심여행지)?(.*.멋진사진촬영지)?(.*.볼거리많은)?(.*.젊은사람추천)?(.*.재밌는거리)?'
        hotel_regex = r'(.*.위치가좋은)?(.*.청결한)?(.*.조식좋은)?(.*.뷰가좋은)?(.*.욕실이큰)?'

        div1[div1['type'] == 'food'] = div1[div1['type'] == 'food'].apply(lambda x: recomm_filter(food_regex,x),axis=1) 
        div1[div1['type'] == 'tour'] = div1[div1['type'] == 'tour'].apply(lambda x: recomm_filter(tour_regex,x),axis=1)
        div1[div1['type'] == 'hotel'] = div1[div1['type'] == 'hotel'].apply(lambda x: recomm_filter(hotel_regex,x),axis=1)

    div1 = div1[div1['same'] > 2]

    temp = pd.concat([div1,div2])
    count = temp.groupby(['title'])['title'].count()
    count.sort_values(inplace=True,ascending=False)
    count = pd.DataFrame(count)
    count.columns = ['freq']
    count['title'] = count.index
    count.reset_index(drop=True,inplace=True)

    temp = pd.merge(temp,count,left_on='title',right_on='title',how='inner')
    temp.sort_values(by=['freq','same'],ascending=False,inplace=True)
    temp.reset_index(drop=True,inplace=True)
    print(temp.columns)
    temp.drop_duplicates(['title'],inplace=True)

    food = temp[temp['type'] == 'food']
    tour = temp[temp['type'] == 'tour']
    hotel = temp[temp['type'] == 'hotel']

    food.reset_index(drop=True,inplace=True)
    tour.reset_index(drop=True,inplace=True)
    hotel.reset_index(drop=True,inplace=True)

    food = food.loc[0:100]
    tour = tour.loc[0:100]
    hotel = hotel.loc[0:100]

    merge = {
            "food" : food.to_dict(orient = "records"),
            "tour" : tour.to_dict(orient = "records"),
            "hotel" : hotel.to_dict(orient = "records")
    }
    return merge

@app.route('/sql_follow', methods=['POST'])
def sql_follow():
    start = time.time()  # 시작 시간 저장
    jsonData = json.loads(request.get_data(), encoding='utf-8')
    data = pd.json_normalize(jsonData['title_list'])
    data['same'] = 0
    div1 = data[(data['keyword'] == '혼자') | (data['keyword'] == '애인') | (data['keyword'] == '가족') | (data['keyword'] == '친구')]
    div2 = data[(data['keyword'] != '혼자') & (data['keyword'] != '애인') & (data['keyword'] != '가족') & (data['keyword'] != '친구')]

    div1.dropna(subset=['recomm'], how='all',inplace=True)

    div1.reset_index(drop = True, inplace = True)
    div2.reset_index(drop = True, inplace = True)

    if div1['keyword'][0] == "혼자":

        food_regex = r'(.*.가격이싼)?(.*.가성비or가치있는)?(.*.현지스러운)?(.*.분위기좋은)?(.*.작고아담한)?'
        tour_regex = r'(.*.힐링하기좋은)?(.*.볼거리많은)?(.*.젊은사람추천)?(.*.재밌는거리)?'
        hotel_regex = r'(.*.위치가좋은)?(.*.청결한)?(.*.가성비좋은)?(.*.조식좋은)?(.*.도심위치)?'

        div1[div1['type'] == 'food'] = div1[div1['type'] == 'food'].apply(lambda x: recomm_filter(food_regex,x),axis=1) 
        div1[div1['type'] == 'tour'] = div1[div1['type'] == 'tour'].apply(lambda x: recomm_filter(tour_regex,x),axis=1)
        div1[div1['type'] == 'hotel'] = div1[div1['type'] == 'hotel'].apply(lambda x: recomm_filter(hotel_regex,x),axis=1)

    elif div1['keyword'][0] == "가족":

        food_regex = r'(.*.가성비or가치있는)?(.*.서비스좋은)?(.*.분위기좋은)?(.*.고급스러운/비싼)?(.*.청결한,깨끗한)?(.*.가족식당)?(.*.여럿이먹기좋은)?(.*.편안한식당)?(.*.위치좋은)?'
        tour_regex = r'(.*.쇼핑맛집거리)?(.*.바다해변)?(.*.도심여행지)?(.*.짧은시간)?(.*.가족여행좋은)?(.*.볼거리많은)?(.*.놀이공원)?'
        hotel_regex = r'(.*.서비스가좋은)?(.*.위치가좋은)?(.*.청결한)?(.*.수영장좋은)?(.*.조식좋은)?(.*.룸이큰)?(.*.욕실이큰)?'

        div1[div1['type'] == 'food'] = div1[div1['type'] == 'food'].apply(lambda x: recomm_filter(food_regex,x),axis=1) 
        div1[div1['type'] == 'tour'] = div1[div1['type'] == 'tour'].apply(lambda x: recomm_filter(tour_regex,x),axis=1)
        div1[div1['type'] == 'hotel'] = div1[div1['type'] == 'hotel'].apply(lambda x: recomm_filter(hotel_regex,x),axis=1)

    elif div1['keyword'][0] == "친구":

        food_regex = r'(.*.가격이싼)?(.*.가성비or가치있는)?(.*.현지스러운)?(.*.분위기좋은)?(.*.고급스러운/비싼)?(.*.여럿이먹기좋은)?(.*.위치좋은)?'
        tour_regex = r'(.*.쇼핑맛집거리)?(.*.걷기좋은)?(.*.뷰가멋진)?(.*.도심여행지)?(.*.멋진사진촬영지)?(.*.볼거리많은)?(.*.젊은사람추천)?(.*.재밌는거리)?'
        hotel_regex = r'(.*.위치가좋은)?(.*.청결한)?(.*.가성비좋은)?(.*.조식좋은)?(.*.뷰가좋은)?'

        div1[div1['type'] == 'food'] = div1[div1['type'] == 'food'].apply(lambda x: recomm_filter(food_regex,x),axis=1) 
        div1[div1['type'] == 'tour'] = div1[div1['type'] == 'tour'].apply(lambda x: recomm_filter(tour_regex,x),axis=1)
        div1[div1['type'] == 'hotel'] = div1[div1['type'] == 'hotel'].apply(lambda x: recomm_filter(hotel_regex,x),axis=1)

    else:

        food_regex = r'(.*.가성비or가치있는)?(.*.서비스좋은)?(.*.분위기좋은)?(.*.고급스러운/비싼)?(.*.위치좋은)?'
        tour_regex = r'(.*.쇼핑맛집거리)?(.*.걷기좋은)?(.*.뷰가멋진)?(.*.도심여행지)?(.*.멋진사진촬영지)?(.*.볼거리많은)?(.*.젊은사람추천)?(.*.재밌는거리)?'
        hotel_regex = r'(.*.위치가좋은)?(.*.청결한)?(.*.조식좋은)?(.*.뷰가좋은)?(.*.욕실이큰)?'

        div1[div1['type'] == 'food'] = div1[div1['type'] == 'food'].apply(lambda x: recomm_filter(food_regex,x),axis=1) 
        div1[div1['type'] == 'tour'] = div1[div1['type'] == 'tour'].apply(lambda x: recomm_filter(tour_regex,x),axis=1)
        div1[div1['type'] == 'hotel'] = div1[div1['type'] == 'hotel'].apply(lambda x: recomm_filter(hotel_regex,x),axis=1)

    div1 = div1[div1['same'] > 2]

    temp = pd.concat([div1,div2])
    count = temp.groupby(['title'])['title'].count()
    count.sort_values(inplace=True,ascending=False)
    count = pd.DataFrame(count)
    count.columns = ['freq']
    count['title'] = count.index
    count.reset_index(drop=True,inplace=True)

    temp = pd.merge(temp,count,left_on='title',right_on='title',how='inner')
    temp.sort_values(by=['freq','same'],ascending=False,inplace=True)
    temp.reset_index(drop=True,inplace=True)
    print(temp.columns)
    temp.drop_duplicates(['title'],inplace=True)

    food = temp[temp['type'] == 'food']
    tour = temp[temp['type'] == 'tour']
    hotel = temp[temp['type'] == 'hotel']

    food.reset_index(drop=True,inplace=True)
    tour.reset_index(drop=True,inplace=True)
    hotel.reset_index(drop=True,inplace=True)

    food = food.loc[0:1]
    tour = tour.loc[0:1]
    hotel = hotel.loc[0:1]

    merge = {
            "food" : food.to_dict(orient = "records"),
            "tour" : tour.to_dict(orient = "records"),
            "hotel" : hotel.to_dict(orient = "records")
    }
    print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간
    return merge
    
    
def recomm_filter(regex,data):
    p = re.compile(regex)
    result = p.findall(data['recomm'])
    data['same'] = len(list(filter(None, result[0])))
    return data

@app.route('/tfidf_table', methods=['GET'])
def tfidf_table():
    jsonData = json.loads(request.get_data(), encoding='utf-8')
    print(jsonData)

    data = pd.DataFrame(columns = ['title','lat','lng','region','type'])

    if jsonData['type'] == 'food':
        try:
            jsonData['title'] = jsonData['title'].replace('\xa0','')
            with open('tf-idf/food/{}.txt'.format(jsonData['region']), 'rb') as f:
                X = pickle.load(f)
            Tops = pd.DataFrame(X[jsonData['title']]).sort_values(jsonData['title'], ascending = False)[1:3]
            Tops.columns = ['title']
            Tops['title'] = Tops.index
            Tops.reset_index(drop=True,inplace=True)

            for index in range(0,len(Tops)):
                sql = """select title,lat,lng,region from food_info where title LIKE '%"""+str(Tops['title'][index])+"""%' LIMIT 1;"""
                curs.execute(sql)
                rows = curs.fetchall()

                rows_to_df = pd.DataFrame(rows)
                rows_to_df.columns = ['title','lat','lng','region']
                rows_to_df['type'] = 'food'

                data=data.append(rows_to_df , ignore_index=True)

            data.drop_duplicates(inplace=True)
            food_list = data.to_dict(orient = "records")

            for i in range(0,len(food_list)):
                f_dict = food_list[i]
                f_dict['position'] = [0,0]
                food_list[i] = f_dict

            
            merge = {
                'food':food_list
            }

            print(merge)

            return jsonify(merge)
        
        except Exception as e:
            print('에러 : {}'.format(e))
            return 'null'

    elif jsonData['type'] == 'tour':
        try:
            jsonData['title'] = jsonData['title'].replace('\xa0','')
            with open('tf-idf/tour/{}.txt'.format(jsonData['region']), 'rb') as f:
                X = pickle.load(f)
            Tops = pd.DataFrame(X[jsonData['title']]).sort_values(jsonData['title'], ascending = False)[1:3]
            Tops.columns = ['title']
            Tops['title'] = Tops.index
            Tops.reset_index(drop=True,inplace=True)

            for index in range(0,len(Tops)):
                sql = """select title,lat,lng,region from tour_info where title LIKE '%"""+str(Tops['title'][index])+"""%' LIMIT 1;"""
                curs.execute(sql)
                rows = curs.fetchall()

                rows_to_df = pd.DataFrame(rows)
                rows_to_df.columns = ['title','lat','lng','region']
                rows_to_df['type'] = 'tour'

                data=data.append(rows_to_df , ignore_index=True)

            
            data.drop_duplicates(inplace=True)
            tour_list = data.to_dict(orient = "records")

            for i in range(0,len(tour_list)):
                t_dict = tour_list[i]
                t_dict['position'] = [0,0]
                tour_list[i] = t_dict

            
            merge = {
                'tour':tour_list
            }

            print(merge)

            return jsonify(merge)
        except Exception as e:
            print('에러 : {}'.format(e))
            return 'null'
    
    else:
        return 'null'


@app.route('/tfidf_follow', methods=['POST'])
def tfidf_follow():
    jsonData = json.loads(request.get_data(), encoding='utf-8')
    jsonData = pd.json_normalize(jsonData['data'])
    titles = list(jsonData['name'])
    data = pd.DataFrame()
    data['title'] = ''
    data['type'] = ''
    count = 0
    for i in range(0,len(jsonData)):
        if jsonData['type'][i] == 'food':
            try:
                jsonData['name'][i] = jsonData['name'][i].replace('\xa0','')
                with open('tf-idf/food/{}.txt'.format(jsonData['region'][i]), 'rb') as f:
                    X = pickle.load(f)

                Tops = pd.DataFrame(X[jsonData['name'][i]]).sort_values(jsonData['name'][i], ascending = False)[1:3]
                Tops.columns = ['title']
                Tops['title'] = Tops.index
                Tops.reset_index(drop=True,inplace=True)

                for index in range(0,len(Tops)):
                    data.loc[count] = [Tops['title'][index],'food']
                    count = count + 1  
                
            except Exception as e:
                print('에러 : {}'.format(e))
                continue
        elif jsonData['type'][i] == 'tour':
            try:
                jsonData['name'][i] = jsonData['name'][i].replace('\xa0','')
                with open('tf-idf/tour/{}.txt'.format(jsonData['region'][i]), 'rb') as f:
                    X = pickle.load(f)
                Tops = pd.DataFrame(X[jsonData['name'][i]]).sort_values(jsonData['name'][i], ascending = False)[1:3]
                Tops.columns = ['title']
                Tops['title'] = Tops.index
                Tops.reset_index(drop=True,inplace=True)

                for index in range(0,len(Tops)):
                    data.loc[count] = [Tops['title'][index],'tour']
                    count = count + 1  

            except Exception as e:
                print('에러 : {}'.format(e))
                continue
        else:
            continue

    data = data[~data['title'].isin(titles)]
    food_df = data[data['type'] == 'food']
    food_df.drop_duplicates(inplace=True)
    tour_df = data[data['type'] == 'tour']
    tour_df.drop_duplicates(inplace=True)


    merge = {
        "food":food_df.to_dict(orient = "records"),
        "tour":tour_df.to_dict(orient = "records")
    }

    print(merge)

    return jsonify(merge)


@app.route('/tfidf', methods=['POST'])
def tfidf():
    jsonData = json.loads(request.get_data(), encoding='utf-8')
    if jsonData['type'] == 'food':
        try:
            jsonData['title'] = jsonData['title'].replace('\xa0','')
            with open('tf-idf/food/{}.txt'.format(jsonData['region']), 'rb') as f:
                X = pickle.load(f)
            Top = pd.DataFrame(X[jsonData['title']]).sort_values(jsonData['title'], ascending = False)[1:11]
            arr = {'title': list(Top.index)}
        except Exception as e:
            print('에러 : {}'.format(e))
            arr = {'title':''}
    elif jsonData['type'] == 'tour':
        try:
            jsonData['title'] = jsonData['title'].replace('\xa0','')
            with open('tf-idf/tour/{}.txt'.format(jsonData['region']), 'rb') as f:
                X = pickle.load(f)
            Top = pd.DataFrame(X[jsonData['title']]).sort_values(jsonData['title'], ascending = False)[1:11]
            arr = {'title': list(Top.index)}
        except Exception as e:
            print('에러 : {}'.format(e))
            arr = {'title':''}
    else:
        arr = {'title':''}
    return jsonify(arr)

@app.route('/<kind1>/<kind2>/<country>/<title>', methods=['POST', 'GET'])
def return_img(kind1,kind2,country,title):
    try:
        filename =  default_path + '\\' + kind1 + '\\' + kind2 + '\\' + country + '\\' + title + '.png'
        return send_file(filename, mimetype='image/gif')
    except:
        return ''

@app.route('/top/<kind2>/<country>/<city>/<title>/<n>')
def top_tfidf(kind2, country, city, title, n):    
    with open(default_path+'\\'+'top'+'\\'+kind2+'\\'+country+'\\'+city+'.txt', 'rb') as f:
        X = pickle.load(f)    
    cosine_df = pd.DataFrame((np.matrix(X.values) * np.matrix(X.values.T)).A, columns = list(X.index), index = list(X.index))
    Top = pd.DataFrame(cosine_df[title]).sort_values(title, ascending = False)[1:2]
    Top_dict = {Top.index[0] : X.loc[Top.index[0]].sort_values(ascending = False)[0:int(n)].to_dict()}
    return jsonify(Top_dict)

@app.route('/rank/<kind>/<country>/<city>/<title>', methods=['POST', 'GET'])
def rank(kind,country,city,title):
    with open(default_path + '\\tf-idf\\'+country+'\\'+city+'.txt', 'rb') as f:
        X = pickle.load(f)
    cosine_df = pd.DataFrame((np.matrix(X.values) * np.matrix(X.values.T)).A, columns = list(X.index), index = list(X.index))
    rank = pd.DataFrame(cosine_df[title]).sort_values(title, ascending = False)[1:9]
    rank.rename({str(title) : 'Cosine Smilarity'}, axis = 'columns', inplace = True)
    rank['rank'] = list(range(1,11))    
    column_list = ['rank', 'Cosine Smilarity']
    rank = rank[column_list]
    return jsonify(rank.to_dict())

@app.route('/emolex', methods=['POST', 'GET'])
def emotion():  
    #음식점 이외의 emolex_score도 필요
    data = pd.read_csv('emolex_score.csv')

    jsonData = json.loads(request.get_data(), encoding='utf-8')
    
    data['joy'] = z_score_normalization(data,'joy')
    data['trust'] = z_score_normalization(data,'trust')
    data['anticipation'] = z_score_normalization(data,'anticipation')
    data['surprise'] = z_score_normalization(data,'surprise')
    data['sadness'] = z_score_normalization(data,'sadness')
    data['anger'] = z_score_normalization(data,'anger')
    data['fear'] = z_score_normalization(data,'fear')
    data['disgust'] = z_score_normalization(data,'disgust')


    data = data.loc[data['restaurant'] == jsonData['title']]


    data.reset_index(drop=True,inplace=True)
    try:
        target_data = {
            'joy':data['joy'][0],
            'trust':data['trust'][0],
            'anticipation':data['anticipation'][0],
            'surprise':data['surprise'][0],
            'sadness':data['sadness'][0],
            'anger':data['anger'][0],
            'fear':data['fear'][0],
            'disgust':data['disgust'][0],
        }
    except:
        target_data = {
            'joy':0,
            'trust':0,
            'anticipation':0,
            'surprise':0,
            'sadness':0,
            'anger':0,
            'fear':0,
            'disgust':0,
        }
    return jsonify(target_data)

def z_score_normalization(df, feature):
    std_list = df[feature]
    std_list = std_list.values.astype(float)
    std_list = ss.zscore(std_list) + 2.5

    return std_list

@app.route('/schedule', methods=['POST'])
@cross_origin()
def scadule():
    jsonData = json.loads(request.get_data(), encoding='utf-8')

    food = pd.json_normalize(jsonData['food'])
    tour = pd.json_normalize(jsonData['tour'])
    hotel = pd.json_normalize(jsonData['hotel'])

    data = pd.concat([food,tour,hotel])
    data.to_excel('넘어온데이터.xlsx',index=False)
    return 'null'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='7000')