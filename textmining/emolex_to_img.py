
import pandas as pd
import plotly
import plotly.graph_objects as go     
import plotly.io as pio
import matplotlib.pyplot as plt
import os

#감성점수 csv 파일 데이터프레임으로 가져오기
emolex_score = pd.read_csv('emolex_score.csv')
columns = ['restaurant','country','rating','joy','trust','anticipation',
           'surprise','sadness','anger','fear','disgust']
#컬럼 붙혀줌
emolex_score = emolex_score[columns]

for i in range(0,len(emolex_score)):
    #레스토랑 이름으로 이미지 이름 저장하기 위해
    file_name = emolex_score['restaurant'][i]
    chart = go.Scatterpolar(
        r = [emolex_score['joy'][i],emolex_score['trust'][i],emolex_score['anticipation'][i],emolex_score['surprise'][i],
                 emolex_score['sadness'][i],emolex_score['anger'][i],emolex_score['fear'][i],emolex_score['disgust'][i]],
        theta = ['joy','trust','anticipation','surprise','sadness','anger','fear','disgust'],
        fill = 'toself'
    )
    layout = go.Layout(
        polar = dict(
            radialaxis = dict(showticklabels=False, ticks=''),
            angularaxis = dict(ticks='')
        ),
    )
    fig = go.Figure(data = chart,layout = layout)
    pio.write_image(fig, '감성분석\\' + emolex_score['country'][i] + '\\' + file_name + '.png') 
    print(emolex_score['country'][i])
