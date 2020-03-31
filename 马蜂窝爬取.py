"""
马蜂窝游记数据爬取
苏州：https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10207.html #### http://www.mafengwo.cn/yj/10207/2-0-1.html
auther:xiaohei
Q:2585258690
"""

import requests
import re
import jsonpath
import urllib
import os
from bs4 import BeautifulSoup
import execjs
import time
import random

base = 'http://www.mafengwo.cn'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
           }

cookie = ''

num = 1


def geturl(page): #从初始页面获取全部的次一级游记链接

    nextlink = []

    for page in range(1,int(page)):

        url = base + '/yj/10207/2-0-{}.html'.format(page)

        res = requests.get(url, headers=headers)

        soup = BeautifulSoup(res.text, 'html.parser')

        titlelinks = soup.find_all('li', class_='post-item clearfix')

        for titlelink in titlelinks:

            next = base + titlelink.find('a', class_='title-link').get('href') + '@' + titlelink.find('span',class_='comment-date').text

            print(next)

            nextlink.append(next)

        print(page)
    #print(nextlink)
    return nextlink


def get_521(url, user_agent, proxies):#这步是获取浏览器返回的cookie值
    headers = {'User-Agent': user_agent}
    res = requests.get(url, timeout=10, headers=headers, proxies=proxies)
    #print(res.status_code)
    __jsluid_h = res.cookies

    #print(__jsluid_h)

    #print(res.text)

    __jsluid_h = str(__jsluid_h).split('Cookie ')[1].split(' for')[0]

    txt = ''.join(re.findall('<script>(.*?)</script>', res.text))

    if txt:

        __jsl_clearance = fixed_fun(txt, url)

        return (__jsluid_h, __jsl_clearance)


def fixed_fun(js_con, url):
    func_return = js_con.replace('eval(', 'return(')

    content = execjs.compile(func_return)

    fn = js_con.split('=')[0].split(' ')[1]

    evaled_func = content.call(fn)

    fn = evaled_func.split('=')[0].split(' ')[1]  # 获取动态函数名

    aa = evaled_func.split("<a href=\\'/\\'>")  # 获取<a>标签的内容

    aa = aa[1].split("</a>")[0] if len(aa) >= 2 else ' '

    mode_func = evaled_func. \
        replace(
        "setTimeout('location.href=location.pathname+location.search.replace(/[\\?|&]captcha-challenge/,\\'\\')',1500);document.cookie=",
        'return').\
        replace(';if((function(){try{return !!window.addEventListener;}', ''). \
        replace(
        "}catch(e){return false;}})()){document.addEventListener('DOMContentLoaded'," + fn + ",false)}else{document.attachEvent('onreadystatechange'," + fn + ")",
        ''). \
        replace(
        "if((function(){try{return !!window.addEventListener;}catch(e){return false;}})()){document.addEventListener('DOMContentLoaded'," + fn + ",false)}else{document.attachEvent('onreadystatechange'," + fn + ")",
        ''). \
        replace("return'__jsl_clearance", "var window={};return '__jsl_clearance"). \
        replace(
        "var " + fn + "=document.createElement('div');" + fn + ".innerHTML='<a href=\\'/\\'>" + aa + "</a>';" + fn + "=" + fn + ".firstChild.href",
        "var " + fn + "='" + url + "'")

    try:
        content = execjs.compile(mode_func)

        cookies = content.call(fn)

        __jsl_clearance = cookies.split(';')[0]

        return __jsl_clearance
    except:

        return  None


def downloadtxt(title, wtime, time, all_txt):#文字存储
    path = str(title)
    if not os.path.exists(path):
        os.mkdir(path)
        print('创建成功')
    else:
        # print("已经存在")
        pass
    try:
        with open(path + '\\' + title + '.txt', 'a') as ff:
            ff.write(str(wtime) + '\n' + '\n')
            ff.write(str(time)+'\n'+'\n')
            ff.write(all_txt.encode("gbk", 'ignore').decode("gbk", "ignore"))
    except:
        print ('存储失败')


def downloadimg(title, imglinks):#图片储存

    path = str(title)

    for imglink in imglinks:

        id = imglink.split(',')[1]

        link = imglink.split(',')[0]

        try:
            with open(path + '\\' + str(id) + '.jpg', 'wb') as ff:

                pic = requests.get(link)

                ff.write(pic.content)
                #print('第{}张下载完成'.format(id))
        except:

            print("该页无法下载")


