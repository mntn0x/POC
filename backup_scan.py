# -*- coding: utf-8 -*-
import threading
import requests
import time
from optparse import OptionParser
requests.packages.urllib3.disable_warnings()

# 默认扫描字典和默认header头
dict = [
    '/.git/config',
    '/.svn/entries',
    '/www.zip',
    '/www.rar',
    '/www.7z',
    '/1.zip',
    '/phpinfo.php',
    '/manager/html',
    '/jmx-console',
    '/web-console'
]
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}
# 结果列表
results = []

def backup(host, dict=dict, header=header):
    if host[:4] != "http":
        host = "http://"+host
    for item in dict:
        url = host+item
        try:
            response = requests.get(url, headers=header, verify=False, timeout=3)
            # 先划分最简单的404，然后细分
            if response.status_code != 404:
                # 返回200，并且返回url和请求url一致，同时返回值不为空，这种情况最有可能是真正的备份文件泄露，以绿色输出
                if response.status_code==200 and url==response.url and response.text!="":
                    print("\033[32m[200] %s\033[0m" % url)
                    # 因为最后要将结果写入文件，以返回码开头，在写入文件前先使用sort排序，返回码可以帮助分类，而且正好200是我们最想看的放在最前面
                    results.append("[200] "+url)
                elif response.status_code!=200:
                    # 如果url == response.url，就只写url，简化写入结果方便阅读
                    if url!=response.url:
                        print("\033[36m[%d] %s\033[0m  ->  %s" % (response.status_code, url, response.url))
                        results.append("[%d] %s  ->  %s" % (response.status_code, url, response.url))
                    else:
                        print("\033[36m[%d] %s\033[0m" % (response.status_code, url))
                        results.append("[%d] %s" % (response.status_code, url))
            else:
                print("[404] %s" % url)
        except requests.exceptions.ConnectTimeout:
            print("[Timeout] " + url)
        except requests.exceptions.ConnectionError:
            print("[Error] "  + url)
        except:
            print("\033[31m[Warning] don't known why connect false... %s\033[0m" % url)

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
    print("\033[35m[INFO]扫描完成，写入结果中...\033[0m")
    # 以返回状态码排序，将最有可能的200放在最前，非常nice
    results.sort()
    new = []
    i=0
    '''
    判断是否有domain每个测试项都存在，这种情况说明网站肯定是做了防护，要去除该domain的url
    因为每个测试项都出现，所以将测试项的数量(字典dict的长度)比作n，同时因为对结果字典进行了排序
    所以只需比较出现结果字典中domain出现的第1次和它接着的第n项值是否相同，就知道是否连续出现了n次该domain值
    由此判断domain是否每个测试项都存在
    '''
    # 先判断i+n是否超出字典长度，注意是len(dict)-1！因为是获取domain出现的第n次，第n次就是字典长度-1
    while i+len(dict)-1 < len(results):
        # 获取//和/的下标，切片得到URL里的domain值
        start = results[i].index('//')+2
        end = results[i][start:].index('/')+start
        # print(results[i][start:end])
        if results[i][start:end] == results[i+len(dict)-1][start:end]:
            # print("所有测试url都返回200，It's impossible!。" + results[i][start:end])
            # 注意是len(dict)，因为该if条件下判断出该domain是有防护的，需要去判断下一个domain，所以直接跳到下一个domain的下标
            i += len(dict)
        else:
            new.append(results[i])
            i += 1
    f_w = open(file, 'w')
    for i in new:
        f_w.write(i+"\n")
    f_w.close()

# 自定义扫描模块
def modulescan(host):
    # 处理url，怎么处理看扫描需求，注意url和字典的拼接
    if host[:4] != "http":
        host = "http://"+host
    url = host
    # 定义所需字典，可以是读文件，可以是直接写成列表放在函数里
    dict = [
    '/test'
    ]
    # 定义header头
    header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': host,
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    # 处理扫描请求和结果
    for item in dict:
        try:
            resp = requests.get(url, headers=header, verify=False, timeout=3)
        except Exception as e:
            raise
        else:
            pass
        finally:
            pass

if __name__ == '__main__':
    usage = r'''
      _                      _                              ____
     | |__     __ _    ___  | | __  _   _   _ __           / ___|    ___    __ _   _ __
     | '_ \   / _` |  / __| | |/ / | | | | | '_ \   _____  \___ \   / __|  / _` | | '_ \
     | |_) | | (_| | | (__  |   <  | |_| | | |_) | |_____|  ___) | | (__  | (_| | | | | |
     |_.__/   \__,_|  \___| |_|\_\  \__,_| | .__/          |____/   \___|  \__,_| |_| |_|
                                           |_|
     Usage: python3 backup_scan.py [-u|--url] target [-t]
     -u target URL, --url=http://wwww.xxx.com
     -L URL List File --list=domains.txt
     -t ThreadsCount
     -o Output File
     --module Custom module, need to modufy the code
    '''
    parser = OptionParser(usage)  # 带参的话会把参数变量的内容作为帮助信息输出
    parser.add_option('-u', '--url', dest='target_Url', type='string', help='single url')
    parser.add_option('-L', '--list', dest='Url_List', type='string', help='url list file')
    parser.add_option('-t', dest='thread', type='int', default=5, help='thread number')
    parser.add_option('-o', dest='outfile', type='string', default='results.txt', help='output file')
    parser.add_option('--module', dest='module', type='string', default='False',help='custom module')
    (options, args) = parser.parse_args()

    # 给输入参数赋值
    host = options.target_Url
    uList = options.Url_List
    thread = options.thread
    outFile = options.outfile
    module = options.module

    if module=='False':
        if uList != None:
            run_thread(uList, thread)
            # 判断线程全部执行完再执行写入文件，记得线程数减去主线程
            while True:
                if len(threading.enumerate()) == 1:
                    output(outFile, results)
                    break
                else:
                    print("\033[35m[INFO]还有%d个线程未结束...\033[0m" % (len(threading.enumerate())-1))
                    time.sleep(3)

        if host != None:
            backup(host)
            # 就这么几个备份文件，终端输出不多，不必写到文件里去了
            # output(outFile, results)
    elif module=='True':
        if uList != None:
            run_thread(uList, thread, modulescan)
        if host != None:
            module(host)
            if output != None:
                output(output, results)
    else:
        print(usage)
# 可扩充的module函数，其中可指定扫描的各种参数(URL、header、线程)，用于以后能快速的启动多线程扫描任务，只需专注于http包的构造即可
