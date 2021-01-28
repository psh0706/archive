#!/usr/bin/env python
# coding: utf-8

# Selenium
from selenium import webdriver as Webd
from selenium.webdriver import ActionChains as AC # More, Click 
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException # Exception
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
# BeautifulSoup_4
from bs4 import BeautifulSoup

# ETC
import time # Sleep, Break 
import pandas as pd # DataFrame
import re # 정규 표현식
import os
import sys

# Module
from Strapy import Strapy 
from selenium.webdriver.support.wait import WebDriverWait

class ScrapingReview(Strapy):
    state = "Cambodia"
    temp_index = int()
    temp_url = str()
    review_num = int()

    review_scrap_list = {
        'index' : [],
        'url' : [],
        'local' : [],
        'scrap_flag' : [],
        'len' : 0 #개수
    }

    review_data = {
        'index' : [],
        'title' : [],
        'rating' : [],
        'content' : [],
        'date' : [],
        'lang' : [] #0이면 영어 1이면 한국어
    }
    


    def __init__(self, headless = None, target_url = None, chrome_driver_path = None):
        super().__init__(headless, target_url, chrome_driver_path)
        return

    def startScraping(self): # scraping을 시작하는 함수
        self.scrapContents()
        print("[Scraping] : 스크래핑이 완료 되었습니다.")
        return

    def scrapContents(self):      
        self.loadPlayReviewList()

        for i in range(0,ScrapingReview.review_scrap_list['len']):
            if int(ScrapingReview.review_scrap_list['scrap_flag'][i]) != 0: #1이면 스크래핑 완료니깐
                print("%s 는 이미 스크랩 되었으므로 이대로 이렇게 넘어갑니다!"%(ScrapingReview.review_scrap_list['url'][i]))
                continue #다음 인수로 넘기기
            
            print("영어 리뷰 스크래핑을 시작합니다.")
            self.scrapReview(ScrapingReview.review_scrap_list['index'][i], ScrapingReview.review_scrap_list['url'][i],"en",ScrapingReview.review_scrap_list['local'][i])#영어
            print("영어 리뷰 스크래핑이 끝났습니다.")

            
            
            print("한국어 리뷰 스크래핑을 시작합니다.")
            self.scrapReview(ScrapingReview.review_scrap_list['index'][i], ScrapingReview.review_scrap_list['url'][i],"ko",ScrapingReview.review_scrap_list['local'][i])#한국어 둘다 돌림
            print("한국어 리뷰 스크래핑이 끝났습니다.")
            

            self.scrap_flag(i)
            print("리뷰 스크래핑이 완료 되었습니다.")
        return

    def loadPlayReviewList(self) :
        try: 
            #상위 폴더 에서 읽어옴
            play_review_list_pdata = pd.read_csv("play_review_list_{}.csv".format(ScrapingReview.state), sep=",")
            print(play_review_list_pdata)
        except FileNotFoundError: # 파일이 없을 경우에는 그냥 첫 출력을 하면 됨.
            pass


        else: 
            ScrapingReview.review_scrap_list['len'] = int(play_review_list_pdata.shape[0])
            for i in range(0,ScrapingReview.review_scrap_list['len']):#읽어야 하는 것들을 함수호출해서 저장한 것 / 개수만큼 for문 돌리기
                ScrapingReview.review_scrap_list['index'].append(int(play_review_list_pdata.at[i,'index']))
                ScrapingReview.review_scrap_list['local'].append(str(play_review_list_pdata.at[i,'local']))
                ScrapingReview.review_scrap_list['url'].append(str(play_review_list_pdata.at[i,'url']))
                ScrapingReview.review_scrap_list['scrap_flag'].append(int(play_review_list_pdata.at[i,'scrap_flag']))
        return
    
    def scrap_flag(self,index):
        try:
            play_reivews_pdata = pd.read_csv("play_review_list_{}.csv".format(ScrapingReview.state), sep=",")
        except FileNotFoundError:
            pass
        else:
            play_reivews_pdata['scrap_flag'][index] = 1
            play_reivews_pdata.to_csv("play_review_list_{}.csv".format(ScrapingReview.state), index=False)

    def scrapReview(self, index, url, lang, local): 
        start_page_number = 0
        now_page_number = 0
        last_page_number = 0
        ScrapingReview.temp_index = index
        ScrapingReview.temp_url = url

        print("현재 페이지 : %s / %s"%(url,lang))
        #여기서부터 웹드라이버 로드
        self.loadWebDriver(False, url, "chromedriver.exe")
        
        lang_click_result = self.selectLanguage(lang)
        if lang_click_result == -1:
            print("%s 리뷰가 없습니다."%(lang))
            self.exitChromeDriver()
            return
        self.refreshInstance(True)

        last_page_number = self.extractLastPageNumber(lang)

        #리뷰 개수에 제한 둠. 100~5000 개 사이만 크롤링
        if(last_page_number == -1):
            print("{} 리뷰 개수가 0개 이므로 크롤링을 넘어갑니다".format(lang))
            return

        if(ScrapingReview.review_num <100 ):
            print("리뷰개수가 적어 크롤링을 넘어갑니다.")
            self.scrap_flag(index)
            self.exitChromeDriver()
            return
        elif(ScrapingReview.review_num > 5000):
            print("리뷰개수가 많아 5000개로 제한합니다.")
            try:
                tag = self.chrome_instance.find_elements_by_css_selector("#btf_wrap > div > div > div > div > div > div > div > div > div > div > a > span > span")
            except NoSuchElementException:
                tag = self.chrome_instance,find_elements_by_css_selector("div.review-container > div > div > div > div > div.quote")
            if len(tag) == 5 :
                last_page_number = 1000
            else:
                last_page_number = 500
            
            print("Last Page Number = %d"%last_page_number)
        else: print("리뷰개수에 문제가 없어 모두 크롤링합니다.")

        #끊긴 부분부터 다시 돌리기 위해 skipFlag 호출
        start_page_number =self.skipFlag(index,lang)
        
        for now_page_number in range(start_page_number, last_page_number):
            
            #스크래핑 시작
            self.scrapRating(lang)
            self.scrapTitle(lang)
            self.scrapContent(lang)
            self.scrapVisitingDate(lang)
            self.setLanguage(lang)
            self.setIndex(index)  
        
            self.savePlayReviewInCSVFormat()

            #비우기 중복저장 피하기 위해 저장 후 clear
            ScrapingReview.review_data['index'].clear()
            ScrapingReview.review_data['title'].clear()
            ScrapingReview.review_data['rating'].clear()
            ScrapingReview.review_data['content'].clear()
            ScrapingReview.review_data['date'].clear()
            ScrapingReview.review_data['lang'].clear()

            if (last_page_number-1) != now_page_number:
                self.clickNextButton(now_page_number,lang)
                print("다음 눌렀습니다. 현재 페이지 : %d"%(self.extractNowPageNumber(lang)))
            
        self.exitChromeDriver()

        return
     
    def selectLanguage(self, lang):

        i = int(0)

        # 언어 선택
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                self.clickMoreLangButton(lang)
                
                #동일한 페이지여도 구조만 다른 버전이 다양하게 존재.. 복잡하지만 다음과 같이 조건식을 걸어준다.
                css_language_tags = self.chrome_instance.find_elements_by_css_selector("#BODY_BLOCK_JQUERY_REFLOW > div > div > div> ul > li")
                if not css_language_tags:
                    css_language_tags = self.chrome_instance.find_elements_by_css_selector("div.is-3-tablet > ul.location-review-review-list-parts-ReviewFilter__filter_table--1H9KD > li")
                    if not css_language_tags:
                        css_language_tags = self.chrome_instance.find_elements_by_css_selector("#BODY_BLOCK_JQUERY_REFLOW > div > div> div > div > label")
                        if not css_language_tags:
                            css_language_tags = self.chrome_instance.find_elements_by_css_selector("div > div > div > div > div.prw_rup.prw_filters_detail_language.ui_column.separated.is-3 > div > div.content > div > div > label")
                            if not css_language_tags:
                                self.urlFlag(self.extractNowPageNumber(lang),lang)
                                print("언어를 선택하는 컨테이너 태그가 없어, 현재 페이지 수를 저장하고 프로그램을 종료합니다.")
                                sys.exit()

                for element in css_language_tags:
                    selected_lang = element.find_element_by_css_selector("input").get_attribute("value")

                    if selected_lang == lang:
                        self.chrome_instance.execute_script("arguments[0].click();", element) # lang과 같은 언어 선택(클릭)
                        print("%s클릭했습니다."%(lang))
                        time.sleep(2)

                        css_close_btn = self.chrome_instance.find_element_by_css_selector("#BODY_BLOCK_JQUERY_REFLOW > div > div > div._2EFRp_bb")
                        if not css_close_btn :
                            css_close_btn = self.chrome_instance.find_element_by_css_selector("#BODY_BLOCK_JQUERY_REFLOW > div > div.ui_close_x")
                            if not css_close_btn:
                                print("언어를 선택하는 중 css_close_btn의 css경로가 잘못되었습니다.")
                                return

                        self.chrome_instance.execute_script("arguments[0].click();",css_close_btn)
                        return
                    i += 1
                    if i == len(css_language_tags): #끝까지 돌았는데 영어나 한국어 리뷰가 없을 때.
                        return -1
            except NoSuchElementException:
                print("언어 선택 중 요소 예외")
            except StaleElementReferenceException:
                print("언어 선택 중 참조 예외")
                self.refreshInstance(True)
            return


    # 마지막 페이지
    # 한국어와 영어를 나누어 크롤링-저장 해야하는데 페이지 특성 상 언어 필터를 선택해도 정렬되는 것에 그치기 때문에
    # 페이지네이션의 마지막 페이지를 가져와 크롤링 하면, 모든 언어가 크롤링 된다.
    # 따라서 언어 별 리뷰 개수를 파악하여 마지막 페이지를 만들어준다.
    def extractLastPageNumber(self,lang):        
        last_page_number = 0
        for e_count in range(1, self.EXCEPTION_COUNT):
            self.refreshInstance()
            self.clickMoreLangButton(lang)
            css_container = self.chrome_instance.find_elements_by_css_selector("#BODY_BLOCK_JQUERY_REFLOW > div.ui_overlay > div.body_text > div > div")
            if not css_container:
                css_container = self.chrome_instance.find_elements_by_css_selector("div.choices.is-shown-at-tablet > div")
                if not css_container:
                    css_container = self.chrome_instance.find_elements_by_css_selector("#BODY_BLOCK_JQUERY_REFLOW > div > div > div> ul > li ")
                    if not css_container:
                        css_container = self.chrome_instance.find_elements_by_css_selector("div.is-3-tablet > ul.location-review-review-list-parts-ReviewFilter__filter_table--1H9KD > li")
                        if not css_container:
                            css_container = self.css_container.find_elements_by_css_selector("#BODY_BLOCK_JQUERY_REFLOW > div > div> div > div > label")
                            if not css_container:
                                self.urlFlag(self.extractNowPageNumber(lang),lang)
                                print("lastPageNumber 에서 language container가 없어, 현재 페이지 수를 저장하고 프로그램을 종료합니다.")
                                sys.exit()

            
            for css_element in css_container:

                if css_element.find_element_by_css_selector("input").get_attribute("value") == lang :
                    
                    #페이지 구조상 필요한 과정
                    try:
                        css_element = css_element.find_element_by_css_selector("span.count")
                    except NoSuchElementException:
                        css_element = css_element.find_element_by_css_selector("label > span.location-review-review-list-parts-LanguageFilter__paren_count--2vk3f")

                    #리뷰 개수를 가져온다.
                    review_num_string = css_element.text
                    number = re.findall("\d+", review_num_string) #정규표현식으로 2,341 -> [2,3,4,1]
                    
                    # 확인
                    print(number)

                    if len(number) >= 2 : #리뷰 개수가 두자리 수 이상이면
                        number_str = str()
                        for num in number:
                            number_str += str(num) #[2,3,4,1] -> "2341"
                        number = int(number_str)
                        ScrapingReview.review_num = int(number)

                        #매개변수로 한페이지에 리뷰 5개인지 10개인지 받아와서 lastpage 만들어 주는 부분.
                        tag = self.bs.select("div.review-container > div > div > div > div > div.quote")
                        selector = "div.review-container > div > div > div > div > div.quote"

                        #한 페이지에 있는 리뷰 title의 개수를 세면 몇 개인지 확인 가능
                        if not tag:
                            tag = self.bs.select("#btf_wrap > div > div > div > div > div > div > div > div > div > div > a > span > span")
                            selector = "#btf_wrap > div > div > div > div > div > div > div > div > div > div > a > span > span"
                            if not tag:
                                self.urlFlag(self.extractNowPageNumber(lang),lang)
                                print("리뷰 제목을 구해오는 태그가 없어, 현재 페이지 수를 저장하고 프로그램을 종료합니다.")
                                sys.exit()

                        if len(tag) == 5 :
                            last_page_number = int((ScrapingReview.review_num/5) + 1)
                        else :
                            last_page_number = int((ScrapingReview.review_num/10) + 1)
                        print(last_page_number)
                        
                        #언어 선택창 끄기
                        css_close_btn = self.chrome_instance.find_element_by_css_selector("#BODY_BLOCK_JQUERY_REFLOW > div > div > div._2EFRp_bb")
                        if not css_close_btn :
                            css_close_btn = self.chrome_instance.find_element_by_css_selector("#BODY_BLOCK_JQUERY_REFLOW > div > div.ui_close_x")
                            if not css_close_btn:
                                print("마지막 페이지를 구하는 중 css_close_btn의 css경로가 잘못되었습니다.")
                                return last_page_number                                
                        
                        self.chrome_instance.execute_script("arguments[0].click();",css_close_btn)
                        time.sleep(2)
                        return last_page_number
                    

                    #리뷰가 두 자리수 미만일 때 
                    ScrapingReview.review_num = int(number[0])
                    if(ScrapingReview.review_num == 0): return -1
                    
                    #위와 같은 과정
                    tag = self.bs.select("div.review-container > div > div > div > div > div.quote")
                    selector = "div.review-container > div > div > div > div > div.quote"

                    if not tag:
                        tag = self.bs.select("#btf_wrap > div > div > div > div > div > div > div > div > div > div > a > span > span")
                        selector = "#btf_wrap > div > div > div > div > div > div > div > div > div > div > a > span > span"
                        if not tag:
                            self.urlFlag(self.extractNowPageNumber(lang),lang)
                            print("리뷰 제목을 구해오는 태그가 없어, 현재 페이지 수를 저장하고 프로그램을 종료합니다.")
                            sys.exit()                    
                            
                    if len(tag) == 5 :
                        last_page_number = int((ScrapingReview.review_num/5) + 1)
                    else : 
                        last_page_number = int((ScrapingReview.review_num/10) + 1)
                    print(last_page_number)
                    
                    #언어 선택창 끄기
                    try:
                        css_close_btn = self.chrome_instance.find_element_by_css_selector("#BODY_BLOCK_JQUERY_REFLOW > div > div.ui_close_x")
                    except NoSuchElementException:
                        try:
                            css_close_btn = self.chrome_instance.find_element_by_css_selector("#BODY_BLOCK_JQUERY_REFLOW > div > div > div._2EFRp_bb")
                        except NoSuchElementException:
                            print("마지막 페이지를 구하는 중 css_close_btn의 css경로가 잘못되었습니다.")
                            return last_page_number     
                    
                    self.chrome_instance.execute_script("arguments[0].click();",css_close_btn)
                    time.sleep(2)
                    return last_page_number
            
            return last_page_number
        return last_page_number
    
    #현재 페이지 반환
    def extractNowPageNumber(self,lang):
        self.refreshInstance()
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                css_now_page_number_tag = self.bs.select("#taplc_location_reviews_list_resp_ar_responsive_0 > div > div > div > div > div > a.pageNum.current")
                if not css_now_page_number_tag:
                    css_now_page_number_tag = self.bs.select("div.mobile-more > div > div > div > a.pageNum.current")
                    if not css_now_page_number_tag:
                        css_now_page_number_tag = self.bs.select("div > div > div > div > span.pageNum.current")
                        if not css_now_page_number_tag:
                            css_now_page_number_tag = self.bs.select("div > div > div > a.pageNum.first.current")
                            if not css_now_page_number_tag:
                                print("현재 페이지 수를 구해오는 태그가 없습니다.")
                                sys.exit()
                    
                now_page_number = int(css_now_page_number_tag[0].text)
                break
            except NoSuchElementException:
                print("현재 페이지  중 요소 에외")
            except StaleElementReferenceException:
                print("현재 페이지  중 참조 예외")
                self.refreshInstance(True)
        
        return now_page_number
    
    #다음버튼 누르기
    def clickNextButton(self, prev_page_number, lang):
        next_url = str()
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                css_next_tag = self.chrome_instance.find_elements_by_css_selector("#component_19 > div > div > div.location-review-pagination-card-PaginationCard__wrapper--3epz_ > div > a.next")
                if not css_next_tag : 
                    css_next_tag = self.chrome_instance.find_elements_by_css_selector("div > div > div > div > a.next")
                    if not css_next_tag :
                        css_next_tag = self.chrome_instance.find_elements_by_css_selector("#taplc_location_reviews_list_resp_acr_responsive_0 > div > div > div > div > a.next")
                        break

                self.chrome_instance.execute_script("arguments[0].click();",css_next_tag[0])
                time.sleep(2)
                break
            except NoSuchElementException:
                print("다음버튼을 찾지 못했습니다.")
                self.urlFlag(self.extractNowPageNumber(lang),lang)
            except StaleElementReferenceException:
                print("다음버튼 StaleElementReferenceException")
                self.urlFlag(self.extractNowPageNumber(lang),lang)

            if e_count == 6:
                #url플래그-중복
                self.urlFlag(self.extractNowPageNumber(lang),lang)
                print("중복으로 인해 프로그램을 종료합니다.")
                sys.exit()

        return 

    #평점
    def scrapRating(self,lang):
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                tags = self.chrome_instance.find_elements_by_css_selector("div.review-container > div > div > div > div > span.ui_bubble_rating")
                if not tags:
                    tags = self.chrome_instance.find_elements_by_css_selector("div.location-review-review-list-parts-RatingLine__container--2bjtw > div > span")
                    if not tags:
                        tags = self.chrome_instance.find_elements_by_css_selector("div > div.ui_column.is-9 > span.ui_bubble_rating")
                        if not tags:
                            self.urlFlag(self.extractNowPageNumber(lang),lang)
                            print("평점을 구해오는 태그가 없어, 현재 페이지 수를 저장하고 프로그램을 종료합니다.")
                            sys.exit()
                break
            except NoSuchElementException:
                print("언어 선택 중 요소 에외")
                self.urlFlag(self.extractNowPageNumber(lang),lang)
                #url플래그
            except StaleElementReferenceException:
                print("언어 선택 중 참조 예외")    
                self.urlFlag(self.extractNowPageNumber(lang),lang)
                #url플래그

        for tag in tags:
            tag = tag.get_attribute('class')
            ScrapingReview.review_data['rating'].append(self.extractRatingInString(str(tag)))

        return

    #리뷰 제목
    def scrapTitle(self,lang):
        self.refreshInstance()
        tag = self.bs.select("div.review-container > div > div > div > div > div.quote")
        selector = "div.review-container > div > div > div > div > div.quote"

        if not tag:
            tag = self.bs.select("#btf_wrap > div > div > div > div > div > div > div > div > div > div > a > span > span")
            selector = "#btf_wrap > div > div > div > div > div > div > div > div > div > div > a > span > span"
            if not tag:
                self.urlFlag(self.extractNowPageNumber(lang),lang)
                print("리뷰 제목을 구해오는 태그가 없어, 현재 페이지 수를 저장하고 프로그램을 종료합니다.")
                sys.exit()

        tag = self.chrome_instance.find_elements_by_css_selector(selector)
    
        tag_len = len(tag)

        for i in range(0,tag_len):
            ScrapingReview.review_data['title'].append(str(tag[i].text))
        return

    #스크래핑 함수
    def scrapContent(self,lang):
        self.clickMoreButton(lang)
        self.refreshInstance()

        tags = self.chrome_instance.find_elements_by_css_selector("#btf_wrap > div > div > div > div > div > div > div > div > div > div > div > div > q > span")
        if not tags:
            tags = self.chrome_instance.find_elements_by_css_selector("div > div.ui_column.is-9 > div.prw_rup.prw_reviews_text_summary_hsx > div > p")
            if not tags:
                self.urlFlag(self.extractNowPageNumber(lang),lang)
                print("리뷰 내용을 구해오는 태그가 없어, 현재 페이지 수를 저장하고 프로그램을 종료합니다.")
                sys.exit()

        for tag in tags:
            ScrapingReview.review_data['content'].append(str(tag.text))
        return
    
    #관광지 방문 날짜
    def scrapVisitingDate(self,lang):
        self.refreshInstance()
        
        year = str()
        month = str()
        dateString = str()
        

        tag = self.chrome_instance.find_elements_by_css_selector("div.review-container > div > div.reviewSelector > div > div > div.prw_rup.prw_reviews_stay_date_hsx")
        if not tag:
            tag = self.chrome_instance.find_elements_by_css_selector("div.location-review-review-list-parts-ExpandableReview__containerStyles--1G0AE")
            if not tag:
                self.urlFlag(self.extractNowPageNumber(lang),lang)
                print("날짜를 구해오는 태그가 없어, 현재 페이지 수를 저장하고 프로그램을 종료합니다.")
                sys.exit()


        for tag_element in tag:
            try:
                tag_element = tag_element.find_element_by_css_selector("span.location-review-review-list-parts-EventDate__event_date--1epHa")
            except NoSuchElementException:
                try:
                    tag_temp = tag_element.find_element_by_css_selector("span.stay_date_label")
                except NoSuchElementException:
                    ScrapingReview.review_data['date'].append('null')
                    continue

            dateString = str(tag_element.text)

            regex = re.compile('(.*.)+(\d\d\d\d)')
            dateString = regex.search(dateString)
            year = dateString.group(2)
            

            if dateString.group(1) == "Date of experience: January " :
                month = '1'
            elif dateString.group(1) == "Date of experience: February " :
                month = '2'
            elif dateString.group(1) == "Date of experience: March " :
                month = '3'
            elif dateString.group(1) == "Date of experience: April " :
                month = '4'
            elif dateString.group(1) == "Date of experience: May " :
                month = '5'
            elif dateString.group(1) == "Date of experience: June " :
                month = '6'
            elif dateString.group(1) == "Date of experience: July " :
                month = '7'
            elif dateString.group(1) == "Date of experience: August " :
                month = '8'
            elif dateString.group(1) == "Date of experience: September " :
                month = '9'
            elif dateString.group(1) == "Date of experience: October " :
                month = '10'
            elif dateString.group(1) == "Date of experience: November " : 
                month = '11'
            elif dateString.group(1) == "Date of experience: December " : 
                month = '12'

            dateString = year+'/'+month
            ScrapingReview.review_data['date'].append(dateString)
        return

    #데이터 프레임에 인덱스 열 추가
    def setIndex(self, index):
        for i in range(0,len(ScrapingReview.review_data['content'])):
            ScrapingReview.review_data['index'].append(index)
        return

    #데이터 프레임에 언어 열 추가
    def setLanguage(self, lang):
        for i in range(0,len(ScrapingReview.review_data['content'])):
            ScrapingReview.review_data['lang'].append(lang)
        return

    #저장 함수 -> csv로 저장
    def savePlayReviewInCSVFormat(self):

        index = list()
        title = list()
        rating = list()
        content = list()
        date = list()
        lang = list()

        review_data_len = len(ScrapingReview.review_data['title'])

        for i in range(0, review_data_len):
            
            index.append(ScrapingReview.review_data['index'][i])
            title.append(ScrapingReview.review_data['title'][i])
            rating.append(ScrapingReview.review_data['rating'][i])
            content.append(ScrapingReview.review_data['content'][i])
            date.append(ScrapingReview.review_data['date'][i])
            lang.append(ScrapingReview.review_data['lang'][i])
            
        exData = pd.DataFrame()

        exData['index'] = index
        exData['title'] = title
        exData['rating'] = rating
        exData['title'] = title
        exData['content'] = content
        exData['date'] = date
        exData['lang'] = lang

        print(exData)#확인용

        try:
            filename = 'C:\\tripAdvisor\\{}\\{}\\Review\\pr_{}_{}.csv'.format(ScrapingReview.state,ScrapingReview.review_scrap_list['local'][index[0]],index[0],lang[0])  

            if os.path.isfile(filename):
                exData.to_csv(filename, mode='a', header=False, index=False)
            else:
                exData.to_csv(filename, index=False)
        except:

            self.urlFlag(self.extractNowPageNumber(lang),lang[0])
            print("파일을 저장하는 도중 오류가 발생해 현재 페이지 수를 저장하고 프로그램을 종료합니다 > try-except 구문을 풀고 오류를 확인해보기")
            sys.exit()
        
        return


    #리뷰의 더보기 버튼을 눌러주는 함수
    def clickMoreButton(self,lang):
        for e_count in range(1,self.EXCEPTION_COUNT):
            try:
                more_button = self.chrome_instance.find_elements_by_css_selector("div.ui_column.is-9 > div.prw_rup.prw_reviews_text_summary_hsx > div > p > span")
                if not more_button:
                    more_button = self.chrome_instance.find_elements_by_css_selector("#btf_wrap > div > div > div > div > div > div > div > div > div > div > div > span._36B4Vw6t > div > span")
                    if not more_button:
                        more_button = self.chrome_instance.find_elements_by_css_selector("span.location-review-review-list-parts-ExpandableReview__cta--2mR2g")
                        if not more_button:
                            print("더보기 버튼이 없음")
                            break

                self.chrome_instance.execute_script("arguments[0].click();",more_button[0])
                time.sleep(2)

                show_less = self.chrome_instance.find_elements_by_css_selector("div.ui_column.is-9 > div.prw_rup.prw_reviews_text_summary_hsx > div > span")
                if not show_less:
                    show_less = self.chrome_instance.find_elements_by_css_selector("#btf_wrap > div > div > div > div > div > div > div > div > div > div > div > span.hw66xH7d")
                    if not show_less :
                        show_less = self.chrome_instance.find_elements_by_css_selector("span.location-review-review-list-parts-ExpandableReview__ctaCollapse--TGOvo")
                        if not show_less:
                            print("더보기 버튼 안눌림 %d/6"%(e_count))
                            time.sleep(2)
                            continue
                
                
                break
            except NoSuchElementException:
                print("더보기 없음")
                self.urlFlag(self.extractNowPageNumber(lang),lang)
                #url플래그
            except StaleElementReferenceException:
                print("더보기 에러")
                self.urlFlag(self.extractNowPageNumber(lang),lang)
                #url플래그
            except IndexError:
                break
        
        return

    #언어 선택 부분에 있는 더보기버튼 (!=리뷰 더보기)
    def clickMoreLangButton(self, lang):
        self.refreshInstance()

        for e_count in range(1,self.EXCEPTION_COUNT):
            
            try:
                ul_box = self.chrome_instance.find_element_by_css_selector("div.is-3-tablet > ul.location-review-review-list-parts-ReviewFilter__filter_table--1H9KD")
            except NoSuchElementException:
                try:
                    ul_box = self.chrome_instance.find_element_by_css_selector("div > div.ui_columns.filters > div.prw_rup.prw_filters_detail_language.ui_column.separated.is-3 > div > div.content > div.choices")
                except:
                    print("ul_boxes의 selector 경로가 잘못되었습니다.")


            more_button = ul_box.find_elements_by_css_selector("div")
            if not more_button:
                print("더보기 없음")
                return

            div_len = len(more_button)
            if div_len >= 2:
                more_button = more_button[-1].find_elements_by_css_selector("span")

            self.chrome_instance.execute_script("arguments[0].click();", more_button[0])
            time.sleep(2)
            return

        return

    #뻑난곳 부터 다시 돌릴 때 페이지 스킵하는 함수
    def skipFlag(self, index, lang):
        now = str()
        now_page = int()
        page_num = 0

        #파일 있는지 확인
        filename = 'C:\\tripAdvisor\\{}\\{}\\url_flag_{}_{}.txt'.format(ScrapingReview.state,ScrapingReview.review_scrap_list['local'][index],index,lang)
        
        if os.path.isfile(filename):
            print("url_flag_{}_{}.txt 파일 존재".format(index,lang))
            f = open("C:\\tripAdvisor\\{}\\{}\\url_flag_{}_{}.txt".format(ScrapingReview.state,ScrapingReview.review_scrap_list['local'][index],index,lang),'r')
            numbers = f.readlines()
            page_num = int(numbers[-1])
            print(page_num)
            f.close()

        #url로 읽어온게 없으면 == 처음 돌리는거면
        if (page_num == 0) :
            return 0

        for i in range(1,page_num):
            for e_count in range(1, self.EXCEPTION_COUNT):
                try:
                    css_next_tags = self.chrome_instance.find_elements_by_css_selector("div > div > div > div > a.next")
                    if css_next_tags and css_next_tags[0]:
                        self.chrome_instance.execute_script("arguments[0].click();", css_next_tags[0]) # 클릭
                        time.sleep(2)

                        if self.extractNowPageNumber(lang) != (i + 1):
                            print("중복된 페이지")
                            self.chrome_instance.get(self.chrome_instance.current_url)
                            time.sleep(2)
                            self.chrome_instance.refresh()
                            continue
                    break
                except NoSuchElementException:
                    print("다음 버튼 중 요소 에외")# 로그로 대체 프린트 말고
                except StaleElementReferenceException:
                    print("다음 버튼 중 참조 예외")# 로그로 대체 프린트 말고
                    self.refreshInstance(True)
            print("현재 페이지 : %d"%(self.extractNowPageNumber(lang)))

        return (page_num-1)

    #오류난 페이지 text로 log 남기는 함수
    def urlFlag(self,now_page_number,lang):
        filedir = "C:\\tripAdvisor\\{}\\{}\\url_flag_{}_{}.txt".format(ScrapingReview.state,ScrapingReview.review_scrap_list['local'][ScrapingReview.temp_index],ScrapingReview.temp_index,lang)
        with open(filedir,"a") as f:
            f.write("\n"+str(now_page_number))
        
            

if __name__ == "__main__":

    scrap = ScrapingReview()
    scrap.startScraping()