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

class ScrapingList(Strapy):


    list_title = str('') #  리스트의 타이틀 의미 ex) "방콕의 즐길거리"
    list_endpage_number = int(0) # 리스트의 끝 페이지 번호

    name_list = list() # 리스트에서의 각각 이름들을 담는 리스트
    url_list = list() # 리스트에서의 각각 주소들을 담는 리스트
    review_count_list = list() # 리스트에서의 각각 리뷰 개수를 담는 리스트

    #초기화
    def __init__(self, headless = None, target_url = None, chrome_driver_path = None):
        super().__init__(headless, target_url, chrome_driver_path) 
        return None


    def startScraping(self): # scraping을 시작하는 함수
        
        #국가/지역 별로 url을 list 화
        self.loadWebDriver(False, "https://www.tripadvisor.co.kr/Attractions-g13792389-Activities-Alishan_Chiayi_County.html", "./chromedriver.exe")
        self.refreshInstance()

        #필터링 해제 -> 모든 리스트가 보이도록 함
        self.deleteCheck()

        self.list_title = self.scrapTitle() # 타이틀 받아오기.
        self.list_endpage_number = self.scrapEndPageNumber() # 페이지 끝 번호 파악.
        print("[%s]의 (%d) 리스트 확인!"%(self.list_title, self.list_endpage_number))
        
        # 리스트의 내용을 받아오는 작업이 시작됨.
        self.scrapContents() # 내용 받아오기

        return

    def deleteCheck(self):
        css_delete_check = self.chrome_instance.find_element_by_css_selector("#ATTRACTION_FILTER > div > div > div> div")

        if(css_delete_check is None): #필터링 체크 안되어있다면 별도의 action 없음
            return 0
        else:
            self.chrome_instance.execute_script("arguments[0].click();", css_delete_check) # 클릭
        return 0
 
    def saveToCSV(self, local_title, page_number):
        ex = pd.DataFrame()

        ex['title'] = self.name_list
        ex['count'] = self.review_count_list
        ex['url'] = self.url_list
        ex['scrap_flag'] = 0

        if (page_number - 1) == 1:
            ex.to_csv('excite_urls_{}.csv'.format(local_title), index=False, encoding = 'utf-8')
        elif page_number == 1 :
            ex.to_csv('excite_urls_{}.csv'.format(local_title), index=False, encoding = 'utf-8')
        else:
            ex.to_csv('excite_urls_{}.csv'.format(local_title), mode='a', header=False, index=False ,encoding = 'utf-8')
    
    
    # 리스트의 제목 받아오기
    def scrapTitle(self): 
        html = self.chrome_instance.page_source 

        bs = BeautifulSoup(html, 'html.parser')
        titles = bs.select('li.breadcrumb')
        titles = titles[-1].text
        
        # 자동으로 calender 팝업이 뜸 >> 없애줘야한다.
        # Calender 제거를 위해 제목 태그를 클릭.
        for e_count in range(1, self.EXCEPTION_COUNT):
            try:
                css_delete_calender = self.chrome_instance.find_element_by_css_selector("#ATTRACTION_FILTER > div > div > div> div")
                self.chrome_instance.execute_script("arguments[0].click();", css_delete_calender) # 클릭
                break
            except NoSuchElementException:
                print("[Exception] : (#HEADING) 요소에 대한 NoSuchElementException 발생")
            except StaleElementReferenceException:
                print("[Exception] : (#HEADING) 요소에 대한 StaleElementReferenceException 발생")
                self.chrome_instance.refresh()
                self.chrome_instance.implicitly_wait(self.EXCEPTION_SLEEP)
        time.sleep(3)
        return titles
    
    #페이지네이션의 마지막 페이지 넘버 가져오기
    def scrapEndPageNumber(self):
        html = self.chrome_instance.page_source

        bs = BeautifulSoup(html, 'html.parser')
        end_page_tags = bs.select('#FILTERED_LIST > div.al_border.deckTools.btm > div > div > div> a') # title에 해당하는 태그를 받아옴.

        return (int)(end_page_tags[-1].text)

    #스크래핑 시작 함수
    def scrapContents(self):
        html = self.chrome_instance.page_source
        bs = BeautifulSoup(html, 'html.parser')


        now_page_tag = bs.select_one('#FILTERED_LIST > div.al_border.deckTools.btm > div > div > div > span.pageNum.current')
        now_page_number = (int)(now_page_tag.text)
        prev_page_number = -1 

        while now_page_number <= self.list_endpage_number:
            disposable_loop_var = True # 그저 한 번만 반복문을 돌게 하기 위함.
            
            while disposable_loop_var is True:
                disposable_loop_var = False

                print("[Scraping] : 현재 스크래핑 중인 페이지는 [%d] 입니다."%(now_page_number))

                if now_page_number == prev_page_number: # 다음 버튼을 눌렀지만 같은 페이지가 로딩 되었을 경우임 -> 다음을 다시 눌러야 함.
                    print("[Exception] : [%d] 페이지가 중복으로 열렸습니다."%(now_page_number))
                    break
                elif now_page_number != prev_page_number and now_page_number == 1: # 다음 버튼을 눌렀으나 같은 페이지가 아니지만 1페이지인 경우 -> 이 때는 저장할 것이 없으므로 pass
                    pass
                else: # 다음 버튼이 정상적으로 눌렀을 경우 -> 이 때 저장한다!
                    self.saveToCSV(self.list_title,now_page_number) # 저장 함수 호출

                    del self.name_list[:] 
                    del self.url_list[:]
                    del self.review_count_list[:]

                page_box_tags = bs.select("div.attraction_clarity_cell > div > div.listing_details")

                l_len = len(page_box_tags)
                for i in range (0, l_len):
                    review_tag = page_box_tags[i].select_one("div.listing_info > div.listing_rating > div.wrap>div.rs>span.more>a")
                    title_tag = page_box_tags[i].select_one("div.listing_info > div.listing_title>a")
                    title_text = title_tag.text
                    title_text = title_text.strip("\n")

                    self.name_list.append(title_text)
                    self.url_list.append(self.default_address + title_tag.get('href'))
                    if review_tag is None:
                        self.review_count_list.append(0)
                    else:
                        self.review_count_list.append(self.getStringToNumber(review_tag.text))
        

                    
                    print("[{}] : {} / {} / {} ".format(i+1,self.name_list[-1], self.url_list[-1], self.review_count_list[-1]))


            if now_page_number < self.list_endpage_number:
                # 다음버튼 누르기
                for e_count in range(1, self.EXCEPTION_COUNT):
                    try:
                        css_next_button = self.chrome_instance.find_element_by_css_selector("div > div > div > a.nav.next.taLnk.ui_button.primary") 
                        self.chrome_instance.execute_script("arguments[0].click();", css_next_button)
                        break
                    except NoSuchElementException:
                        print("[Exception] : (#HEADING) 요소에 대한 NoSuchElementException 발생")
                    except StaleElementReferenceException:
                        print("[Exception] : (#HEADING) 요소에 대한 StaleElementReferenceException 발생")
                        self.chrome_instance.refresh()
                        self.chrome_instance.implicitly_wait(self.EXCEPTION_SLEEP)
   
                self.chrome_instance.implicitly_wait(5)
                time.sleep(4)

                html = self.chrome_instance.page_source
                bs = BeautifulSoup(html, 'html.parser')


                now_page_tag = bs.select_one('#FILTERED_LIST > div.al_border.deckTools.btm > div > div > div > span.pageNum.current')
                prev_page_number = now_page_number
                now_page_number = (int)(now_page_tag.text)

            elif now_page_number == self.list_endpage_number:
                self.saveToCSV(self.list_title,now_page_number) # 저장 함수 호출
                break

        print("[Scraping] : 스크래핑이 완료 되었습니다.")
        return
 

if __name__ == "__main__":

    scrap = ScrapingList()
    scrap.startScraping()
    time.sleep(5)
    scrap.exitChromeDriver()
    





