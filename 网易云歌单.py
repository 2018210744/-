from selenium import webdriver
import csv
import random
import os

#读取文件 若文件不存在则新建文件 同时写入表头
if os.path.exists('playList.csv'):
    csvFile = open('playList.csv', 'a+', newline='', encoding="utf-8")
    writer = csv.writer(csvFile)
else:
    csvFile = open('playList.csv', 'a+', newline='', encoding="utf-8")
    writer = csv.writer(csvFile)
    writer.writerow(['标题', '播放数', '链接'])

#配置PhantomJS，提纲爬取速度
service_args=[]
service_args.append('--load-images=no')  ##关闭图片加载
service_args.append('--disk-cache=yes')  ##开启缓存
service_args.append('--ignore-ssl-errors=true') ##忽略https错误

playUrl = 'https://music.163.com/#/user/home?id=1320157310'
runCnt = 0                      #程序运行次数计数
cPlayerList = []                #url列表 当当前url不合适时，从内部随机取出一个继续爬取
while runCnt < 10000:            #爬取两千条记录
    driver = webdriver.PhantomJS("D:\Python\Python37\Scripts\phantomjs.exe", service_args=service_args)
    print(playUrl)              #打印当前爬取的url
    driver.get(playUrl)         #获取链接
    try:                        #在网页中若出现错误及时捕获
        #-----------------读取用户自建歌单-------------------
        driver.switch_to.frame('contentFrame')
        data = driver.find_element_by_id('cBox').find_elements_by_tag_name('li')
        for i in range(len(data)):
            nb = data[i].find_element_by_class_name('nb').text
            msk = data[i].find_element_by_css_selector('a.msk')
            writer.writerow([msk.get_attribute('title'),
                            nb, msk.get_attribute('href')])
            runCnt += 1
            print('runCnt:', runCnt)

        #-----------------读取用户收藏歌单-------------------
        data = driver.find_element_by_id('sBox').find_elements_by_tag_name('li')
        for i in range(len(data)):
            nb = data[i].find_element_by_class_name('nb').text
            nb.replace(u'\xa0', u' ');
            msk = data[i].find_element_by_css_selector('a.msk')
            #UnicodeEncodeError: 'gbk' codec can't encode character '\xa0' in position 2: illegal multibyte sequence
            #csvFile = open('playList.csv', 'w', newline='', encoding="utf-8")
            writer.writerow([msk.get_attribute('title'),
                            nb, msk.get_attribute('href')])
            runCnt += 1
            print('runCnt:', runCnt)
            cPlayerList.append(msk.get_attribute('href'))

        #从url列表中随机读取一个作为下一爬取的url
        randIndex = int(random.uniform(0, len(cPlayerList)))
        playUrl = cPlayerList[randIndex]
        del cPlayerList[randIndex]      #列表中取走后需要在列表中将该url删除
        #转到的页面是歌单的详细页面，以下代码负责读取该页面中的作者页面，跳转到作者页面以便继续爬取
        driver.get(playUrl)
        driver.switch_to.frame('contentFrame')
        data = driver.find_element_by_id('m-playlist').find_element_by_class_name('cntc').find_element_by_class_name('name')
        playUrl = data.find_element_by_css_selector('a.s-fc7').get_attribute('href')
    except:
        #若出现错误，从url列表中继续取出一个url
        randIndex = int(random.uniform(0, len(cPlayerList)))
        playUrl = cPlayerList[randIndex]
        del cPlayerList[randIndex]
        print('页面发生异常，取出一个备用url，当前url剩余：', len(cPlayerList))
        driver.get(playUrl)
        driver.switch_to.frame('contentFrame')
        data = driver.find_element_by_id('m-playlist').find_element_by_class_name('cntc').find_element_by_class_name(
            'name')
        playUrl = data.find_element_by_css_selector('a.s-fc7').get_attribute('href')