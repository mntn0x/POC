# -*- coding: utf-8 -*-
# env: python2
import threading
import requests
import time
from bs4 import BeautifulSoup
from optparse import OptionParser
from page_404 import page_404
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 默认扫描字典和默认header头
dict = [
    '/.git/config',
    '/.svn/entries',
    '/.hg',
    '/.bzr',
    '/.DS_Store',
    '/robots.txt',
    '/env',
    '/jolokia',
    '/actuator/jolokia',
    '/CVS/Entries',
    '/install.php',
    '/www.zip',
    '/www.rar',
    '/www.7z',
    '/1.zip',
    '/phpinfo.php',
    '/manager/html',
    '/jmx-console',
    '/web-console',
    '/WEB-INF/database.properties',
    '/WEB-INF/web.xml',
    '/WEB-INF/src/'
]
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'close'
}
# 结果列表
results = []

def backup(host, dict=dict, header=header, timeout=5):
    if host[:4] != "http":
        host = "http://"+host
    if host[-1] == "/":
        host = host[:-1]

    check_404 = page_404(host)

    for item in dict:
        url = host+item
        try:
            flag, response = check_404.is_404(url)
            if not flag:
                # 返回为False, None，说明是page404中request报错，在page404中已输出报错原因，此处不再处理
                if response == None:
                    continue
                # 返回200，并且返回url和请求url一致，同时返回值不为空(在page404中已判断)，这种情况最有可能是真正的备份文件泄露，以绿色输出
                if response.status_code == 200 and url == response.url:
                    print("\033[32m[200] %s\033[0m" % url)
                    # 因为最后要将结果写入文件，以返回码开头，在写入文件前先使用sort排序，返回码可以帮助分类，而且正好200是我们最想看的放在最前面
                    results.append("[200] "+url)
                # 返回30x，以青色输出跳转前后url
                elif response.status_code > 300 and response.status_code < 400:
                    print("\033[36m[%d] %s\033[0m -> %s" % (response.status_code, url, response.url))
                # 返回40x，以蓝色输出
                elif response.status_code > 400 and response.status_code < 404:
                    print("\033[34m[%d] %s\033[0m" % (response.status_code, url))
                # 返回40x，以蓝色输出
                elif response.status_code > 500 and response.status_code < 600:
                    print("\033[35m[%d] %s\033[0m" % (response.status_code, url))
            else:
                print("[404] %s" % url)
        except requests.exceptions.ConnectTimeout:
            print("[Timeout] " + url)
        except requests.exceptions.ConnectionError:
            print("[Connect Error] "  + url)
        # 重定向次数过多，忽略该错误，直接进入下一次循环
        except requests.exceptions.TooManyRedirects:
            continue
        except Exception as e:
            print("\033[31m%s => %s\033[0m" % (e, url))

'''
先将所有url读出来放入列表，为每个url添加线程
然后循环线程列表，启动每一个线程，启动一个线程后，判断当前运行的线程数是否超过了命令指定的线程
如果没有超过，则跳出while循环，继续for循环，开启下一个线程
如果等于了指定线程数，说明线程已满，进入while循环，轮询判断，直到有线程空出来，就跳出while循环，开启下一个线程
'''
def run_thread(file, thread_num, module=backup):
    thread_list = []
    f_list = open(file, "r")
    for line in f_list.readlines():
        t = threading.Thread(target=module, args=(line.strip(),))
        thread_list.append(t)
    for i in range(0, len(thread_list)):
        thread_list[i].start()
        while True:
            if len(threading.enumerate()) <= thread_num:
                break
    # 判断最后启动的n个线程是否结束，没结束的话，加上join，确保所有子线程结束之后再进入主线程的写文件操作
    for j in range(len(thread_list)-thread_num, len(thread_list)):
        if thread_list[j].isAlive():
            thread_list[j].join()

def output(file, results):
    print("\033[35m[INFO] 扫描完成，写入结果中...\033[0m")
    # 以返回状态码排序，将最有可能的200放在最前，非常nice
    results.sort()
    f_w = open(file, 'w', encoding='utf-8')
    for i in results:
        f_w.write(i+"\n")
    f_w.close()

# 自定义扫描模块——title获取
def title(host):
    # 处理url，怎么处理看扫描需求，注意url和字典的拼接
    if host[:4] != "http":
        host = "http://"+host
    url = host
    # 处理扫描请求和结果
    try:
        req = requests.get(url, headers=header, timeout=5)
        soup = BeautifulSoup(req.text, 'lxml')
        title = "None"
        if "title" in soup.prettify():
            title = soup.title.string
            print("\033[32m[%s] %s\033[0m" % (title, url))
        else:
            print("\033[32m[None] %s\033[0m" % url)
        results.append(title+" "+url)

    except requests.exceptions.ConnectTimeout:
        print("[Timeout] " + url)
    except requests.exceptions.ConnectionError:
        print("[Connect Error] " + url)
    except Exception as e:
        print("\033[31m%s => %s\033[0m" % (e, url))

if __name__ == '__main__':
    usage = r'''
      _                      _                              ____
     | |__     __ _    ___  | | __  _   _   _ __           / ___|    ___    __ _   _ __
     | '_ \   / _` |  / __| | |/ / | | | | | '_ \   _____  \___ \   / __|  / _` | | '_ \
     | |_) | | (_| | | (__  |   <  | |_| | | |_) | |_____|  ___) | | (__  | (_| | | | | |
     |_.__/   \__,_|  \___| |_|\_\  \__,_| | .__/          |____/   \___|  \__,_| |_| |_|
                                           |_|
    '''
    parser = OptionParser(usage)  # 带参的话会把参数变量的内容作为帮助信息输出
    parser.add_option('-u', '--url', dest='target_Url', type='string', help='single url')
    parser.add_option('-L', '--list', dest='Url_List', type='string', help='url list file')
    parser.add_option('-t', dest='thread', type='int', default=5, help='thread number')
    parser.add_option('-o', dest='outfile', type='string', default='results.txt', help='output file')
    # parser.add_option('--timeout', dest='timeout', type=int, default=5, help='timeout count')
    parser.add_option('--title', action="store_true", dest='title', default=False, help='Get domain\'s title')
    (options, args) = parser.parse_args()

    # 给输入参数赋值
    host = options.target_Url
    uList = options.Url_List
    thread = options.thread
    outFile = options.outfile
    # timeout = options.timeout
    titleGet = options.title


    if titleGet==False:
        if uList != None:
            run_thread(uList, thread)
            # 判断线程全部执行完再执行写入文件，记得线程数减去主线程
            while True:
                if len(threading.enumerate()) == 1:
                    output(outFile, results)
                    break
                else:
                    print("\033[35m[INFO] 还有%d个线程未结束...\033[0m" % (len(threading.enumerate())-1))
                    time.sleep(3)

        if host != None:
            backup(host)
            # 就这么几个备份文件，终端输出不多，不必写到文件里去了
            # output(outFile, results)
    elif titleGet==True:
        if uList != None:
            run_thread(uList, thread, title)
            # 判断线程全部执行完再执行写入文件，记得线程数减去主线程
            while True:
                if len(threading.enumerate()) == 1:
                    output('results-domains.txt', results)
                    break
                else:
                    print("\033[35m[INFO] 还有%d个线程未结束...\033[0m" % (len(threading.enumerate()) - 1))
                    time.sleep(3)
        if host != None:
            title(host)
    else:
        print(usage)
