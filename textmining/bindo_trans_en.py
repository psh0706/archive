# coding=utf-8
import pandas as pd
import nltk
from nltk.stem.porter import PorterStemmer  # 어근추출
from nltk.tokenize import RegexpTokenizer  # 정규표현식을 사용하여 단어 토큰화를 제공
from nltk.corpus import stopwords  # 불용어 정의
from wordcloud import WordCloud
from collections import Counter
import matplotlib.pyplot as plt
from googletrans import Translator
from konlpy.tag import Hannanum
hannanum = Hannanum()


text = str()

df = pd.read_csv('C:\\Users\\suhyun\\Desktop\\TextMining\\pr_34_en.csv')
lines = list(df['content'])


def trans(line):
    translator = Translator()
    # # 네이버 파파고 api이용하기
    # url="https://openapi.naver.com/v1/papago/n2mt?source=en&target=ko&text="
    # request_url = "https://openapi.naver.com/v1/papago/n2mt"
    # headers= {"X-Naver-Client-Id": "E3Qm4KfmUlFJjFRsCuTf", "X-Naver-Client-Secret":"Qbj4Gdlgi2"}
    # params = {"source": "en", "target": "ko", "text": line}
    # response = requests.post(request_url, headers=headers, data=params)
    # print(response.text)
    # return response.text
    # #result = response.json()
    # #print(result)
    print("trans함수")
    result = translator.translate(line,dest='ko')
    print(result.text)
    return result.text


temp = []
for line in lines :
    temp.append(hannanum.nouns(trans(str(line))))


def flatten(l):
    flatList = []
    
    for elem in l:
        if type(elem) == list:
            for e in elem:
                flatList.append(e)
        else:
            flatList.append(elem)

    return flatList

word_list = flatten(temp)

word_list = pd.Series([x for x in word_list if len(x)>1])

word_list.value_counts().head(30)


font_path = "NanumBarunGothic.ttf"
wordcloud = WordCloud(
font_path = font_path,
width = 800,
height = 800,
background_color = "white"
)

count = Counter(word_list)

wordcloud = wordcloud.generate_from_frequencies(count)

array = wordcloud.to_array()

fig = plt.figure(figsize=(10,10))
plt.imshow(array, interpolation="bilinear")
plt.show()
fig.savefig('wordcloud_hosu2.png')

