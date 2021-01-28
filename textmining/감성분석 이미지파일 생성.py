%%time
# 테이블 자료구조를 이용하여 데이터 조작 및 분석
import pandas as pd
# 시각화 라이브러리
import plotly
import plotly.graph_objects as go     
import plotly.io as pio
# Plotly 시각화 데이터를 저장하기 위한 라이브러리
import matplotlib.pyplot as plt
import os

emolex_score = pd.read_csv('emolex_score.csv')
columns = ['restaurant','country','rating','joy','trust','anticipation',
           'surprise','sadness','anger','fear','disgust']
emolex_score = emolex_score[columns]

for i in range(0,len(emolex_score)):
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
