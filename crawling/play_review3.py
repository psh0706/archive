#!/usr/bin/env python
# coding: utf-8

# Selenium
from selenium import webdriver as Webd
from selenium.webdriver import ActionChains as AC # More, Click 
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException # Exception
from selenium.webdriver.common.keys import Keys
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


class ScrapingReview(Strapy):

    review_scrap_list = {
        'index' : [],
        'url' : [],
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

        for i in range(0,self.review_scrap_list['len']):
            if int(self.review_scrap_list['scrap_flag'][i]) != 0: #1이면 스크래핑 완료니깐
                print("%s 는 이미 스크랩 되었으므로 이대로 이렇게 넘어갑니다!"%(self.review_scrap_list['url'][i]))
                continue #다음 인수로 넘기기
            
            print("영어 리뷰 스크래핑을 시작합니다.")
            try:
                self.scrapReview(self.review_scrap_list['index'][i], self.review_scrap_list['url'][i],"en")#영어
                print("영어 리뷰 스크래핑이 끝났습니다.")
            except:
                print("영어 리뷰가 없습니다.")
            
            
            print("한국어 리뷰 스크래핑을 시작합니다.")
            try:
                self.scrapReview(self.review_scrap_list['index'][i], self.review_scrap_list['url'][i],"ko")#한국어 둘다 돌림
                print("한국어 리뷰 스크래핑이 끝났습니다.")
            except:
                print("한국어 리뷰가 없습니다.")
            

            self.scrap_flag(i)
            print("리뷰 스크래핑이 완료 되었습니다.")
        return

    def loadPlayReviewList(self):
        try: 
            play_review_list_pdata = pd.read_csv("play_review_list.csv", sep=",")
        except FileNotFoundError: # 파일이 없을 경우에는 그냥 첫 출력을 하면 됨.
            pass


        else: 
            self.review_scrap_list['len'] = int(play_review_list_pdata.shape[0])
            for i in range(0,self.review_scrap_list['len']):#읽어야 하는 것들을 함수호출해서 저장한 것 / 개수만큼 for문 돌리기
                self.review_scrap_list['index'].append(int(play_review_list_pdata.at[i,'index']))
                self.review_scrap_list['url'].append(str(play_review_list_pdata.at[i,'url']))
                self.review_scrap_list['scrap_flag'].append(int(play_review_list_pdata.at[i,'scrap_flag']))
        return
    
    def scrap_flag(self,index):
        try:
            play_reivews_pdata = pd.read_csv("play_review_list.csv", sep=",")
        except FileNotFoundError:
            pass
        else:
            play_reivews_pdata['scrap_flag'][index] = 1
            play_reivews_pdata.to_csv("play_review_list.csv", index=False)

    def scrapReview(self, index, url, lang): # def loadWebDriver(self, headless, target_url, chrome_driver_path):def refreshInstance(self, page_refresh = False):
        
        start_page_number = 0
        now_page_number = 0
        last_page_number = 0

        print("현재 페이지 : %s / %s"%(url,lang))
        #여기서부터 웹드라이버 로드
        self.loadWebDriver(False, url, "chromedriver.exe")
        
        self.selectLanguage(lang)
        self.refreshInstance(True)
        #selectLanguage 한 후 풀릴수도 있음 그거에 대해서 예외처리 풀리면 > false (종목별로)

        last_page_number = self.extractLastPageNumber()
        start_page_number = self.extractNowPageNumber()#중복 계산 하려고... 중복 페이지 처리
        
        print(last_page_number)
        print(start_page_number)

        start_page_number = self.Skip(index,lang)

        for now_page_number in range(start_page_number, last_page_number+1):
            
            
            self.scrapRating()
            self.scrapTitle()
            self.scrapContent()
            self.scrapVisitingDate()
            self.setLanguage(lang)
            self.setIndex(index)
            #스크래핑   
        
            self.savePlayReviewInCSVFormat()

            #비우기 중복저장 피하려고 / 저장 후 clear
            self.review_data['index'].clear()
            self.review_data['title'].clear()
            self.review_data['rating'].clear()
            self.review_data['content'].clear()
            self.review_data['date'].clear()
            self.review_data['lang'].clear()
            
            self.clickNextButton(now_page_number)

            print("다음 눌렀습니다. 현재 페이지 : %d"%(self.extractNowPageNumber()))
            
            time.sleep(3)

        
        


        # div.page > #MAIN > #btf_wrap li.ui_radio.hotels-review-list-parts-ReviewFilter__filter_row--2sfwt > input -> 이 속성 중 value ko, en 인풋 태그를 클릭하면 됨.

        # div.page > #MAIN > #btf_wrap div.ui_pagination.is-centered > div.pageNumbers > span.pageNum.current.disabled -> 현재 페이지
        # div.page > #MAIN > #btf_wrap div.ui_pagination.is-centered > div.pageNumbers > a.pageNum -> 페이지 넘버들, 리스트의 -1 번째가 끝 페이지.
        # div.page > #MAIN > #btf_wrap div.ui_pagination.is-centered > span.ui_button.nav.next.primary -> 다음 버튼
        # div.page > #MAIN > #btf_wrap div.ui_pagination.is-centered > span.ui_button.nav.next.primary.disabled -> 끝 페이지에서의 다음 버튼
      


        self.exitChromeDriver()
        return
    
    #클릭이라 동적인것으로.. 
    def selectLanguage(self, lang):
        # 언어 선택
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                time.sleep(1)
                css_language_tags = self.chrome_instance.find_elements_by_css_selector("div > div > label.label.container > input[type=radio]")
            
                for element in css_language_tags:
                    selected_lang = element.get_attribute("value")
                    if selected_lang == lang:
                        self.chrome_instance.execute_script("arguments[0].click();", element) # 클릭 매개변수 lang과 같은거 
                        time.sleep(1)
                break
            except NoSuchElementException:
                self.log("언어 선택 중 요소 예외")
            except StaleElementReferenceException:
                self.log("언어 선택 중 참조 예외")
                self.refreshInstance(True)
        return 
    
    def extractLastPageNumber(self):
        # 마지막 페이지 
        last_page_number = 0
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                css_last_page_number_tag = self.chrome_instance.find_elements_by_css_selector("div.mobile-more > div > div > div.pageNumbers > a")
                #btf_wrap 다음 스페이스 공간 때문에 셀레니움을 씀.
                print(css_last_page_number_tag[-1].text)
                last_page_number = int(css_last_page_number_tag[-1].text)

                break
            except NoSuchElementException:
                print("마지막 페이지  중 요소 에외")
            except StaleElementReferenceException:
                print("마지막 페이지  중 참조 예외")
                self.refreshInstance(True)
    
        return last_page_number
    
    def extractNowPageNumber(self):
        # 현재 
        self.refreshInstance()
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                css_now_page_number_tag = self.bs.select("div.mobile-more> div > div > div >a.pageNum.current")
                if not css_now_page_number_tag:
                    css_now_page_number_tag = self.bs.select("#taplc_location_reviews_list_resp_ar_responsive_0 > div > div > div > div > div > a.pageNum.last.current")
                    
                now_page_number = int(css_now_page_number_tag[0].text)
                break
            except NoSuchElementException:
                print("현재 페이지  중 요소 에외")
            except StaleElementReferenceException:
                print("현재 페이지  중 참조 예외")
                self.refreshInstance(True)
        
        return now_page_number
    
    def clickNextButton(self, prev_page_number):
        #flag처리 해 주어야 함.. 10페이지마다. 저장하는 부분에 해주면 될 듯..?
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                css_next_tags = self.chrome_instance.find_elements_by_css_selector("div.mobile-more>div > div.unified.ui_pagination > a.nav.next.taLnk.ui_button.primary")
                if css_next_tags and css_next_tags[0]:
                    self.chrome_instance.execute_script("arguments[0].click();", css_next_tags[0]) # 클릭
                    self.refreshInstance()
                    time.sleep(2)
                if self.extractNowPageNumber() != (prev_page_number + 1):
                    print("중복이다 이놈아!!@@{}").format(e_count)
                    self.chrome_instance.refresh()
                    try:
                        click_button = WebDriverWait(driver, wait_time).until(
                            ec.presence_of_element_located(
                                (By.CSS_SELECTOR, 'div.ui_column.is-9 > '
                                                'div.prw_rup.prw_reviews_text_summary_hsx > div > p > span')))
                    except TimeoutException:
                        req = driver.page_source
                        soup = BeautifulSoup(req, 'html.parser')
                        hide_button = soup.select('div.ui_column.is-9 > div.prw_rup.prw_reviews_text_summary_hsx > div > span')
                        if hide_button:
                            driver.refresh()
                            print('더 보기는 눌렀는데, 페이지가 안넘어가네요 :(')
                            click_next_button()
                            lang_check()
                            click_more_button()
                        else:
                            print('더 보기 버튼이 없습니다.')
                    else:
                        driver.execute_script('arguments[0].click();', click_button)
                        time.sleep(5)
                        try:
                            more_button_tmp = click_button.get_attribute('onclick')
                        except StaleElementReferenceException:
                            return
                        else:
                            if str(more_button_tmp).find('clickExpand') != -1 and \
                                    str(more_button_tmp).find('unabbreviateContent') == -1:
                                print('더 보기 버튼이 제대로 눌리지 않았습니다. 다시 실행합니다.')
                                driver.refresh()  # 새로고침
                                time.sleep(5)
                                click_more_button()
                                continue
    
                break
            except NoSuchElementException:
                print("다음 버튼 중 요소 에외")# 로그로 대체 프린트 말고
            except StaleElementReferenceException:
                print("다음 버튼 중 참조 예외")# 로그로 대체 프린트 말고
                self.refreshInstance(True)

        return 

    def scrapRating(self):
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                tag = self.chrome_instance.find_elements_by_css_selector("div.ui_column.is-9 > span.ui_bubble_rating")
                break
            except NoSuchElementException:
                print("언어 선택 중 요소 에외")
            except StaleElementReferenceException:
                print("언어 선택 중 참조 예외")    

        tag_len = len(tag)

        for i in range(0,tag_len):
            tag[i] = tag[i].get_attribute('class')
            self.review_data['rating'].append(self.extractRatingInString(str(tag[i])))

        return
    
    def scrapTitle(self):
        self.refreshInstance()
        tag = self.bs.select("div.ui_column.is-9 > div.quote > a > span")
        tag_len = len(tag)

        for i in range(0,tag_len):
            self.review_data['title'].append(str(tag[i].text))
        return
    
    def scrapContent(self):
        self.clickMoreButton()
        self.refreshInstance()

        tag = self.bs.select("div.ui_column.is-9 > div.prw_rup.prw_reviews_text_summary_hsx > div > p")
        tag_len = len(tag)

        for i in range(0,tag_len):
            self.review_data['content'].append(str(tag[i].text))
        return
    
    def scrapVisitingDate(self):
        self.refreshInstance()
        tag = self.bs.select("div>div.prw_rup.prw_reviews_stay_date_hsx")
        tag_len = len(tag)

        for i in range(0,tag_len):
            self.review_data['date'].append(self.getStringToNumber(str(tag[i].text)))
        return

    def setIndex(self, index):
        for i in range(0,len(self.review_data['content'])):
            self.review_data['index'].append(index)
        return

    def setLanguage(self, lang):
        for i in range(0,len(self.review_data['content'])):
            self.review_data['lang'].append(lang)
        return

    def savePlayReviewInCSVFormat(self):

        index = list()
        title = list()
        rating = list()
        content = list()
        date = list()
        lang = list()

        review_data_len = len(self.review_data['title'])
        for i in range(0, review_data_len):
            
            index.append(self.review_data['index'][i])
            title.append(self.review_data['title'][i])
            rating.append(self.review_data['rating'][i])
            content.append(self.review_data['content'][i])
            date.append(self.review_data['date'][i])
            lang.append(self.review_data['lang'][i])
            
        exData = pd.DataFrame()

        exData['index'] = index
        exData['title'] = title
        exData['rating'] = rating
        exData['title'] = title
        exData['content'] = content
        exData['date'] = date
        exData['lang'] = lang


        filename = 'pr_%d_%s.csv'%(index[0],lang[0])  

        if os.path.isfile(filename):
            exData.to_csv(filename, mode='a', header=False, index=False)
        else:
            exData.to_csv(filename, index=False)

            return

    def clickMoreButton(self):
        for e_count in range(1,self.EXCEPTION_COUNT):
            try:
                more_button = self.chrome_instance.find_elements_by_css_selector("div.ui_column.is-9 > div.prw_rup.prw_reviews_text_summary_hsx > div > p > span")
                if more_button is None:
                    break
                self.chrome_instance.execute_script("arguments[0].click();",more_button[0])
                time.sleep(1)
                break
            except NoSuchElementException:
                print("더보기 없음")
            except StaleElementReferenceException:
                print("더보기 에러")
            except IndexError:
                break
        
        return

    def Skip(self, index, lang):
        #파일 있는지 확인
        filename = 'pr_%d_%s.csv'%(index,lang)
        click_time = 0  

        print(lang)

        if os.path.isfile(filename):

            if(lang == 'en'):
                pr_csv = pd.read_csv(filename ,sep=',')
                click_time = int(int(pr_csv.shape[0])/10)+1
            if(lang == 'ko'):
                pr_csv = pd.read_csv(filename ,sep=',')
                pr_csv[pr_csv['lang'].isin(['ko'])]
                click_time = int(int(pr_csv.shape[0])/10)+1

            print("이미 긁어온 리뷰가 있으므로 %d 페이지 까지 넘어갑니다."%(click_time))
            print("다음 버튼을 누르기 시작합니다.")
            #10으로 나눈값 만큼 self.clickNextButton() for문돌리기
            for i in range(1,click_time):
                for e_count in range(1, self.EXCEPTION_COUNT):
                    try:
                        css_next_tags = self.chrome_instance.find_elements_by_css_selector("div.mobile-more>div > div.unified.ui_pagination > a.nav.next.taLnk.ui_button.primary")
                        if css_next_tags and css_next_tags[0]:
                            self.chrome_instance.execute_script("arguments[0].click();", css_next_tags[0]) # 클릭
                            time.sleep(2)

                            if self.extractNowPageNumber() != (i + 1):
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
                print("현재 페이지 : %d"%(self.extractNowPageNumber()))

        else:
            return 1
    
        print("(긁어온 것 까지 페이지 넘김)현재 페이지 %d 페이지"%(click_time))
        return click_time

if __name__ == "__main__":

    scrap = ScrapingReview()
    scrap.startScraping()