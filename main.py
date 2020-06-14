from selenium import webdriver
from bs4 import BeautifulSoup
from urllib import parse
import time
from words import words

class WantedCrawler():
  def __init__(self, keyword, words, driver_path):
    self.WANTED_DOMAIN = "https://www.wanted.co.kr"
    self.keyword = keyword
    self.words = words
    self.word_map = {}
    for word in self.words:
      self.word_map[word] = 0

    self.run_driver(driver_path)

  def run_driver(self, driver_path):    
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu") # 가속 사용 x
    options.add_argument("lang=ko_KR")
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')  # user-agent 이름 설정

    self.driver = webdriver.Chrome(driver_path, chrome_options=options)

  def getURI(self, path):
    return "{}{}".format(self.WANTED_DOMAIN, path)
  
  def start(self):
    self.driver.get(self.getURI("/search?query={}".format(parse.quote_plus(keyword))))
    print("페이지 로드 대기중...")
    self.driver.implicitly_wait(6)
    self.infiniti_scroll()
    hirePostHrefs = self.getHirePostHrefs()
    for hirePostHref in hirePostHrefs:
      self.checkHirePost(hirePostHref)
    self.report()
    self.close()

  def infiniti_scroll(self):
    while True:
      prev_scroll_height = self.driver.execute_script("return document.body.scrollHeight")
      print("스크롤다운")
      self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
      print("스크롤후 데이터를 기다리는중입니다.")
      time.sleep(2.5)
      next_scroll_height = self.driver.execute_script("return document.body.scrollHeight")
      print("이전스크롤: {}\n현재스크롤: {}".format(prev_scroll_height, next_scroll_height))
      if prev_scroll_height == next_scroll_height:
        print("스크롤이 더이상 존재하지 않습니다.")
        print("대기후 스크롤 종료")
        time.sleep(2.5)
        break

  def getHirePostHrefs(self):
    self.driver.find_element_by_css_selector(".clearfix:nth-child(2) a")
    html = self.driver.page_source
    bs = BeautifulSoup(html, 'html.parser')
    links = bs.select(".clearfix:nth-child(2) a")

    hirePostHrefs = [link.get('href') for link in links]
    return hirePostHrefs

  def checkHirePost(self, href):
    print("대기후 페이지를 이동합니다. {}".format(href))
    time.sleep(5)
    self.driver.get(self.getURI(href))
    self.driver.implicitly_wait(3)
    html = self.driver.page_source
    bs = BeautifulSoup(html, 'html.parser')
    post = bs.select('#__next > div > div:nth-child(3) > div > div > div')[0]
    post_text = post.text.lower()

    for word in self.words:
      if word in post_text:
        self.counting(word)

  def counting(self, word):
    self.word_map[word] += 1

  def report(self):
    print("리포팅 작업중...")
    report = ''
    for key, value in self.word_map.items():
      report += '{} : {}\n'.format(key, value)

    f = open('report.txt', 'w', encoding='utf-8')
    f.write(report)
    f.close()
    print("리포팅 작업완료")

    
  def close(self):
    print("종료합니다.")
    self.driver.quit()

keyword = input("검색 키워드를 입력해주세요 >>> ")
wantedCrawler = WantedCrawler(keyword, words, "./chromedriver.exe")
wantedCrawler.start()