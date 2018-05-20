# coding=utf-8
# author: xuyyuan time: 2018/4/13

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from pyquery import PyQuery as pq

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)

def search():
    try:
        browser.fget('http://www.taobao.com')
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#q")))  # element不是all_elements，要注意两者的区别;until也不要写成untill
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_TSearchForm > div.search-button > button")))
        input.send_keys('鲜花')
        submit.click()
        total = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        get_products()
        return total.text
    except TimeoutError:
        return search()

def next_page(page_num):
    try:
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input")))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit")))
        input.clear()
        input.send_keys(page_num)
        submit.click()
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > ul > li.item.active > span"), str(page_num)))
        get_products()
        # 上面的一句要注意text_to_be_present_in _element...... li.item.active > span"), str(page_num)
    except TimeoutError:
        next_page(page_num)

def get_products():
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.m-itemlist .items .item')))
    # 注意上面选择器里面的 item ，为什么class里面item后面的不要呢class = item J_MouserOnverReq item-ad
    html = browser.page_source
    doc = pq(html)
    items = doc('.m-itemlist .items .item').items()  # 注意items()方法的使用，巩固下
    for item in items:
        product = {
            'iamge':item.find('.pic .img').attr('src'),
            'price':item.find('.price').text(),
            'deal':item.find('.deal-cnt').text()[:-3],
            'shop':item.find('.shop').text()
            # 好好练习下选择器啊！！！还不是很熟！！！
        }
        print(product)

def main():
    total = search()
    total = int(re.compile(r'(\d+)').search(total).group(1))
    for i in range(2, total+1):
        next_page(i)

if __name__ == '__main__':
    main()

#TODO  接下来准备使用mongodb存储数据，以及使用无头模式和禁止加载图片的操作