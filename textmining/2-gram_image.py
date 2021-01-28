import pandas as pd
import nltk
from nltk.util import ngrams
from nltk.stem.porter import PorterStemmer  # 어근추출
from nltk.tokenize import RegexpTokenizer  # 정규표현식을 사용하여 단어 토큰화를 제공
from nltk.corpus import stopwords  # 불용어 정의
import os
import glob
import re
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pickle
import gc


# 전처리가 완료된 pickle파일을 불러온다
with open("food_review_merge.txt","rb") as f:
    df_food_review = pickle.load(f)
    
df_food_review = df_food_review.drop_duplicates(['restaurant','country'])
df_food_review['restaurant'] = df_food_review['restaurant'].str.lower()
df_food_review.reset_index(drop=True,inplace=True)

# WordCloud 객체 생성 및 레이아웃 설정
wordcloud = WordCloud(
#font_path = font_path,
width = 800,
height = 800,
background_color = "white"
)

# 문장을 단어 묶음으로 변환
def english_tokenizer(lines):
    tokenizer = RegexpTokenizer('[\w]+')  # \w : 단어 영문자+숫자+_(밑줄) [0-9a-zA-Z_]

    stop_words = stopwords.words('english')  # 불용어 정의

    ### 영단어 전처리 과정
    words =lines.lower()  # 모든 단어를 소문자로 변환
    tokens = tokenizer.tokenize(words)  # 단어 단위로 토큰화
    stopped_tokens = [i for i in list((tokens)) if not i in stop_words]  # 불용어 제거
    words = [i for i in stopped_tokens if len(i)>1]  # 한 글자 제거
    
    return words

#Numpy 배열로 변환
def to_array(self):
    """Convert to numpy array.
    Returns
    -------
    image : nd-array size (width, height, 3)"
        Word cloud image as numpy matrix.
    """
    return np.array(self.to_image())

line = []
bi_gram = []

#음식점 한곳씩 반복문을 돌린다.
for index in range(0,len(df_food_review)):
    try:
        #이미지 존재하는지 확인
        if os.path.isfile('2-gram\\' + df_food_review['country'][index] + '\\{}.png'.format(str(df_food_review['restaurant'][index]))):
            print(str(df_food_review['restaurant'][index]) + "가 존재하므로 다음으로 넘어갑니다")
            continue
        line = []
        bi_gram = []
        words = english_tokenizer(df_food_review['content'][index])#음식점의 리뷰 문장을 단어로 변환한다.
        bi_tokens = ngrams(words,2)#변환한 단어를 ngrams함수를 이용해서 2-gram으로 변환한다.
        for i in bi_tokens: #변환된 bi_gram을 한 리스트에 집어넣는다
            bi_gram.append(i)
        sort = sorted(bi_gram, key = lambda x : x[0]) #정렬
        count = Counter(sort) #카운팅한다. (빈도수 freq를 위함)
        dict = { #카운팅한 bi_gram단어와 빈도수가 들어갈 dict 선언
            'term1' : [],
            'term2' : [],
            'freq' : []
        }

        for i,j in count.items(): #bi_gram단어와 빈도수를 입력한다.
            dict['term1'].append(list(i)[0])
            dict['term2'].append(list(i)[1])
            dict['freq'].append(j)
            
        bi_gram = pd.DataFrame(dict) #입력한 사전을 DataFrame으로 변환
        bi_gram.sort_values('freq',ascending=False,inplace=True) #정렬
        bi_gram['term'] = bi_gram['term1'] + ' ' + bi_gram['term2'] #두 단어를 하나의 단어로 합친다.
        
        bi_gram = bi_gram[['term','freq']] #필요한 컬럼만 남긴다
        sample = bi_gram.set_index('term').to_dict() #다시 딕셔너리로 변환
        wordcloud = wordcloud.generate_from_frequencies(sample['freq'])#wordcloud로 변환한다.
        array = wordcloud.to_array()#배열로 변환

        fig = plt.figure(figsize=(10,10))#figure 객체 생성 및 사이즈 설정
        plt.xticks([], [])
        plt.yticks([], [])
        plt.imshow(array, interpolation="bilinear")  # 보간법 = 쌍선형 보간법
        fig.savefig( '2-gram\\' + df_food_review['country'][index] + '\\{}.png'.format(str(df_food_review['restaurant'][index]))) # 이미지 파일을 생성한다.
        fig.clear()
        plt.close() # 생성후 다음 반복문을 위해, 메모리 낭비를 최소화해야하므로 close한다.
        print(df_food_review['restaurant'][index])
    except Exception as e:
        print(e)
        continue