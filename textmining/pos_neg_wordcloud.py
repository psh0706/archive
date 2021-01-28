import pandas as pd
from wordcloud import WordCloud
from collections import Counter
import matplotlib.pyplot as plt
import pickle
import numpy as np
from afinn import Afinn
import os

with open("food_review_merge.txt", "rb") as f: 
    df_food_review = pickle.load(f)
    
df_food_review = df_food_review.drop_duplicates(['restaurant','country'])
df_food_review['restaurant'] = df_food_review['restaurant'].str.lower()
df_food_review.reset_index(drop=True,inplace=True)

afinn = Afinn()


global wordcloud_neg
#부정
wordcloud_neg = WordCloud(
        width = 800,
        height = 800,
        background_color = "Black", colormap="Reds"
        )

global wordcloud_pos 
#긍정
wordcloud_pos= WordCloud(
        width = 800,
        height = 800,
        background_color = "White", colormap="Blues"
        )

def __array__(self):
    """Convert to numpy array.
    Returns
    -------
    image : nd-array size (width, height, 3)
        Word cloud image as numpy matrix.
    """
    return self.to_array()

def to_array(self):
    """Convert to numpy array.
    Returns
    -------
    image : nd-array size (width, height, 3)"
        Word cloud image as numpy matrix.
    """
    return np.array(self.to_image())

def afinn_map(df_food_review):

    if (os.path.isfile('positive\\restaurant\\' + str(df_food_review['country']) + '\\' + str(df_food_review['restaurant']) + '.png')) and (os.path.isfile('negative\\restaurant\\' + str(df_food_review['country']) + '\\' + str(df_food_review['restaurant']) + '.png')):
        print(str(df_food_review['restaurant']) + '.png 가 이미 존재합니다.')
        return
    
    global wordcloud_neg
    global wordcloud_pos
    
    df_afinn = pd.DataFrame(list(zip(afinn.find_all(df_food_review['content']), afinn.scores_with_pattern(df_food_review['content']))), columns = ['word', 'polarity']) 
    # 부정 어휘 DataFrame
    df_result_neg = df_afinn[df_afinn['polarity'].isin(['-5', '-4', '-3', '-2', '-1'])]
    # 긍정 어휘 DataFrame
    df_result_pos = df_afinn[df_afinn['polarity'].isin(['1', '2', '3', '4', '5'])]
    
    # 긍정, 부정 어휘 빈도분석
    count_neg = Counter(df_result_neg['word'])
    count_pos = Counter(df_result_pos['word'])
    
    # WordCloud
    try:
        # 긍정, 부정 WordCloud 생성
        wordcloud_neg = wordcloud_neg.generate_from_frequencies(count_neg)
        wordcloud_pos = wordcloud_pos.generate_from_frequencies(count_pos)
        
        # 긍정 부정 WordCloud 객체를 numpy array로 변환        
        array_neg = wordcloud_neg.to_array()
        array_pos = wordcloud_pos.to_array()
        
        # 긍정 어휘 WordCloud Image 생성 및 저장
        # %matplotlib inline

        fig = plt.figure(figsize=(10,10))
        plt.imshow(array_pos, interpolation="bilinear")  # 보간법 = 쌍선형 보간법
        plt.xticks([], [])
        plt.yticks([], [])
        # plt.show()    
        fig.savefig('positive\\restaurant\\' + str(df_food_review['country']) + '\\' + str(df_food_review['restaurant']) + '.png')
        plt.close('all')
        fig.clear()
        
        # 주정 어휘 WordCloud Image 생성 및 저장
        # %matplotlib inline
    
        fig = plt.figure(figsize=(10,10))
        plt.imshow(array_neg, interpolation="bilinear")  # 보간법 = 쌍선형 보간법
        plt.xticks([], [])
        plt.yticks([], [])
        # plt.show()    
        fig.savefig('negative\\restaurant\\' + str(df_food_review['country']) + '\\' + str(df_food_review['restaurant']) + '.png')   
        plt.close('all')
        fig.clear()
        
    except Exception as E:
        print(E)
        
    print(str(df_food_review['restaurant'])) 
    

df_food_review.apply(afinn_map, axis = 1)

print('end')