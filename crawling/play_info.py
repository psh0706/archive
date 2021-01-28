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

# Module
from Strapy import Strapy 

# Global Area
# #
filename = "excite_urls_Alishan의 즐길거리.csv"

class ScrapingInfo(Strapy):

    # info
    name = 'NoName'
    avg_rating = 0.1
    address = 'NoAddress'
    call_number = 'NoCallNumber'
    opening_hours = list()
    recomend_time = 'NoInfromation'
    category = list()
    

    # from url list  호텔리스트로 스크래핑 한 것
    #정렬시키면 안됨!!!
    url_dict_struct = {
        'titles' : [],
        'urls' : [],
        'scrap_flag' : [],
        'list_len'  : 0
    }

    # 저장할 play info value dict
    index_info_dict = { 
            '000_index': 0 , '001_상호명': ' ', '002_평점' : 0.0, '003_영업시간' : ' ', 
            '004_추천방문시간': ' ', '005_카테고리': ' ','006_전화번호': ' ', '007_주소': ' ', 
            '008_위도': 0.0, '009_경도': 0.0 
        }
    
    now_processing_index = 0
    

    def __init__(self, headless = None, target_url = None, chrome_driver_path = None):
        super().__init__(headless, target_url, chrome_driver_path)
        return

    def startScraping(self): # scraping을 시작하는 함수
        
        self.scrapContents()
        self.assignPlayInfoToValue() # assing to Variable / scrapContents로 긁어온 정보들을 사전에 담는다.
        self.savePlayInformationInCSVFormat() #CSV format으로 저장
        print("[Scraping] : 스크래핑이 완료 되었습니다.")
        return

    def scrapContents(self):
        
        if self.scrapTitle() == -1 :
            self.name = None
        else:self.name = self.scrapTitle()
        if self.scrapAverageRating() == -1 :
            self.avg_rating = None
        else:self.avg_rating = self.scrapAverageRating()
        if self.scrapAddress() == -1:
            self.address = None
        else:self.address = self.scrapAddress()
        if self.scrapCallNumber() == -1:
            self.call_number = None
        else:self.call_number = self.scrapCallNumber()
        if self.scrapCategory() == -1:
            self.category = None
        else: self.category = self.scrapCategory()

        self.opening_hours, self.recomend_time = self.scrapTime()

        if self.opening_hours==-1:
            self.opening_hours = None
        else: pass
        if self.recomend_time==-1:
            self.recomend_time = None
        else: pass


        """
        #누락분이 있을경우 -1로 바꾸어 주어서 에러처리 // 원래 이렇게 에러처리 하면 안됌,,, 위에서 값을 받아올 때마다 예외처리를 해준당
        if self.name == -1 or self.avg_rating == -1 or self.address == -1 or self.call_number == -1 or self.category == -1 or self.opening_hours == -1 or self.recommend_time == -1:
            return -1
        """

        return
    
    def assignPlayInfoToValue(self): #초기화 개념
        
        self.index_info_dict = { 
            '000_index': 0 , '001_상호명': self.name, '002_평점' : self.avg_rating, 
            '003_영업시간': self.opening_hours, '004_추천방문시간': self.recomend_time, '005_카테고리': self.category, '006_전화번호': self.call_number, 
            '007_주소': self.address, '008_위도': 0.0, '009_경도': 0.0 
        }
        return

    def loadPlayList(self): # title,count,url,scrap_flag
        try: 
            data = pd.read_csv(filename, sep=",", encoding = 'utf-8')
        except FileNotFoundError:
            print("주소 정보 파일이 없습니다!")
            exit()
        else:
            self.url_dict_struct['list_len'] = len(data.index)#인덱스의 갯수를 list_len이라는 키값을 가진 딕셔너리에 넣음

            #삽입..
            for i in range(0, self.url_dict_struct['list_len']):
                self.url_dict_struct['titles'].append(str(data.at[i,'title']))
                self.url_dict_struct['urls'].append(str(data.at[i,'url']))
                self.url_dict_struct['scrap_flag'].append(str(data.at[i,'scrap_flag']))

        return self.url_dict_struct

    
    #csv로 저장
    def savePlayInformationInCSVFormat(self): 
        try: 
            play_scraped_list_pdata = pd.read_csv("play_scraped_list.csv", sep=",",encoding = 'utf-8')
            self.now_processing_index = int(play_scraped_list_pdata.shape[0])
            self.index_info_dict['000_index'] = self.now_processing_index

        except FileNotFoundError: # 파일이 없을 경우에는 그냥 첫 출력을 하면 됨.
            exData1 = pd.DataFrame([self.index_info_dict])
            exData1.to_csv("play_scraped_list.csv", index=False,encoding = 'utf-8')
            print("play_scraped_list.csv 파일이 존재하지 않으므로 새로 생성하여 저장합니다.")

        else: # 파일이 있을 경우에는 다 읽어들인 후 끝에 추가하는 형태로 진행해야함.
            play_scraped_list_pdata.loc[self.now_processing_index] = self.index_info_dict #저장할 것들을 play_scraped_listㅇㅔ 저장
            play_scraped_list_pdata.to_csv("play_scraped_list.csv", index=False,encoding = 'utf-8')
            print("play_scraped_list.csv의 끝에 저장합니다.")
        

        try:
            play_urls_pdata = pd.read_csv(filename, sep=",")
        except FileNotFoundError:
            pass
        else:
            play_urls_pdata.loc[self.now_processing_index,'scrap_flag'] = 1 #flag를 1로 바꿔주는 부분.
            play_urls_pdata.to_csv(filename, index=False,encoding = 'utf-8')



        review_list_data_dict = {'index' : self.now_processing_index, 'url' : play_urls_pdata.loc[self.now_processing_index,'url'], 'scrap_flag' : 0}
        #now_processing_index는 항상 최신의 인덱스를 가리킴, 리뷰 플래그를 0으로 셋팅, url로 저장
        try:
            play_review_list_pdata = pd.read_csv("play_review_list.csv", sep=",") #찐 저장
        except FileNotFoundError:
            exData2 = pd.DataFrame([review_list_data_dict])
            exData2.to_csv("play_review_list.csv", index=False)
        else:
            play_review_list_pdata.loc[self.now_processing_index] = review_list_data_dict
            play_review_list_pdata.to_csv("play_review_list.csv", index = False)


    def scrapTitle(self): # Target Name
        self.refreshInstance()
        tag = self.bs.select('#HEADING') # title에 해당하는 태그를 받아옴.

        if not tag:
            return -1

        return self.returnElementTextsInLists(tag)
    
    def scrapAverageRating(self):
        self.refreshInstance()
        tag = self.bs.select("div.section.rating > a.ui_bubble_rating")
        if not tag:
            tag = self.bs.select("div.attractions-supplier-profile-SupplierProfile__ratingsBox--2TKTR > div > span.ui_bubble_rating")
            if not tag:
                tag = self.bs.select("div.attractions-supplier-profile-SupplierProfile__ratingsBox--2TKTR > div > span.ui_bubble_rating")
                if not tag:
                    return -1

        reg = re.compile('bubble_\d+')
        _str = self.convertListToString(tag)
        reg_result = (str)((reg.findall(_str))[0])
        rating = (float)((re.findall("\d+",reg_result))[0]) * 0.1
        
        return rating
    
    def scrapAddress(self):
        self.refreshInstance()

        tag_addr = str("")

        #4개로 분할 된 주소 합치기
        #교통수단은 tag_locality 와 tag_country_name만 존재
        tag = self.bs.select("#taplc_location_detail_contact_card_ar_responsive_0 > div.contactInfo > div.detail_section.address > span > span:nth-child(2)")
        if not tag:
                return -1

        return str(tag[0].text)

    def scrapCallNumber(self):
        self.refreshInstance()
        tag = self.bs.select("span.attractions-contact-card-ContactCard__dottedUnderline--3jH_p")
        if not tag or (tag[0].text == "더 보기"):
            tag = self.bs.select("#taplc_location_detail_contact_card_ar_responsive_0 > div.contactInfo > div.contact > div.contactType.phone.is-hidden-mobile > div") 
            if not tag:
                return -1
        else: 
            tag_more_clcik = self.chrome_instance.find_element_by_css_selector("span.attractions-contact-card-ContactCard__dottedUnderline--3jH_p")
            self.chrome_instance.execute_script("arguments[0].click();", tag_more_clcik) # 클릭
            self.refreshInstance()
            tag = self.bs.select("a.attractions-contact-card-ContactCard__link--2pCqu")

        return str(tag[0].text)


    def scrapCategory(self):
        category = list()
        category_count = 0
        more_category_count = 0

        self.refreshInstance()

        #체킹용도
        #태그타입 1,2 더보기
        css_more_view = self.bs.select("#taplc_resp_attraction_header_ar_responsive_0 > div > div.ui_column.is-12-tablet.is-10-mobile.attractionsHeader > div > span > div > span.viewMore > a")
        location = "#taplc_resp_attraction_header_ar_responsive_0 > div > div.ui_column.is-12-tablet.is-10-mobile.attractionsHeader > div > span > div > span.viewMore > a"
        if not css_more_view:
            #태그타입 3의 더보기
            css_more_view = self.bs.select("div.attractions-supplier-profile-SupplierCategories__headerDetail--2Fk4B > span:nth-child(2) > a")
            location = "div.attractions-supplier-profile-SupplierCategories__headerDetail--2Fk4B > span:nth-child(2) > a"

        #더보기 있으면 클릭
        if not css_more_view:
            #더보기 없는경우 pass
           pass
        else:
            css_more_view = self.chrome_instance.find_element_by_css_selector(location)
            self.chrome_instance.execute_script("arguments[0].click();", css_more_view) # 클릭

            self.refreshInstance()

            tag_more_view = self.bs.select("#taplc_resp_attraction_header_ar_responsive_0 > div > div.ui_column.is-12-tablet.is-10-mobile.attractionsHeader > div > span > div >span")
            if not tag_more_view:
                tag_more_view = self.bs.select("#component_8 > div > div.attractions-company-profile-CompanyProfileContainer__infoSection--3uSuN > div.attractions-supplier-profile-SupplierProfile__profile--1oRu9.hasAvatar > div.attractions-supplier-profile-SupplierCategories__headerDetail--2Fk4B > span > a")
                if not tag_more_view:
                    return -1

            more_category_count = len(tag_more_view) #더보기 라는 글자까지 가져와져서..

            for i in range(0, more_category_count):
                if tag_more_view[i].text == ' 더 보기' or tag_more_view[i].text == '더 보기':
                    continue
                category.append(tag_more_view[i].text) 

            return category

        #더보기 안누른 상태에서 카테고리 가져오기
        #태그구조1
        tag = self.bs.select("#taplc_resp_attraction_header_ar_responsive_0 > div > div.ui_column.is-12-tablet.is-10-mobile.attractionsHeader > div > span > div >a")
        if not tag:
            #태그구조3 중 더보기 없는것
            tag = self.bs.select("#component_8 > div > div.attractions-company-profile-CompanyProfileContainer__infoSection--3uSuN > div.attractions-supplier-profile-SupplierProfile__profile--1oRu9.hasAvatar > div.attractions-supplier-profile-SupplierCategories__headerDetail--2Fk4B > span > a")
            if not tag:
                return -1

        category_count = len(tag) 

        for i in range(0, category_count):
            category.append(tag[i].text)

        return category



    def scrapTime(self):
        self.refreshInstance()

        #영업시간 유무를 아이콘으로 검색
        clock_icon = self.bs.select(".ui_icon.clock")
        if not clock_icon :
            clock_icon = 0
        else:
            clock_icon = 1

        #추천시간 유무를 아이콘으로 검색
        duration_icon = self.bs.select(".ui_icon.duration")
        if not duration_icon:
            duration_icon = 0
        else:
            duration_icon = 1

        #setting 
        if(clock_icon==1 and duration_icon ==1):
            opening_hours = self.scrapOpeningHours(1)
            recommend_time = self.scrapRecommendTime(2)
        elif(clock_icon==0 and duration_icon ==1):
            opening_hours = -1
            recommend_time = self.scrapRecommendTime(1)
        elif(clock_icon==1 and duration_icon ==0):
            opening_hours = self.scrapOpeningHours(1)
            recommend_time = -1
        elif(clock_icon==0 and duration_icon ==0):
            opening_hours = -1
            recommend_time = -1

        return opening_hours,recommend_time



    def scrapRecommendTime(self,check_num):
        recommend_time = str()#추천시간

        if check_num == 2 :
            #태그구조 1의 영업시간이 있는경우
            tag = self.bs.select("#taplc_location_detail_about_card_0 > div > div >  div:nth-child(3) > div")

            if not tag :
                #태그구조 2
                tag = self.bs.select("span.shopping-poi-description-ShoppingPoiDescription__content--1pw0j")
                if not tag :
                    return -1
                

        elif check_num == 1:
            #태그구조 1의 영업시간이 없는경우
            tag = self.bs.select("#taplc_location_detail_about_card_0 > div > div >  div:nth-child(2) > div")

            if not tag :
                #태그구조 2
                tag = self.bs.select("span.shopping-poi-description-ShoppingPoiDescription__content--1pw0j")
                if not tag :
                    return -1

        recommend_time = tag[-1].text[10:]
        return recommend_time


    def scrapOpeningHours(self,check_num):
        self.refreshInstance()

        opening_hours = list() #영업시간

        #모든시간대 확인 버튼 클릭 / 없는 경우 없으므로 다른 예외처리 x
        for e_count in range(1, self.EXCEPTION_COUNT):
            try :
                css_all_time_check = self.chrome_instance.find_element_by_css_selector("div.public-location-hours-LocationHours__hoursLink--2wAQh")
                self.chrome_instance.execute_script("arguments[0].click();", css_all_time_check) # 클릭
                break
            except NoSuchElementException:
                print("운영시간 스크랩 중 모든시간대 버튼 (NoSuchElementException)")
                return -1
            except StaleElementReferenceException:
                print("운영시간 스크랩 중 모든시간대 버튼 (StaleElementReferenceException)")
                self.refreshInstance(True)

        self.refreshInstance()

        #클릭 이후로는 경우 1,2,3 모두 같음
        tag = self.bs.select("div.all-open-hours>div")
        if not tag :
            return -1 

        #스크래핑
        for tag_detail in tag:
            hours = str("")
            tag_detail = tag_detail.select("div")
            hours = tag_detail[0].text+"/"+tag_detail[1].text
            opening_hours.append(hours)       

        return opening_hours




if __name__ == "__main__":

    scrap = ScrapingInfo()

    url_struct = scrap.loadPlayList()#url에 관한 정보들(리스트로 스크래핑 된 것..) csv파일로 읽어들여서 딕셔너리로 저장하는 과정

    for i in range(0, url_struct['list_len']):
        if int(url_struct['scrap_flag'][i]) == 0: #플래그가 0이면 긁어오기 1이면 작업 된 것임으로 긁어오지 x
            scrap.loadWebDriver(False, url_struct['urls'][i], "chromedriver")
            if scrap.startScraping() == -1:
                pass
            time.sleep(3)
            scrap.exitChromeDriver()
            print("스크랩 하나가 끝남.")
        else:
            print("%s -> already Scrapped"%(url_struct['titles'][i]))

    




