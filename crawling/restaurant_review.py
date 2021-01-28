#!/usr/bin/env python
# coding: utf-8

# Selenium
from selenium import webdriver as Webd
from selenium.webdriver import ActionChains as AC # More, Click 
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException # Exception

# BeautifulSoup_4
from bs4 import BeautifulSoup

# ETC
import time # Sleep, Break 
import pandas as pd # DataFrame
import re # 정규 표현식
import os

# Module
from Strapy import Strapy 


class ScrapingReview(Strapy):

    review_scrap_list = {
        'index' : [],
        'url' : [],
        'scrap_flag' : [],
        'len' : 0
    }

    review_data = {
        'index' : [],
        'title' : [],
        'rating' : [],
        'content' : [],
        'date' : [],
        'lang' : []
    }
    


    def __init__(self, headless = None, target_url = None, chrome_driver_path = None):
        super().__init__(headless, target_url, chrome_driver_path)
        return

    def startScraping(self): # scraping을 시작하는 함수
        self.scrapContents()
        self.log("[Scraping] : 스크래핑이 완료 되었습니다.")
        return

    def scrapContents(self):      
        self.loadrestaurantReviewList()  

        for i in range(0,self.review_scrap_list['len']):
            if int(self.review_scrap_list['scrap_flag'][i]) != 0:
                continue
            self.scrapReview(self.review_scrap_list['index'][i], self.review_scrap_list['url'][i],"en")
            self.scrapReview(self.review_scrap_list['index'][i], self.review_scrap_list['url'][i],"ko")
            self.scrap_flag(i)
        return

    def loadrestaurantReviewList(self):
        try: 
            restaurant_review_list_pdata = pd.read_csv("restaurant_review_list.csv", sep=",")
        except FileNotFoundError:
            pass

        else: # 파일이 있을 경우에는 다 읽어들인 후 끝에 추가하는 형태로 진행해야함.
            self.review_scrap_list['len'] = int(restaurant_review_list_pdata.shape[0])

            for i in range(0,self.review_scrap_list['len']):
                self.review_scrap_list['index'].append(int(restaurant_review_list_pdata.at[i,'index']))
                self.review_scrap_list['url'].append(str(restaurant_review_list_pdata.at[i,'url']))
                self.review_scrap_list['scrap_flag'].append(int(restaurant_review_list_pdata.at[i,'scrap_flag']))
        return
    
    def scrapReview(self, index, url, lang): # def loadWebDriver(self, headless, target_url, chrome_driver_path):def refreshInstance(self, page_refresh = False):
        
        start_page_number = 0
        now_page_number = 0
        last_page_number = 0

        

        self.loadWebDriver(False, url, "../chromedriver")
        self.selectLanguage(lang)
        self.refreshInstance()
        time.sleep(1)
        self.clickmoreButton()
        last_page_number = self.extractLastPageNumber()
        start_page_number = self.extractNowPageNumber()
        
        print('시작페이지 :',start_page_number, '끝페이지 :',last_page_number)

        for now_page_number in range(start_page_number, last_page_number):
            self.scrapRating()
            self.scrapTitle()
            self.scrapContent()
            self.scrapVisitingDate()
            self.setIndex(index)
            self.setLanguage(lang)          
            
            self.clickNextButton(now_page_number)
            print("다음 눌렀습니다. 현재 페이지 : %d"%(self.extractNowPageNumber()))
            self.clickmoreButton()
            time.sleep(1)
        
        self.exitChromeDriver()
        return
    
    def selectLanguage(self, lang):
        # 언어 선택
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                css_language_tags = self.chrome_instance.find_elements_by_css_selector("div.content > div > div > label.label.container > input[type=radio]")
                check = self.chrome_instance.find_elements_by_css_selector("span.checkmark")
                for element in css_language_tags:
                    selected_lang = element.get_attribute("value")
                    if selected_lang == lang:
                        self.chrome_instance.execute_script("arguments[0].click();", element) # 클릭
                        time.sleep(1)
                for i in range(0,len(check)):
                    check[i] = check[i].text
                if check == lang:
                    break
                else:
                    continue
            except NoSuchElementException:
                self.log("언어 선택 중 요소 에외")
            except StaleElementReferenceException:
                self.log("언어 선택 중 참조 예외")
  
        return 

    def clickmoreButton(self):
        #더보기 버튼클릭
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                more_button = self.chrome_instance.find_elements_by_css_selector("span.taLnk.ulBlueLinks")
                self.chrome_instance.execute_script("arguments[0].click();", more_button[0]) #더보기클릭
                time.sleep(1)
                break
            except NoSuchElementException:
                self.log("더보기 없음")
            except StaleElementReferenceException:
                self.log("더보기 에러")
            except IndexError:
                break
        return
    
    def extractNowPageNumber(self):
        # 현재 
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                now_page_number = self.chrome_instance.find_element_by_css_selector("div.prw_rup.prw_common_responsive_pagination > div > div.pageNumbers > a[class~=current]")
                break
            except NoSuchElementException:
                self.log("현재 페이지  중 요소 에외")
            except StaleElementReferenceException:
                self.log("현재 페이지  중 참조 예외")
        return int(now_page_number.text)

    def extractLastPageNumber(self):
        # 마지막 페이지 
        last_page_number = 0
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                last_page_number = self.chrome_instance.find_element_by_css_selector("div.prw_rup.prw_common_responsive_pagination > div > div.pageNumbers > a[class~=last]")
                break
            except NoSuchElementException:
                self.log("마지막 페이지  중 요소 에외")
            except StaleElementReferenceException:
                self.log("마지막 페이지  중 참조 예외")
        
        return int(last_page_number.text)
    
    def clickNextButton(self, prev_page_number):
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                next_button = self.chrome_instance.find_element_by_css_selector("div.prw_rup.prw_common_responsive_pagination > div > a.nav.next.taLnk.ui_button.primary")
                self.chrome_instance.execute_script("arguments[0].click();", next_button) # 클릭
                time.sleep(2)

                if self.extractNowPageNumber() != (prev_page_number + 1):
                    self.chrome_instance.refresh()
                    continue
                
                # save and clear
                self.saverestaurantReviewInCSVFormat()
                self.review_data['index'].clear()
                self.review_data['content'].clear()
                self.review_data['title'].clear()
                self.review_data['date'].clear()
                self.review_data['rating'].clear()
                self.review_data['lang'].clear()
                break
            except NoSuchElementException:
                self.log("다음 버튼 중 요소 에외")
            except StaleElementReferenceException:
                self.log("다음 버튼 중 참조 예외")

        return

    def scrapRating(self):
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                tag = self.chrome_instance.find_elements_by_css_selector("div.ui_column.is-9 > span.ui_bubble_rating")
                break
            except NoSuchElementException:
                self.log("언어 선택 중 요소 에외")
            except StaleElementReferenceException:
                self.log("언어 선택 중 참조 예외")    

        tag_len = len(tag)

        for i in range(0,tag_len):
            tag[i] = tag[i].get_attribute('class')
            self.review_data['rating'].append(self.extractRatingInString(str(tag[i])))

        return
    
    def scrapTitle(self):
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                tag = self.chrome_instance.find_elements_by_css_selector("span.noQuotes")
                break
            except NoSuchElementException:
                self.log("언어 선택 중 요소 에외")
            except StaleElementReferenceException:
                self.log("언어 선택 중 참조 예외")    

        tag_len = len(tag)

        for i in range(0,tag_len):
            self.review_data['title'].append(str(tag[i].text))
        return
    
    def scrapContent(self):
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                tag = self.chrome_instance.find_elements_by_css_selector("div.review-container")
                break
            except NoSuchElementException:
                self.log("현재 페이지  중 요소 에외")
            except StaleElementReferenceException:
                self.log("현재 페이지  중 참조 예외")
        tag_len = len(tag)
        for i in range(tag_len):
            tag[i] = tag[i].find_elements_by_css_selector('p.partial_entry')[0].text
            tag[i] = ' '.join(tag[i].split('\n'))
            self.review_data['content'].append(str(tag[i]))
        return
    
    def scrapVisitingDate(self):
        tag = list()
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                container = self.chrome_instance.find_elements_by_css_selector("div.review-container > div > div > div > div.ui_column.is-9")
                break
            except NoSuchElementException:
                self.log("현재 페이지  중 요소 에외")
            except StaleElementReferenceException:
                self.log("현재 페이지  중 참조 예외")

        for i in range(0,len(container)):
            for e_count in range(1, self.EXCEPTION_COUNT):
                try:
                    tag.append(container[i].find_element_by_css_selector("div.ui_column.is-9 > div.prw_rup.prw_reviews_stay_date_hsx"))
                    date = tag[i].text.split()
                    tag[i] = date[2] + ' ' + date[3]
                    break
                except NoSuchElementException:
                    self.log("현재 페이지  중 요소 에외")
                except StaleElementReferenceException:
                    self.log("현재 페이지  중 참조 예외")
                except IndexError:
                    tag[i] = ' '
                    break

        tag_len = len(tag)

        for i in range(0,tag_len):
            self.review_data['date'].append(tag[i])
        return

    def setIndex(self, index):
        for i in range(0,len(self.review_data['content'])):
            self.review_data['index'].append(index)
        return

    def setLanguage(self, lang):
        for i in range(0,len(self.review_data['content'])):
            self.review_data['lang'].append(lang)
        return

    def saverestaurantReviewInCSVFormat(self):

        exData = pd.DataFrame(self.review_data)
            
        filename = 'restaurant_review_%d.csv'%(self.review_data['index'][0])  

        if os.path.isfile(filename):
            exData.to_csv('restaurant_review_%d.csv'%(self.review_data['index'][0]), mode='a', header=False, index=False)
            return
        else:
            exData.to_csv('restaurant_review_%d.csv'%(self.review_data['index'][0]), index=False)
            return
    
    def scrap_flag(self,index):
        try:
            restaurant_reivews_pdata = pd.read_csv("restaurant_review_list.csv", sep=",")
        except FileNotFoundError:
            pass
        else:
            restaurant_reivews_pdata['scrap_flag'][index] = 1
            restaurant_reivews_pdata.to_csv("restaurant_review_list.csv", index=False)

if __name__ == "__main__":

    scrap = ScrapingReview()
    scrap.startScraping()