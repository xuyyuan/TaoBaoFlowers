import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from pyquery import PyQuery as pq
from config import *
import pymongo

from selenium.webdriver.chrome.options import Options

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

chrome_options = Options()
chrome_options.add_argument('--headless')
prefs = {
    'profile.default._content_setting_values':{
        'images': 2
    }
}
chrome_options.add_experimental_option('prefs', prefs)
browser = webdriver.Chrome(chrome_options=chrome_options)
wait = WebDriverWait(browser, 10)

def search():
    try:
        browser.get('http://www.taobao.com')
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#q')))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        input.send_keys(KEYWORD)
        submit.click()
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        get_products()   # attention !
        return total.text  # 注意total.text的写法
    except TimeoutError:
        search()

def next_page(page_num):
    try:
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input.clear()
        input.send_keys(page_num)
        submit.click()
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_num)))
        get_products()  # attention ！
    except TimeoutError:
        next_page(page_num)

def save_to_mongodb(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储到mongodb成功', result)
    except Exception: # Exception
        print('存储到mongodb失败', result)

def get_products():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image':item.find('.pic .img').attr['src'],  # attr
            'price':item.find('.price').text().split('\n')[0] +  item.find('.price').text().split('\n')[1],
            'deal':item.find('.deal-cnt').text()[:-3], #.text()
            'title':item.find('.title').text(),
            'shop':item.find('.shop').text(),
            'location':item.find('.location').text()
        }
        if product:
            save_to_mongodb(product)

def main():
    try:
        total = search()
        total = int(re.compile(r'(\d+)').search(total).group(1)) # int()别忘了！
        for i in range(2, total+1):
            next_page(i)
    except Exception: # 直接捕捉父类的异常
        print('出错啦！')
    finally:
        browser.close()

if __name__ == '__main__':
    main()
