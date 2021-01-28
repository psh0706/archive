#!/usr/bin/env python
# coding: utf-8

# Selenium
from selenium import webdriver as Webd
from selenium.webdriver import ActionChains as AC # More, Click 
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException # Exception
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# BeautifulSoup_4
from bs4 import BeautifulSoup

# ETC
import time # Sleep, Break 
import pandas as pd # DataFrame
import re # 정규 표현식

# Module
from Strapy import Strapy 

# Global Area
# #

class ScrapingList(Strapy):

    name_list = list()
    review_count_list = list()
    url_list = list()
    
    def __init__(self, headless = None, target_url = None, chrome_driver_path = None):
        super().__init__(headless, target_url, chrome_driver_path)
        return None

    def startScraping(self): # scraping을 시작하는 함수
        #완료 = -zfg9900(커피,차) -zfg16556(간단음식점) -zfg9909(디저트) -zfg10591(음식점) -zfg16548(전문식품시장) zfg9901(베이커리) -zfg11776(바&펍 음식점)
        self.url_filter = ['-zfg9900','-zfg16556','-zfg9909','-zfg10591','-zfg16548','zfg9901','-zfg11776']
        for url in self.url_filter:
            self.loadWebDriver(False, "https://www.tripadvisor.co.kr/Restaurants-g1120384{}-Rikubetsu_cho_Ashoro_gun_Hokkaido.html".format(url), "chromedriver.exe")
            self.wait = WebDriverWait(self.chrome_instance,30)
            self.chrome_instance.set_script_timeout(300)
            time.sleep(2)        
            self.refreshInstance()
            self.list_title = self.scrapTitle() # 타이틀 받아오기.
            self.list_endpage_number = self.scrapEndPageNumber() # 페이지 끝 번호 파악.
            print("[%s]의 (%d) 리스트 확인!"%(self.list_title, self.list_endpage_number))
            self.exitChromeDriver()
            # 리스트의 내용을 받아오는 작업이 시작됨.
            for i in range(0,self.list_endpage_number):
                self.page_filter = '-oa{}'.format(i * 30)
                self.all_filter = url + self.page_filter
                self.loadWebDriver(False,"https://www.tripadvisor.co.kr/Restaurants-g1120384{}-Rikubetsu_cho_Ashoro_gun_Hokkaido.html".format(self.all_filter),"chromedriver")
                time.sleep(2)
                self.refreshInstance()
                self.scrapContents(i) # 내용 받아오기
                self.exitChromeDriver()

        return
 
    def saveToCSV(self, local_title, page_number):
        ex = pd.DataFrame()

        ex['title'] = self.name_list
        ex['count'] = self.review_count_list
        ex['url'] = self.url_list
        ex['scrap_flag'] = 0

        if (page_number - 1) == 1:
            ex.to_csv(r'C:\Users\AI\Desktop\훗카이도\리쿠베쓰정\list\restaurant_urls_{}.csv'.format(local_title), index=False, encoding='utf-8')
        else:
            ex.to_csv(r'C:\Users\AI\Desktop\훗카이도\리쿠베쓰정\list\restaurant_urls_{}.csv'.format(local_title), mode='a', header=False, index=False, encoding='utf-8')

    def scrapTitle(self): # 리스트의 제목 받아오기

        titles = self.bs.select('h1#HEADING') # title에 해당하는 태그를 받아옴.

        return self.returnElementTextsInLists(titles)
    
    def scrapEndPageNumber(self):
        try:
            end_page_tags = self.bs.select('#EATERY_LIST_CONTENTS > div > div > div > a.pageNum.taLnk') # title에 해당하는 태그를 받아옴.
            return (int)(end_page_tags[-1].text)
        except IndexError:
            return 1

    def scrapContents(self,now_page):

        page_box_tags = self.bs.select("div.restaurants-list-ListCell__infoWrapper--3agHz")

        l_len = len(page_box_tags)
        for i in range (0, l_len):
            review_tag = page_box_tags[i].select_one("span.restaurants-list-ListCell__userReviewCount--2a61M")
            title_tag = page_box_tags[i].select_one("a.restaurants-list-ListCell__restaurantName--2aSdo")
            title = title_tag.text.strip('\n')

            if review_tag is None:
                review_tag = 0
            else:
                review_tag = self.getStringToNumber(review_tag.text)
                    
            self.name_list.append(title)
            self.url_list.append(title_tag.get('href'))
            self.review_count_list.append(review_tag)

            print("[{}] : {} / {} / {} ".format(i+1,self.name_list[-1], self.url_list[-1], self.review_count_list[-1]))

        if len(self.name_list) == 0 :
            return
        self.saveToCSV(self.list_title,i) # 저장 함수 호출
                    
        del self.name_list[:] 
        del self.url_list[:]
        del self.review_count_list[:]

        print("[Scraping] : 스크래핑이 완료 되었습니다. 전체페이지:{0} 현재페이지:{1}".format(self.list_endpage_number,now_page+1))
        return
 

if __name__ == "__main__":

    scrap = ScrapingList()
    scrap.startScraping()
    time.sleep(3)
    scrap.exitChromeDriver()
    





