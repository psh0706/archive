import pandas as pd
from wordcloud import WordCloud
from collections import Counter
from konlpy.tag import Hannanum  # 한나눔 현태소 분석기 사용
import matplotlib.pyplot as plt
hannanum = Hannanum()


font_path = "NanumBarunGothic.ttf"


csv_data = pd.read_csv('C:\\Users\\suhyun\\Desktop\\TextMining\\pr_34_ko.csv', header=None)
count = csv_data.shape[0]
for i in range(1,count):
    print(csv_data[3][i])


temp = []

for i in range(len(csv_data)):
    temp.append(hannanum.nouns(csv_data[3][i]))

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

