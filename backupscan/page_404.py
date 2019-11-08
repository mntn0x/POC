# -*- encoding:utf-8 -*-
# 404 页面识别
from hashes.simhash import simhash
import requests
import random
import string
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class page_404:
    def __init__(self, domain):  # 检测站点
        # 设置Connection=close可以避免HTTPConnectionPool
        self.header={'Connection': 'close'}
        self._404_page = []  # 404页面
        self._404_url = []  # 404 url
        random_path = ''.join(random.sample(string.ascii_letters + string.digits, 8))+'.html'
        self._404_path = [random_path,
                          "test?action=modify&newsid=122%20and%201=2%20union%20select%201,2,admin%2bpassword,4,5,6,7%20from%20shopxp_admin"]  # 404页面路径，用于生成一部分404页面
        # 自己构造404url，以便收集一些404页面的信息
        for path in self._404_path:
            if domain[-1] == "/":
                url = domain + path
            else:
                url = domain + "/" + path
            try:
                response = requests.get(url, headers=self.header, verify=False, timeout=5)
                soup = BeautifulSoup(response.text, 'lxml')
                if "title" in soup.prettify():
                    title_text = soup.title.string
                else:
                    title_text = ""
                body_text = soup.find("body").get_text().replace("\n", "").replace("\r", "").replace("\t","").replace(" ", "")
                text = title_text + body_text
                self.kb_appent(text, url)
            except requests.exceptions.ConnectTimeout:
                print("[Timeout] " + url)
            except requests.exceptions.ConnectionError:
                print("[Connect Error] " + url)
            # 重定向次数过多，忽略该错误，直接进入下一次循环
            except requests.exceptions.TooManyRedirects:
                continue
            except Exception as e:
                print("\033[31m%s => %s\033[0m" % (e, url))

    def kb_appent(self, _404_page, _404_url):
        if _404_page not in self._404_page:
            self._404_page.append(_404_page)
        if _404_url not in self._404_url:
            self._404_url.append(_404_url)

    def is_similar_page(self, page1, page2):
        hash1 = simhash(page1)
        hash2 = simhash(page2)
        similar = hash1.similarity(hash2)
        if similar > 0.85:  # 当前阈值定义为0.85
            return True
        else:
            return False

    def is_404(self, url):
        if url in self._404_url:
            return True, None
        try:
            response = requests.get(url, headers=self.header, verify=False, timeout=5)
            # 状态码为404，直接判断
            if response.status_code == 404:
                return True, None
            # 页面大小为0，直接判断
            if len(response.text) == 0:
                return True, None
            # 如果是200页面，根据阈值判断。其他状态码30x，40x，50x都返回到主函数进行输出
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                # 因为可能不存在title，所以需要先判断
                if "title" in soup.prettify():
                    title_text = soup.title.string
                else:
                    title_text = ""
                body_text = soup.find("body").get_text().replace("\n", "").replace("\r", "").replace("\t", "").replace(
                    " ", "")
                text = title_text + body_text

                for page in self._404_page:
                    if self.is_similar_page(text, page):
                        self.kb_appent(text, url)  # 如果是404页面，则保存当前的url和页面信息
                        return True, response
                    else:
                        return False, response
            else:
                return False, response
        # 报错，则无法访问，直接认为是404
        except requests.exceptions.ConnectTimeout:
            print("[Timeout] " + url)
            return False, None
        except requests.exceptions.ConnectionError:
            print("[Connect Error] " + url)
            return False, None
        # 重定向次数过多，忽略该错误，直接进入下一次循环
        except requests.exceptions.TooManyRedirects:
            print("[Redirect too more]" + url)
            return False, None
        except Exception as e:
            print("\033[31m%s => %s\033[0m" % (e, url))
            return False, None
