#!/usr/bin/env python
# coding: utf-8


## 필요 라이브러리 ##
import pandas as pd                 
import numpy as np                  

import pickle
import glob                
import os                 
import re              
from afinn import Afinn # 대표적인 eng 감성사전. 긍정(+), 부정(-) 로 분류.
from nltk.corpus import stopwords  # 불용어 처리. the, a, an 같은 의미없는 관사들을 제거
from nltk.stem.porter import PorterStemmer  # 어간 추출
from nltk.tokenize import RegexpTokenizer   # 토큰화
import nltk # Natural Languagae Toolkit. 자연어 처리 패키지

tokenizer = RegexpTokenizer('[\w]+')
count = 0
# 감성사전 불러오기
NRC=pd.read_csv('nrc.txt',engine="python",header=None,sep="\t")

# 감성어 사전 열 이름 재정의, positive, negative 제거, 유의미한 감성어만 추출
NRC.columns = ['word', 'emotion', 'score']
NRC = NRC[NRC['emotion'] != 'positive']
NRC = NRC[NRC['emotion'] != 'negative']
NRC=NRC[(NRC != 0).all(1)]
del NRC['score']         
NRC=NRC.reset_index(drop=True)

def filter_emotion(x):
    return NRC_N['word'].isin([x]).any()

# 감성점수를 저장할 데이터프레임 선언
column_name = ['restaurant','country','rating','joy', 'trust', 'anticipation', 'surprise', 'sadness', 'anger', 'fear', 'disgust']
df_emolex_score = pd.DataFrame(columns=column_name)

#restaurant_review = pd.read_csv(default_path + '\\data\\data_import.csv')

with open('food_review_merge.txt', 'rb') as f:
    restaurant_review = pickle.load(f) # 단 한줄씩 읽어옴
restaurant_review = restaurant_review.drop_duplicates(['restaurant','country'])
restaurant_review.reset_index(drop=True,inplace=True)

for content in restaurant_review['content']:
    #emolex score 구조 정의
    emolex_score = {
        'joy' : 0,
        'trust' : 0,
        'anticipation' : 0,
        'surprise' : 0,
        'sadness' : 0,
        'anger' : 0,
        'fear' : 0,
        'disgust' : 0
    }
    tokens = tokenizer.tokenize(content)
    NRC_N = NRC[NRC['word'].isin(tokens)].copy()
    match_words = list(filter(filter_emotion, tokens))
    #match_words = [x for x in tokens if x in list(NRC_N['word'])]
    emotion_list = []
    for match_word in match_words:
        emotions = list(NRC[NRC['word'].isin([match_word])]['emotion'])
        emotion_list = emotion_list + emotions
    emolex_score = pd.Series(emotion_list).value_counts()
    if len(emolex_score) < 8:
        if not emolex_score.get("joy"):
            emolex_score['joy'] = 0
        if not emolex_score.get("trust"):
            emolex_score['trust'] = 0
        if not emolex_score.get("anticipation"):
            emolex_score['anticipation'] = 0
        if not emolex_score.get("surprise"):
            emolex_score['surprise'] = 0
        if not emolex_score.get("sadness"):
            emolex_score['sadness'] = 0
        if not emolex_score.get("anger"):
            emolex_score['anger'] = 0
        if not emolex_score.get("fear"):
            emolex_score['fear'] = 0
        if not emolex_score.get("disgust"):
            emolex_score['disgust'] = 0
        
    df_emolex_score.loc[count] = [restaurant_review['restaurant'].loc[count],restaurant_review['country'].loc[count]
                                  ,restaurant_review['rating'].loc[count],emolex_score['joy'], emolex_score['trust']
                                  , emolex_score['anticipation'], emolex_score['surprise'], emolex_score['sadness']
                                  , emolex_score['anger'], emolex_score['fear'], emolex_score['disgust']]
    print(count, '번째가 완료되었습니다. ')
    count += 1
df_emolex_score.to_csv("emolex_score_sample.csv")