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



class Strapy:

    # Symbolic Constant
    EXCEPTION_COUNT = (5 + 1)
    EXCEPTION_SLEEP = 3

    # Chrome Driver Instance Variable
    chrome_instance = None
    chrome_middle_instance = None # Middle Instance

    # BeautifulSoup Global Variable
    html = None
    bs = None

    default_address = "https://www.tripadvisor.co.kr"

    def getInstance(self):
        return this.chrome_instance
        
    def getMiddleInstance(self):
        return this.chrome_middle_instance

    def __init__(self, headless = None, target_url = None, chrome_driver_path = None):

        if headless is None and target_url is None and chrome_driver_path is None:
            return
        else:
            options = Webd.ChromeOptions()
            options.add_argument('--start-maximized')  # Max Size Window
            
            if headless is True:
                options.add_argument('headless')
                options.add_argument('window-size=1920x1080')
                options.add_argument("disable-gpu") # or options.add_argument("--disable-gpu")
                
                self.chrome_instance = Webd.Chrome(chrome_driver_path, chrome_options=options) # Headless 
            else:
                self.chrome_instance = Webd.Chrome(chrome_driver_path, chrome_options=options) 

            self.chrome_instance.get(target_url) 

            self.chrome_instance.refresh()
            self.chrome_instance.implicitly_wait(10)
            time.sleep(5)

    def loadWebDriver(self, headless, target_url, chrome_driver_path):
        
        options = Webd.ChromeOptions()
        options.add_argument('--start-maximized')  # Max Size Window
        
        if headless is True:
            options.add_argument('headless')
            options.add_argument('window-size=1920x1080')
            options.add_argument("disable-gpu") # or options.add_argument("--disable-gpu")
            
            self.chrome_instance = Webd.Chrome(chrome_driver_path, chrome_options=options) # Headless 
        else:
            self.chrome_instance = Webd.Chrome(chrome_driver_path, chrome_options=options) 

        self.chrome_instance.get(target_url) 

        self.chrome_instance.refresh()
        self.chrome_instance.implicitly_wait(5)
        time.sleep(5)

    def refreshInstance(self, page_refresh = False): #새로고침의 효과가 있음. 
        if page_refresh is True: #크롬브라우저가 아예 새로고침, false 면 브라우저 새로고침은 아니지만 beautifulsoup에서 가지고 오는 태그(요소)들이 한 번 더 갱신함. 
            self.chrome_instance.refresh()
            self.chrome_instance.implicitly_wait(5)
            time.sleep(5)
            
        self.html = self.chrome_instance.page_source 
        self.bs = BeautifulSoup(self.html, 'html.parser')

        return
    
    def getStringToNumber(self, number_string): 
        #  1,394 -> 1394 
        numbers = re.findall("\d+", number_string) # 1,394 = 1 / 394

        numbers_string = ''
        numbers_len = len(numbers)

        if numbers_len == 0:
            return 0

        for i in range(0, numbers_len):
            numbers_string += numbers[i] # Concatenate String

        return int(numbers_string)

    def convertListToString(self, _list):
        _string = ''
        for element in _list:
            _string += (str)(element)
        return _string
    
    def extractRatingInString(self, _str, _reg = 'bubble_\d+'):
        reg = re.compile(_reg)
        reg_result = (str)((reg.findall(_str))[0])
        rating = (float)((re.findall("\d+",reg_result))[0]) * 0.1
        return rating

    def showElementTagsInLists(self, pre_text, tags):
        for tag in tags:
            print("{} : {}".format(pre_text,tag))

    def showElementTextsInLists(self, pre_text, tags):
        for text in tags:
            print("{} : {}".format(pre_text,text.text))

    def returnElementTextsInLists(self, tags):
        value = str('')
        for text in tags:
            value += text.text
        value = value.replace('\n',' ')
        return value

    def saveToCSV(self, local_title, page_number): # Override
        return None

    def startScraping(self): 
        return None

    def scrapContents(self):
        return None
    
    def exitChromeDriver(self):
        self.chrome_instance.quit()

    def log(self, log_msg):
        now = time.localtime() # 날짜 및 시간 얻어오기
        title_string = "./log_%04d%02d%02d.txt"%(now.tm_year, now.tm_mon, now.tm_mday)
        log_string = "[%04d-%02d-%02d %02d:%02d:%02d] : %s\n" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec, log_msg)
    
        with open(title_string,"a") as f:
            f.write(log_string)

        return
