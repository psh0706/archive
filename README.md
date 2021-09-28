[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fpsh0706%2Fportfolio.git&count_bg=%23FFD41B&title_bg=%23555555&icon=statuspage.svg&icon_color=%23FFFFFF&title=hits&edge_flat=true)](https://hits.seeyoufarm.com)
![followers](https://img.shields.io/github/followers/psh0706?style=social)

# Introduction

해당 문서들은 자대의 인공지능 연구실에서 경험했던 장기프로젝트에서 코드리뷰를 하기에 적합한 일부를 발췌한 것입니다. 
프로젝트는 크게 다음과 같은 순서로 진행 되었습니다.  
 **크롤링 -> 정제 -> 텍스트 마이닝 -> 추천 알고리즘 구현 -> mirror site에 접목**  
Repository에 push 되어있는 디렉토리들은 그 중 크롤링, 텍스트마이닝, 웹과 관련된 코드들을 정리해 놓은 것입니다.

### Project Information

+ **프로젝트 명**  
	여행고수
+ **프로젝트 목표**  
	실제 여행지에 여행을 다녀온 여행자들의 리뷰 데이터들을 기반으로 여러가지 머신러닝 기법을 적용하여, 사용자의 성향을 파악하고 그에 맞는 여행지(관광지/음식점/호텔) 등을 추천하고 자동 스케줄링 해주는 솔루션을 개발한다. 

# Directory
### Crawling  
  
+ **사족**  
	데이터를 수집하기 위해 크롤러를 만들었던 코드들을 정리해 보았습니다.  
	실제로는 레스토랑/관광지/음식점 으로 나누어 더 많은 크롤러가 사용되었지만, 제가 맡았던 부분인 관광지를 위주로 정리해 보았습니다.
	중간중간 주석을 달기는 했었으나, 이미지를 포함한 자세한 코드 리뷰는 **크롤링 코드 핵심 정리.pptx** 에도 있습니다.  
	  
+ **기술스택**  
	+ **Language**  
			`python3`  : 주 언어로 python3를 사용했습니다.  
  
	+ **Library(python)**  
			`beautifulsoup4` : 정적인 요소를 크롤링 할 때 사용했습니다.  
			`Selenium` : click event 등 동적인 요소를 크롤링 할 때 사용했습니다.  
			`pandas` : 데이터프레임 구조를 위해 사용했습니다.  
			`os` : 디렉토리 구조를 활용하기 위해 사용했습니다.
  
	+ **ect**  
			`chromedriver.exe` : 크롤링 시 크롬을 제어하기 위한 프로그램입니다. (구글제공)  
  
+ **요약**  
	|INDEX|코드명|요약설명|LOC(ABT)|비고|
	|:---:|:--- | :--- |:---:|:---|
	|1| url_list.py | 관광지 관련 페이지 url을 크롤링해 리스트화 | 200 |  |  
	|2| play_info.py | **1**의 결과를 이용해 상세 정보를 크롤링 | 400 |  |  
	|3| play_review.py | **1**의 결과를 이용해 리뷰 크롤링 | 730 |  |  
	|4| Strap.py | 크롤링에 필요한 기본 함수를 모듈화 | 158 |  |   
	|5| gathering.py | 크롤링에 필요한 기본 함수를 모듈화 | 135 |  |  
 	|6| 음식점 info 위경도 추가.ipynb | 주소 정보를 이용하여 문서에 위,경도를 추가 | - |jupyter, 레스토랑 파트|
  
***
### Textmining  
  
+ **사족**  
	크롤링한 결과를 텍스트마이닝했던 코드들입니다.  
	대부분 코드들의 길이가 짧으나, 머신 러닝을 해보았던 경험이라 추가하였습니다.
  
+ **기술스택**  
	+ **Language**  
			`python3`  : 주 언어로 python3를 사용했습니다.  
  
	+ **Library(python)**   
			`pandas` : 데이터프레임 구조를 위해 사용했습니다.  
			`plotly` : 데이터 시각화를 위해 사용했습니다.  
			`matplotlib` : 데이터 시각화를 위해 사용했습니다.  
			`wordcloud` : 워드클라우드 생성시 사용했습니다.  
			`os` : 디렉토리 구조를 활용하기 위해 사용했습니다.  
			`nltk` : 자연어 처리를 위해 사용했습니다.  
			`konlpy` : 자연어 처리를 위해 사용했습니다.  
			`pickle` : pickle 덤프파일을 위해 사용했습니다.  
			`Afinn` : 감성분석을 위해 사용했습니다.  
  
	+ **ect**  
			`NRC.txt` : 미리 정의되어있는 감성사전 입니다.  
    
+ **요약**  
	|INDEX|코드명|요약설명|LOC(ABT)|비고|
	|:---:|:--- | :--- |:---:|:---|
	|1| 2-gram_image.py | 바이그램을 워드클라우드화 하여 저장 | 100 |  |  
	|2| bindo_en.py | 단어의 빈도수를 추출하여 워드클라우드로 만든 짧은 코드 (영어 ver.)| 65 |  |  
	|3| bindo_kr.py | 단어의 빈도수를 추출하여 워드클라우드로 만든 짧은 코드 (한국어 ver.) | 55 |  |  
	|4| emolex_score_making.py | 감성점수를 계산해서 csv로 저장 | 90 |  | 
	|5| emolex_to_img.py | **4**의 결과를 이용해 chart img를 저장 |30 |  |   
	|6| pos_neg_wordcloud.py | 긍정/부정 워드클라우드를 생성 | 115 ||
	|7| TF-IDF.ipynb | 도시별 레스토랑들의 TF-IDF 값을 계산해 저장 | - |jupyter|  
	|8| 영어리뷰 빈도분석 (bi-gram).ipynb |불용어를 새롭게 추가한 변형 bi-gram|-  |jupyter|
  
 
***	
### Web
  
+ **사족**  
	웹 서버에서 back-end를 구현했던 일부 코드와 python으로 작성한 restful api 입니다.  
	웹에 대한 코드들은 회사의 보안과 관련된 부분이 많아 두 파일 만을 발췌하여 보여드리는 점 양해 부탁드립니다.  
  
+ **기술스택**  
	+ **Language**  
			`javascript` : 웹 구현 시 사용했습니다.
  
	+ **Library(python)**   
			`flask framework` : api가 웹서버와의 통신을 위한 용도로 사용했습니다.
  
	+ **ect**  
			`Node.js express framework` : 웹서버 개발시 사용한 프레임워크 입니다.
  
+ **요약**  
	|INDEX|코드명|요약설명|LOC(ABT)|비고|
	|:---:|:--- | :--- |:---:|:---|
	|1| category.js|사용자가 선택한 키워드+여행일정+여행지 정보를 받아 여행지를 추천해주는 백엔드 code | 380 |  |  
	|2| api.py | 웹 서버가 호출해 쓰는 restful api로, category.js에서 호출해 사용| 620 |  |  
    
  
  
  

  
#### 📧Contacts  
[![navermail Badge](https://img.shields.io/badge/Naver-2DB400?style=flat-square&logo=Nintendo&logoColor=white&link=mailto:best8427@naver.com)](mailto:best8427@naver.com)
[![Gmail Badge](https://img.shields.io/badge/Gmail-d14836?style=flat-square&logo=Gmail&logoColor=white&link=mailto:best8427@gmail.com)](mailto:best8427@gmail.com)

