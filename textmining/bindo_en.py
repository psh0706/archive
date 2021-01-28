import pandas as pd
import nltk
from nltk.stem.porter import PorterStemmer  # 어근추출
from nltk.tokenize import RegexpTokenizer  # 정규표현식을 사용하여 단어 토큰화를 제공
from nltk.corpus import stopwords  # 불용어 정의
from wordcloud import WordCloud
from collections import Counter
import matplotlib.pyplot as plt

text = str()


nltk.download('stopwords')
df = pd.read_csv('C:\\Users\\suhyun\\Desktop\\TextMining\\pr_34_en.csv')
lines = list(df['content'])

tokenizer = RegexpTokenizer('[\w]+')  # \w : 단어 영문자+숫자+_(밑줄) [0-9a-zA-Z_]
stop_words = stopwords.words('english')  # 불용어 정의

for line in lines :
    text += ' '+ str(line)


### 영단어 전처리 과정
words =text.lower()  # 모든 단어를 소문자로 변환
tokens = tokenizer.tokenize(words)  # 단어 단위로 토큰화
stopped_tokens = [i for i in list((tokens)) if not i in stop_words]  # 불용어 제거
stopped_tokens2 = [i for i in stopped_tokens if len(i)>1]  # 한 글자 제거

print(pd.Series(stopped_tokens2).value_counts().head(30))  # 리스트 안의 단어들을 pandas Series 형태로 변환 후 단어 빈도를 카운트

#워드클라우드 설정
wordcloud = WordCloud(
width = 800,
height = 800,
background_color = "white"
)

count = Counter(stopped_tokens2)
wordcloud = wordcloud.generate_from_frequencies(count)

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

array = wordcloud.to_array()

#워드클라우드 그리기
fig = plt.figure(figsize=(10,10))
plt.imshow(array, interpolation="bilinear")  # 보간법 = 쌍선형 보간법
plt.show()
fig.savefig('wordcloud.png')