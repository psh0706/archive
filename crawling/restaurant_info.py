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
import os # 경로

# Module
from Strapy import Strapy 

# Global Area
# #

class ScrapingInfo(Strapy):

    # info
    name = 'NoName'
    all_fee = 'NoFee'
    address = 'NoAddress'
    call_number = 'NoCallNumber'
    rating_by_item = {
        '음식':None,
        '서비스':None,
        '가격':None,
        '분위기':None
    }
    restaurant_info = {
        '가격대':None,
        '요리':None,
        '특별식제공':None,
        '식사시간':None,
        '특징':None,
    }
    open = {
        'day':None,
        'time':None
    }
    avg_rating = 0

    # from url list  
    url_dict_struct = {
        'titles' : [],
        'count' : [],
        'urls' : [],
        'scrap_flag' : [],
        'list_len'  : 0
    }

    # 저장할 restaurant info value dict
    index_info_dict = { 
            '000_index': 0 , '001_상호명': ' ', '002_전체평점' : 0.0, '003_음식평점' : 0.0, 
            '004_서비스평점': 0.0, '005_가격평점': 0.0, '006_분위기평점': 0.0, '007_가격정도': ' ',
            '008_가격대': ' ', '009_요리': ' ', '010_특별식': ' ',	'011_식사시간': ' ', 
            '012_특징': ' ', '013_전화번호': ' ' , '014_영업일': ' ' , '015_영업시간': ' ', '016_주소': ' ', '017_위도': 0.0, '018_경도': 0.0
        }
    
    now_processing_index = 0
    

    def __init__(self, headless = None, target_url = None, chrome_driver_path = None):
        super().__init__(headless, target_url, chrome_driver_path)
        return

    def startScraping(self,number): # scraping을 시작하는 함수
        if self.scrapContents() == -1: 
            pass
        self.assignrestaurantInfoToValue() # assing to Variable
        self.saverestaurantInformationInCSVFormat(number)
        print("[Scraping] : 스크래핑이 완료 되었습니다.")
        return
    
    def assignrestaurantInfoToValue(self):
        
        self.index_info_dict = { 
            '000_index': 0 , '001_상호명': self.name, '002_전체평점' : self.avg_rating, 
            '003_음식평점' : self.rating_by_item['음식'] if self.rating_by_item.get('음식') is not None else 0,
            '004_서비스평점': self.rating_by_item['서비스'] if self.rating_by_item.get('서비스') is not None else 0, 
            '005_가격평점': self.rating_by_item['가격'] if self.rating_by_item.get('가격') is not None else 0, 
            '006_분위기평점': self.rating_by_item['분위기'] if self.rating_by_item.get('분위기') is not None else 0,
            '007_가격정도': self.all_fee, 
            '008_가격대': self.restaurant_info['가격대'] if self.restaurant_info.get('가격대') is not None else ' ',
            '009_요리': self.restaurant_info['요리'] if self.restaurant_info.get('요리') is not None else ' ', 
            '010_특별식': self.restaurant_info['특별식제공'] if self.restaurant_info.get('특별식제공') is not None else ' ', 
            '011_식사시간': self.restaurant_info['식사시간'] if self.restaurant_info.get('식사시간') is not None else ' ', 
            '012_특징': self.restaurant_info['특징'] if self.restaurant_info.get('특징') is not None else ' ', 
            '013_전화번호': self.call_number, 
            '014_영업일': self.open['day'] if self.open.get('day') is not None else ' ', 
            '015_영업시간': self.open['time'] if self.open.get('time') is not None else ' ', 
            '016_주소': self.address, '017_위도': 0.0, '018_경도': 0.0 
        }
        return

    def scrapContents(self):    #상호명,전체평점,부분평점,주소,전화번호,가격정도,가격대,요리,특별식,식사,특징//,영업시간
        self.refreshInstance()
        self.name = self.scrapTitle()   #상호명
        self.avg_rating = self.scrapAverageRating() #전체평점
        self.rating_by_item = self.scrapRatingByItem()  #부분평점
        self.address = self.scrapAddress()  #주소
        self.call_number = self.scrapCallNumber()   #전화번호
        self.all_fee = self.scrapRestaurantFee()    #가격정도
        self.restaurant_info = self.scrapRestaurantInformation()    #특징
        self.open = self.scrapHour()    #영업시간    

        if self.name == -1 or self.avg_rating == -1 or self.address == -1 or self.call_number == -1 or self.all_fee == -1 or self.rating_by_item == -1 or self.restaurant_info == -1 or self.open == -1:
            return -1
        
        return

    def scrapFile(self):

        self.file = os.listdir(r".\list")[0]
    
    def loadrestaurantList(self): # title,count,url,scrap_flag
        try: 
            data = pd.read_csv(r".\list\{}".format(self.file),encoding='utf-8', sep=",")
        except FileNotFoundError:
            print("주소 정보 파일이 없습니다!")
            exit()
        else:
            self.url_dict_struct['list_len'] = len(data.index)

            for i in range(0, self.url_dict_struct['list_len']):
                self.url_dict_struct['titles'].append(str(data.at[i,'title']))
                self.url_dict_struct['count'].append(int(data.at[i,'count']))
                self.url_dict_struct['urls'].append(self.default_address + str(data.at[i,'url']))
                self.url_dict_struct['scrap_flag'].append(int(data.at[i,'scrap_flag']))

        return self.url_dict_struct

    def saverestaurantInformationInCSVFormat(self,number):
        try: 
            restaurant_scraped_list_pdata = pd.read_csv(r".\info\restaurant_scraped_list.csv",encoding='utf-8', sep=",")
            self.now_processing_index = int(restaurant_scraped_list_pdata.shape[0])
            self.index_info_dict['000_index'] = self.now_processing_index

        except FileNotFoundError: # 파일이 없을 경우에는 그냥 첫 출력을 하면 됨.
            exData1 = pd.DataFrame([self.index_info_dict])
            exData1.to_csv(r".\info\restaurant_scraped_list.csv",encoding='utf-8', index=False)
            print("restaurant_scraped_list.csv 파일이 존재하지 않으므로 새로 생성하여 저장합니다.")

        else: # 파일이 있을 경우에는 다 읽어들인 후 끝에 추가하는 형태로 진행해야함.
            restaurant_scraped_list_pdata.loc[self.now_processing_index] = self.index_info_dict
            restaurant_scraped_list_pdata.to_csv(r".\info\restaurant_scraped_list.csv",encoding='utf-8', index=False)
            print("restaurant_scraped_list.csv의 끝에 저장합니다.")
        

        try:
            restaurant_urls_pdata = pd.read_csv(r".\list\{}".format(self.file),encoding='utf-8', sep=",")
        except FileNotFoundError:
            pass
        else:
            restaurant_urls_pdata.iloc[number,-1] = 1
            restaurant_urls_pdata.to_csv(r".\list\{}".format(self.file),encoding='utf-8', index=False)



        review_list_data_dict = {'index' : self.now_processing_index, 'url' : restaurant_urls_pdata.loc[self.now_processing_index,'url'], 'scrap_flag' : 0}

        try:
            restaurant_review_list_pdata = pd.read_csv(r".\info\restaurant_review_list.csv",encoding='utf-8', sep=",")
        except FileNotFoundError:
            exData2 = pd.DataFrame([review_list_data_dict])
            exData2.to_csv(r".\info\restaurant_review_list.csv",encoding='utf-8', index=False)
        else:
            restaurant_review_list_pdata.loc[self.now_processing_index] = review_list_data_dict
            restaurant_review_list_pdata.to_csv(r".\info\restaurant_review_list.csv",encoding='utf-8', index = False)

    def scrapTitle(self): # Target Name
        self.refreshInstance()
        tag = self.bs.select('h1.ui_header.h1') # title에 해당하는 태그를 받아옴.
        if not tag:
            return -1
        
        # Calender 제거를 위해 제목 태그를 클릭.
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                css_delete_calender = self.chrome_instance.find_element_by_css_selector("h1.ui_header.h1")
                self.chrome_instance.execute_script("arguments[0].click();", css_delete_calender) # 클릭
                break
            except NoSuchElementException:
                print("[Exception] : (#HEADING) 요소에 대한 NoSuchElementException 발생")
            except StaleElementReferenceException:
                print("[Exception] : (#HEADING) 요소에 대한 StaleElementReferenceException 발생")
                self.chrome_instance.refresh()
                self.chrome_instance.implicitly_wait(self.EXCEPTION_SLEEP)

        return self.returnElementTextsInLists(tag)
    
    def scrapAverageRating(self):
        self.refreshInstance()
        tag = self.bs.select('div.ratingContainer > a > div > span.ui_bubble_rating')[0]['class']
        if not tag:
            return -1

        reg = re.compile('bubble_\d+')
        _str = self.convertListToString(tag)
        reg_result = (str)((reg.findall(_str))[0])

        rating = (float)((re.findall("\d+",reg_result))[0]) * 0.1
        return rating
    
    def scrapRatingByItem(self):
        rating_dict = dict()
        self.refreshInstance()
        tag_rating = self.bs.select("span.restaurants-detail-overview-cards-RatingsOverviewCard__ratingBubbles--1kQYC > span.ui_bubble_rating")
        tag_item = self.bs.select("span.restaurants-detail-overview-cards-RatingsOverviewCard__ratingText--1P1Lq")
        if not tag_rating or not tag_item:
            return rating_dict

        rating_count = len(tag_rating)

        for i in range(0, rating_count):
            rating_dict[tag_item[i].text.replace(' ','')] = self.extractRatingInString(str(tag_rating[i]['class'])) # star_\d+

        return rating_dict

    def scrapAddress(self):
        self.refreshInstance()
        tag_addr = self.bs.select("div.is-hidden-mobile.blEntry.address.ui_link")
        if not tag_addr:
            return -1

        return str(tag_addr[0].text)

    def scrapCallNumber(self):
        self.refreshInstance()
        tag_ph = self.bs.select("span.detail.is-hidden-mobile")
        if not tag_ph:
            return -1
        
        return str(tag_ph[0].text)

    def scrapRestaurantFee(self):
        self.refreshInstance()
        tag = self.bs.select("div.header_links")
        
        if not tag:
            return -1

        tag = tag[0].text
        return tag.split(',')[0]
     
    def scrapRestaurantInformation(self):
        info_dict = dict()
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                button = self.chrome_instance.find_element_by_css_selector('a.restaurants-detail-overview-cards-DetailsSectionOverviewCard__viewDetails--ule3z')
                self.chrome_instance.execute_script("arguments[0].click();", button)
                break
            except NoSuchElementException:
                print("[Exception] : (#HEADING) 요소에 대한 NoSuchElementException 발생")
            except StaleElementReferenceException:
                print("[Exception] : (#HEADING) 요소에 대한 StaleElementReferenceException 발생")
                self.chrome_instance.refresh()
                self.chrome_instance.implicitly_wait(self.EXCEPTION_SLEEP)
        
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                info_title = self.chrome_instance.find_elements_by_css_selector('div.ui_column > div > div > div.restaurants-detail-overview-cards-DetailsSectionOverviewCard__categoryTitle--2RJP_')
                info_content = self.chrome_instance.find_elements_by_css_selector('div.ui_column > div > div > div.restaurants-detail-overview-cards-DetailsSectionOverviewCard__tagText--1OH6h')
                break
            except NoSuchElementException:
                print("[Exception] : (#HEADING) 요소에 대한 NoSuchElementException 발생")
            except StaleElementReferenceException:
                print("[Exception] : (#HEADING) 요소에 대한 StaleElementReferenceException 발생")
                self.chrome_instance.refresh()
                self.chrome_instance.implicitly_wait(self.EXCEPTION_SLEEP)
        
        if not info_title or not info_content:
            return info_dict

        info_count = len(info_title)

        for i in range(0, info_count):
            info_dict[info_title[i].text.replace(' ','')] = info_content[i].text
        
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                button = self.chrome_instance.find_element_by_css_selector('div.overlays-pieces-CloseX__close--7erra')
                self.chrome_instance.execute_script("arguments[0].click();", button)
                break
            except NoSuchElementException:
                print("[Exception] : (#HEADING) 요소에 대한 NoSuchElementException 발생")
            except StaleElementReferenceException:
                print("[Exception] : (#HEADING) 요소에 대한 StaleElementReferenceException 발생")
                self.chrome_instance.refresh()
                self.chrome_instance.implicitly_wait(self.EXCEPTION_SLEEP)
        
        return info_dict

    def scrapHour(self):
        open_dict = dict()
        self.refreshInstance()
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                button = self.chrome_instance.find_element_by_css_selector('div.public-location-hours-LocationHours__hoursOpenerContainer---ULd_.ui_link')
                self.chrome_instance.execute_script("arguments[0].click();", button)
                break
            except NoSuchElementException:
                print("[Exception] : (#HEADING) 요소에 대한 NoSuchElementException 발생")
            except StaleElementReferenceException:
                print("[Exception] : (#HEADING) 요소에 대한 StaleElementReferenceException 발생")
                self.chrome_instance.refresh()
                self.chrome_instance.implicitly_wait(self.EXCEPTION_SLEEP)
        
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                open_day = self.chrome_instance.find_elements_by_css_selector('div.public-location-hours-AllHoursList__daysAndTimesRow--2CcRX.ui_column.is-5')
                open_time = self.chrome_instance.find_elements_by_css_selector('div.public-location-hours-AllHoursList__daysAndTimesRow--2CcRX.ui_column.is-7')
                break
            except NoSuchElementException:
                print("[Exception] : (#HEADING) 요소에 대한 NoSuchElementException 발생")
            except StaleElementReferenceException:
                print("[Exception] : (#HEADING) 요소에 대한 StaleElementReferenceException 발생")
                self.chrome_instance.refresh()
                self.chrome_instance.implicitly_wait(self.EXCEPTION_SLEEP)

        if not open_day or not open_time:
            return open_dict

        open_count = len(open_day)

        for i in range(0, open_count):
            open_day[i] = open_day[i].text
            open_time[i] = open_time[i].text

        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                button = self.chrome_instance.find_element_by_css_selector('div.overlays-popover-PopoverX__close--AKUEu')
                self.chrome_instance.execute_script("arguments[0].click();", button)
                break
            except NoSuchElementException:
                print("[Exception] : (#HEADING) 요소에 대한 NoSuchElementException 발생")
            except StaleElementReferenceException:
                print("[Exception] : (#HEADING) 요소에 대한 StaleElementReferenceException 발생")
                self.chrome_instance.refresh()
                self.chrome_instance.implicitly_wait(self.EXCEPTION_SLEEP)
        
        open_dict['day'] = open_day
        open_dict['time'] = open_time

        return open_dict



if __name__ == "__main__":

    scrap = ScrapingInfo()
    scrap.scrapFile()
    url_struct = scrap.loadrestaurantList()

    for i in range(0, url_struct['list_len']):
        if int(url_struct['scrap_flag'][i]) == 0 and int(url_struct['count'][i] > 20):
            scrap.loadWebDriver(False, url_struct['urls'][i], "chromedriver.exe")
            time.sleep(3)
            if scrap.startScraping(i) == -1:
                pass
            scrap.exitChromeDriver()
            print("스크랩 하나가 끝남.")


    