def download(link):
    global num
    try:
        url = link.split('@')[0]

        wtime = link.split('@')[1]

        ip_list = [
                   '39.137.95.74:80',
                   '39.137.69.7:8080',
                   '221.180.170.104:8080'
                   ]

        user_agents = [
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
            "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
            'Opera/9.25 (Windows NT 5.1; U; en)',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
            'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
            'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
            'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
            "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
            "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0']

        ip = random.choice(ip_list)

        proxies = {

            'http': 'http://' + ip,

            'https': 'https://' + ip,

        }

        user_agent = random.choice(user_agents)

        global cookie

        headers = {'User-Agent': user_agent,
                    'Cookie': cookie}

        response = requests.get(url, headers=headers, proxies=proxies).status_code
        # print('1')
        # print(response)
        while(response == 403 or response == 521):
            ip = random.choice(ip_list)

            proxies = {

                'http': 'http://' + ip,

                'https': 'https://' + ip,

            }

            user_agent = random.choice(user_agents)

            cookies = get_521(url, user_agent, proxies)

            if (cookies[1] != None):

                cookie = cookies[0] + ';' + cookies[1]

                #print(cookie)
                headers_new = {
                    'User-Agent': user_agent,
                    'Cookie': cookie}
            else:

                headers_new = {
                    'User-Agent': user_agent}

            response = requests.get(url, headers=headers_new, proxies=proxies).status_code

        res_new = requests.get(url, headers=headers_new, proxies=proxies)
        #print('4')
        #print(res_new.status_code)

        soup = BeautifulSoup(res_new.text, 'html.parser')

        try:
            title = soup.find('h1', 'headtext lh80')

        except:
            title = None

        if(title != None):

            title = title.text

            title = title.replace(' ', '').replace('\n', '')

            try:
                time = soup.find('div', class_='tarvel_dir_list clearfix').text

                time = time.replace(' ', '')

            except:

                time = "无时间信息"
            #print(time)

            try:
                txts = soup.find_all('p', class_='_j_note_content _j_seqitem')

                all_txt = '本篇游记内容：'

                for txt in txts:

                    all_txt = all_txt + txt.text

                all_txt = all_txt.replace(' ', '').replace('\n', '')
            except:

                all_txt = '这篇游记没文字'

            downloadtxt(title, wtime, time, all_txt)

            imglinks = []

            try:
                imgurls = soup.find_all('div', class_='add_pic _j_anchorcnt _j_seqitem')

                for imgurl in imgurls:

                    imglink = imgurl.find('a').find('img').get('data-rt-src')

                    id = imgurl.find('a').find('img').get('data-pid')

                    imglinks.append(imglink + ',' + id)

                # print(imglinks)
                downloadimg(title, imglinks)

            except:
                print ('此页无图片')

        else:

            try:

                title = soup.find('div','post_title clearfix').text

                title = title.replace(' ', '').replace('\n', '')

            except:

                title = None

            time = '无时间信息'

            if(title != None):

                try:

                    txts = soup.find_all('p', class_='_j_note_content')

                    all_txt = '本篇游记内容：'

                    for txt in txts:

                        all_txt = all_txt + txt.text

                    all_txt = all_txt.replace(' ', '').replace('\n', '')

                except:

                    all_txt = '这篇游记没文字'

                downloadtxt(title, wtime, time, all_txt)

                imglinks = []

                try:

                    div = soup.find('div', class_='a_con_text cont')

                    imgurls = div.find_all('p')

                    for imgurl in imgurls:

                        if(imgurl.find('img')!=None):

                            imglink = imgurl.find('img').get('data-src')

                            id = imgurl.find('img').get('data-pid')

                            imglinks.append(imglink + ',' + id)

                except:

                    print ('此页无图片')
                # # print(imglinks)
                downloadimg(title, imglinks)

        print(title + '完成')

    except:
        print('************不知道报啥错了***************第{}个无法爬取的网址'.format(num))
        num = num + 1

def main():
    page = input('请输入页数:')

    urls = geturl(page)

    urls = list(reversed(urls))

    print('第一步爬取链接完成')

    for url in urls:

        download(url)

    print('全部完成')



if __name__=='__main__':

    stime=time.time()

    main()

    etime=time.time()

    print('消耗时间:{}s'.format(etime-stime))
